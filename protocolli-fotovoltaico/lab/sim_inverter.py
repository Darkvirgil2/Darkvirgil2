#!/usr/bin/env python3
"""
sim_inverter.py - Simulatore di inverter fotovoltaico trifase con interfaccia Modbus TCP / SunSpec.

Avvio:
    python3 sim_inverter.py                       # porta 5020, 20 kW, unit id 1
    python3 sim_inverter.py --port 5021 --wmax 50000 --trace

(Si usa la porta 5020 perche' la 502 standard richiede privilegi di amministratore.)

Mappa dei registri (indirizzi "di protocollo", partono da 0):
    40000-40001  "SunS"
    40002-40003  ID=1   L=66   -> 40004..40069  Common
    40070-40071  ID=103 L=50   -> 40072..40121  Inverter trifase
    40122-40123  ID=123 L=24   -> 40124..40147  Immediate Controls (scrivibile)
    40148-40149  ID=0xFFFF L=0 -> fine catena

La "giornata" solare e' compressa: per default dura 10 minuti, cosi' vedi i valori cambiare.
"""

import argparse
import math
import random
import socketserver
import struct
import threading
import time

import mbtcp
import sunspec

BASE = 40000


def choose_sf(max_abs, signed=True):
    """Sceglie lo scale factor piu' piccolo (>=0) tale che max_abs ci stia in un registro."""
    limit = 32767 if signed else 65534   # 65535/32768 sono riservati a "non implementato"
    sf = 0
    while max_abs / 10 ** sf > limit:
        sf += 1
    return sf


class SunSpecInverter:
    def __init__(self, unit_id=1, wmax=20000, day_seconds=600, serial="LAB0000001"):
        self.unit_id = unit_id
        self.wmax = wmax
        self.day_seconds = day_seconds
        self.lock = threading.Lock()
        self.t0 = time.monotonic()
        self.last_update = self.t0
        self.energy_wh = 1_234_567.0      # contatore di energia iniziale
        self.limit_written_at = None

        self.regs = [0] * 150
        self.addr = {}                     # nome punto -> indirizzo assoluto
        self.writable = set()

        self._set(BASE, list(sunspec.SUNSPEC_MARKER))
        addr = BASE + 2
        for model_id in (1, 103, 123):
            _title, points = sunspec.MODELS[model_id]
            length = sunspec.model_length(points)
            self._set(addr, [model_id, length])
            for name, off in sunspec.point_offsets(points).items():
                self.addr[f"{model_id}.{name}"] = addr + 2 + off
            addr += 2 + length
        self._set(addr, [sunspec.END_MODEL_ID, 0])

        # --- Modello 1: identificativo
        for name, text, size in (("Mn", "LabSolar", 16), ("Md", "SIM-INV-3P", 16),
                                 ("Opt", "", 8), ("Vr", "1.0.0", 8), ("SN", serial, 16)):
            self._set(self.addr[f"1.{name}"], sunspec.string_to_regs(text, size))
        self._put("1.DA", unit_id)
        self._put("1.Pad", 0x8000)

        # --- Modello 103: scale factor fissi (scelti in base alla taglia)
        self.w_sf = choose_sf(wmax * 1.1)
        for name, sf in (("A_SF", -2), ("V_SF", -1), ("W_SF", self.w_sf), ("Hz_SF", -2),
                         ("VA_SF", self.w_sf), ("VAr_SF", self.w_sf), ("PF_SF", -1),
                         ("WH_SF", 0), ("DCA_SF", -2), ("DCV_SF", -1), ("DCW_SF", self.w_sf),
                         ("Tmp_SF", -1)):
            self._put(f"103.{name}", sf & 0xFFFF)
        for name in ("TmpSnk", "TmpTrns", "TmpOt"):
            self._put(f"103.{name}", 0x8000)        # non implementati
        self._put("103.StVnd", 0xFFFF)
        for name in ("Evt2", "EvtVnd1", "EvtVnd2", "EvtVnd3", "EvtVnd4"):
            self._set(self.addr[f"103.{name}"], [0xFFFF, 0xFFFF])

        # --- Modello 123: valori iniziali, tutto il resto "non implementato"
        for name, ptype, *_ in sunspec.MODEL_123:
            self._put(f"123.{name}", sunspec.NOT_IMPLEMENTED.get(ptype, 0))
        for name, value in (("Conn_WinTms", 0), ("Conn_RvrtTms", 0), ("Conn", 1),
                            ("WMaxLimPct", 10000), ("WMaxLimPct_WinTms", 0),
                            ("WMaxLimPct_RvrtTms", 0), ("WMaxLimPct_RmpTms", 0),
                            ("WMaxLim_Ena", 0), ("WMaxLimPct_SF", (-2) & 0xFFFF)):
            self._put(f"123.{name}", value)
        for name in ("Conn_WinTms", "Conn_RvrtTms", "Conn", "WMaxLimPct", "WMaxLimPct_WinTms",
                     "WMaxLimPct_RvrtTms", "WMaxLimPct_RmpTms", "WMaxLim_Ena"):
            self.writable.add(self.addr[f"123.{name}"])

        self.update()

    # ---- accesso ai registri
    def _set(self, address, values):
        for i, v in enumerate(values):
            self.regs[address - BASE + i] = v & 0xFFFF

    def _put(self, point, value):
        self.regs[self.addr[point] - BASE] = value & 0xFFFF

    def _get(self, point):
        return self.regs[self.addr[point] - BASE]

    # ---- "fisica" semplificata dell'impianto
    def update(self):
        now = time.monotonic()
        dt = now - self.last_update
        self.last_update = now

        # Giornata compressa: fase 0..1; luce solare nel primo 60% della giornata.
        phase = ((now - self.t0) / self.day_seconds + 0.25) % 1.0
        sun = math.sin(math.pi * phase / 0.6) if phase < 0.6 else 0.0
        available = self.wmax * sun * random.uniform(0.95, 1.0)

        # Watchdog: se il comando di limitazione non viene rinnovato, decade.
        rvrt = self._get("123.WMaxLimPct_RvrtTms")
        if (self._get("123.WMaxLim_Ena") == 1 and rvrt not in (0, 0xFFFF)
                and self.limit_written_at is not None
                and now - self.limit_written_at > rvrt):
            self._put("123.WMaxLim_Ena", 0)

        limit_w = self.wmax
        if self._get("123.WMaxLim_Ena") == 1:
            pct = self._get("123.WMaxLimPct") * 10 ** sunspec.to_signed16(self._get("123.WMaxLimPct_SF"))
            limit_w = self.wmax * pct / 100

        connected = self._get("123.Conn") == 1
        power = min(available, limit_w) if connected else 0.0

        if not connected:
            state = 8                                   # STANDBY
        elif available < 50:
            state, power = 2, 0.0                       # SLEEPING
        elif limit_w < available:
            state = 5                                   # THROTTLED
        else:
            state = 4                                   # MPPT

        self.energy_wh += power * dt / 3600
        sfw = 10 ** self.w_sf
        v_phase = [random.gauss(230.0, 0.8) for _ in range(3)]
        i_phase = [power / 3 / v for v in v_phase]
        dcv = 620.0 + 60 * sun if power > 0 else 0.0
        dcw = power / 0.975 if power > 0 else 0.0

        self._put("103.A", round(sum(i_phase) * 100))
        for ph, i, v in zip("ABC", i_phase, v_phase):
            self._put(f"103.Aph{ph}", round(i * 100))
            self._put(f"103.PhVph{ph}", round(v * 10))
        for name, (va, vb) in (("PPVphAB", (0, 1)), ("PPVphBC", (1, 2)), ("PPVphCA", (2, 0))):
            self._put(f"103.{name}", round((v_phase[va] + v_phase[vb]) / 2 * math.sqrt(3) * 10))
        self._put("103.W", round(power / sfw))
        self._put("103.Hz", round(random.gauss(50.0, 0.01) * 100))
        self._put("103.VA", round(power / sfw))
        self._put("103.VAr", 0)
        self._put("103.PF", 1000)                            # 100.0 %
        wh = int(self.energy_wh)
        self._set(self.addr["103.WH"], [(wh >> 16) & 0xFFFF, wh & 0xFFFF])
        self._put("103.DCV", round(dcv * 10))
        self._put("103.DCA", round(dcw / dcv * 100) if dcv else 0)
        self._put("103.DCW", round(dcw / sfw))
        self._put("103.TmpCab", round((25 + 20 * power / self.wmax) * 10))
        self._put("103.St", state)
        self._set(self.addr["103.Evt1"], [0, 0])

    # ---- servizi Modbus
    def read(self, address, count):
        if address < BASE or address + count > BASE + len(self.regs):
            raise mbtcp.ModbusException(mbtcp.FC_READ_HOLDING, 0x02)
        self.update()
        return self.regs[address - BASE: address - BASE + count]

    def write(self, function, address, values):
        for a in range(address, address + len(values)):
            if a not in self.writable:
                raise mbtcp.ModbusException(function, 0x02)   # registro di sola lettura
        pct_addr = self.addr["123.WMaxLimPct"]
        if pct_addr in range(address, address + len(values)):
            if values[pct_addr - address] > 10000:            # > 100.00 %
                raise mbtcp.ModbusException(function, 0x03)
        self._set(address, values)
        self.limit_written_at = time.monotonic()
        self.update()

    def handle_pdu(self, pdu):
        fc = pdu[0]
        try:
            with self.lock:
                if fc in (mbtcp.FC_READ_HOLDING, mbtcp.FC_READ_INPUT):
                    address, count = struct.unpack(">HH", pdu[1:5])
                    if not 1 <= count <= mbtcp.MAX_READ_REGISTERS:
                        raise mbtcp.ModbusException(fc, 0x03)
                    values = self.read(address, count)
                    return struct.pack(f">BB{count}H", fc, 2 * count, *values)
                if fc == mbtcp.FC_WRITE_SINGLE:
                    address, value = struct.unpack(">HH", pdu[1:5])
                    self.write(fc, address, [value])
                    return pdu[:5]                                   # eco della richiesta
                if fc == mbtcp.FC_WRITE_MULTIPLE:
                    address, count, nbytes = struct.unpack(">HHB", pdu[1:6])
                    if not 1 <= count <= mbtcp.MAX_WRITE_REGISTERS or nbytes != 2 * count:
                        raise mbtcp.ModbusException(fc, 0x03)
                    values = list(struct.unpack(f">{count}H", pdu[6:6 + nbytes]))
                    self.write(fc, address, values)
                    return struct.pack(">BHH", fc, address, count)
                raise mbtcp.ModbusException(fc, 0x01)                # funzione non supportata
        except mbtcp.ModbusException as exc:
            return bytes([fc | 0x80, exc.code])


def make_server(inverter, host, port, trace=False):
    class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            if trace:
                print(f"[+] connessione da {self.client_address[0]}:{self.client_address[1]}")
            while True:
                try:
                    tid, unit, pdu, raw = mbtcp.read_adu(self.request)
                except (ConnectionError, OSError, ValueError):
                    break
                if trace:
                    print(mbtcp.explain_adu(raw, "<-- richiesta "))
                if unit not in (inverter.unit_id, 0xFF):
                    # Un dispositivo diretto spesso ignora l'Unit ID; un GATEWAY TCP->RTU
                    # lo usa per scegliere lo slave sul bus RS-485. Qui imitiamo un gateway.
                    resp_pdu = bytes([pdu[0] | 0x80, 0x0B])
                else:
                    resp_pdu = inverter.handle_pdu(pdu)
                response = mbtcp.build_adu(tid, unit, resp_pdu)
                if trace:
                    print(mbtcp.explain_adu(response, "--> risposta  "))
                self.request.sendall(response)

    class Server(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    return Server((host, port), Handler)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5020)
    p.add_argument("--unit", type=int, default=1, help="Unit ID Modbus (slave id)")
    p.add_argument("--wmax", type=int, default=20000, help="Potenza nominale in W")
    p.add_argument("--day-seconds", type=float, default=600, help="Durata della giornata simulata")
    p.add_argument("--serial", default="LAB0000001")
    p.add_argument("--trace", action="store_true", help="Stampa ogni frame ricevuto/inviato")
    args = p.parse_args()

    inverter = SunSpecInverter(args.unit, args.wmax, args.day_seconds, args.serial)
    server = make_server(inverter, args.host, args.port, args.trace)
    print(f"Inverter simulato {args.wmax/1000:g} kW in ascolto su {args.host}:{args.port} "
          f"(unit id {args.unit}). Ctrl+C per uscire.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
