"""
mbtcp.py - Implementazione MINIMA e DIDATTICA di Modbus TCP (solo libreria standard).

Non usare in produzione: lo scopo e' vedere ogni byte del protocollo.
In produzione si usano librerie mature (es. pymodbus, libmodbus, j2mod...).

Struttura di un frame Modbus TCP (ADU):

    +----------------+----------------+----------------+----------+-----------------------+
    | Transaction ID | Protocol ID    | Length         | Unit ID  | PDU                   |
    | 2 byte         | 2 byte (=0)    | 2 byte         | 1 byte   | Function code + dati  |
    +----------------+----------------+----------------+----------+-----------------------+
    |<------------------ MBAP header (7 byte) ------------------->|

    Length = numero di byte che seguono (Unit ID + PDU).
    Tutti i campi multi-byte sono BIG-ENDIAN (byte piu' significativo prima).
"""

import socket
import struct
import threading

# Function code usati nel laboratorio
FC_READ_HOLDING = 0x03
FC_READ_INPUT = 0x04
FC_WRITE_SINGLE = 0x06
FC_WRITE_MULTIPLE = 0x10

FUNCTION_NAMES = {
    0x01: "Read Coils",
    0x02: "Read Discrete Inputs",
    0x03: "Read Holding Registers",
    0x04: "Read Input Registers",
    0x05: "Write Single Coil",
    0x06: "Write Single Register",
    0x0F: "Write Multiple Coils",
    0x10: "Write Multiple Registers",
    0x2B: "Encapsulated Interface (Read Device Identification)",
}

EXCEPTION_NAMES = {
    0x01: "ILLEGAL FUNCTION",
    0x02: "ILLEGAL DATA ADDRESS",
    0x03: "ILLEGAL DATA VALUE",
    0x04: "SERVER DEVICE FAILURE",
    0x05: "ACKNOWLEDGE",
    0x06: "SERVER DEVICE BUSY",
    0x0A: "GATEWAY PATH UNAVAILABLE",
    0x0B: "GATEWAY TARGET DEVICE FAILED TO RESPOND",
}

MAX_READ_REGISTERS = 125   # limite del protocollo per FC03/FC04 (PDU max 253 byte)
MAX_WRITE_REGISTERS = 123  # limite del protocollo per FC16


class ModbusException(Exception):
    """Il server ha risposto con un'eccezione Modbus (function code | 0x80)."""

    def __init__(self, function, code):
        self.function = function
        self.code = code
        super().__init__(
            f"Eccezione Modbus 0x{code:02X} ({EXCEPTION_NAMES.get(code, '?')}) "
            f"sulla funzione 0x{function:02X}"
        )


def hexdump(data):
    return " ".join(f"{b:02X}" for b in data)


def build_adu(transaction_id, unit_id, pdu):
    """Antepone l'header MBAP alla PDU."""
    return struct.pack(">HHHB", transaction_id, 0, len(pdu) + 1, unit_id) + pdu


def recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("connessione chiusa dal peer")
        buf += chunk
    return buf


def read_adu(sock):
    """Legge un frame completo dal socket. Restituisce (tid, unit, pdu, raw)."""
    header = recv_exact(sock, 7)
    tid, pid, length, unit = struct.unpack(">HHHB", header)
    if pid != 0:
        raise ValueError(f"Protocol ID inatteso: {pid} (Modbus usa sempre 0)")
    if not 2 <= length <= 254:
        raise ValueError(f"Campo Length non valido: {length}")
    pdu = recv_exact(sock, length - 1)
    return tid, unit, pdu, header + pdu


def explain_adu(raw, direction=""):
    """Restituisce una spiegazione leggibile, campo per campo, di un frame Modbus TCP."""
    tid, pid, length, unit = struct.unpack(">HHHB", raw[:7])
    pdu = raw[7:]
    fc = pdu[0]
    lines = [
        f"{direction} {hexdump(raw)}",
        f"    MBAP: TransactionID={tid}  ProtocolID={pid}  Length={length}  UnitID={unit}",
    ]
    if fc & 0x80:
        lines.append(
            f"    PDU : ECCEZIONE su FC 0x{fc & 0x7F:02X} -> codice 0x{pdu[1]:02X} "
            f"({EXCEPTION_NAMES.get(pdu[1], '?')})"
        )
        return "\n".join(lines)

    name = FUNCTION_NAMES.get(fc, "sconosciuta")
    body = pdu[1:]
    detail = ""
    if fc in (FC_READ_HOLDING, FC_READ_INPUT):
        if len(body) == 4:  # richiesta
            addr, count = struct.unpack(">HH", body)
            detail = f"indirizzo={addr}  quantita'={count} registri"
        else:  # risposta
            nbytes = body[0]
            regs = struct.unpack(f">{nbytes // 2}H", body[1:1 + nbytes])
            preview = ", ".join(str(r) for r in regs[:8]) + (" ..." if len(regs) > 8 else "")
            detail = f"byte count={nbytes}  registri=[{preview}]"
    elif fc == FC_WRITE_SINGLE:
        addr, value = struct.unpack(">HH", body)
        detail = f"indirizzo={addr}  valore={value}"
    elif fc == FC_WRITE_MULTIPLE:
        addr, count = struct.unpack(">HH", body[:4])
        detail = f"indirizzo={addr}  quantita'={count}"
        if len(body) > 4:  # richiesta (contiene anche i dati)
            vals = struct.unpack(f">{count}H", body[5:5 + 2 * count])
            detail += f"  valori={list(vals)}"
    lines.append(f"    PDU : FC=0x{fc:02X} ({name})  {detail}")
    return "\n".join(lines)


class ModbusTcpClient:
    """Client (master) Modbus TCP minimale e sincrono."""

    def __init__(self, host, port=502, unit_id=1, timeout=3.0, trace=False):
        self.host, self.port, self.unit_id = host, port, unit_id
        self.timeout, self.trace = timeout, trace
        self._sock = None
        self._tid = 0
        self._lock = threading.Lock()

    def connect(self):
        self._sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        return self

    def close(self):
        if self._sock:
            self._sock.close()
            self._sock = None

    def __enter__(self):
        return self if self._sock else self.connect()

    def __exit__(self, *exc):
        self.close()

    def _transact(self, pdu):
        with self._lock:
            self._tid = (self._tid + 1) & 0xFFFF
            request = build_adu(self._tid, self.unit_id, pdu)
            if self.trace:
                print(explain_adu(request, "-->"))
            self._sock.sendall(request)
            tid, _unit, resp_pdu, raw = read_adu(self._sock)
            if self.trace:
                print(explain_adu(raw, "<--"))
            if tid != self._tid:
                raise ValueError(f"Transaction ID non corrispondente ({tid} != {self._tid})")
            if resp_pdu[0] & 0x80:
                raise ModbusException(resp_pdu[0] & 0x7F, resp_pdu[1])
            if resp_pdu[0] != pdu[0]:
                raise ValueError("Function code della risposta diverso dalla richiesta")
            return resp_pdu

    def read_holding_registers(self, address, count):
        """FC03: restituisce una lista di interi a 16 bit senza segno."""
        result = []
        # Le letture piu' lunghe di 125 registri vanno spezzate in piu' richieste
        while count > 0:
            n = min(count, MAX_READ_REGISTERS)
            pdu = struct.pack(">BHH", FC_READ_HOLDING, address, n)
            resp = self._transact(pdu)
            nbytes = resp[1]
            result.extend(struct.unpack(f">{nbytes // 2}H", resp[2:2 + nbytes]))
            address += n
            count -= n
        return result

    def write_single_register(self, address, value):
        """FC06: il server risponde con l'eco della richiesta."""
        self._transact(struct.pack(">BHH", FC_WRITE_SINGLE, address, value & 0xFFFF))

    def write_multiple_registers(self, address, values):
        """FC16 (0x10)."""
        values = [v & 0xFFFF for v in values]
        pdu = struct.pack(f">BHHB{len(values)}H", FC_WRITE_MULTIPLE, address,
                          len(values), 2 * len(values), *values)
        self._transact(pdu)
