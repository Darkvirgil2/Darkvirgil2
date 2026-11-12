#!/usr/bin/env python3
"""
modbus_rtu.py - Come e' fatto un frame Modbus RTU (seriale RS-485) e come lo traduce un gateway.

    python3 modbus_rtu.py                  # esempi
    python3 modbus_rtu.py 01 03 00 00 00 0A  # calcola il CRC di un frame qualsiasi

Frame RTU:
    +----------------+------------------------+----------------------+
    | Indirizzo slave| PDU (FC + dati)        | CRC-16 (2 byte)      |
    | 1 byte         | identica a Modbus TCP  | byte BASSO per primo |
    +----------------+------------------------+----------------------+
    I frame sono separati da almeno 3,5 "caratteri" di silenzio sulla linea.
"""

import struct
import sys


def crc16_modbus(data):
    """CRC-16/MODBUS: polinomio 0xA001 (0x8005 riflesso), valore iniziale 0xFFFF."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def build_rtu(slave, pdu):
    body = bytes([slave]) + pdu
    return body + struct.pack("<H", crc16_modbus(body))   # "<" = little-endian: low byte first


def check_rtu(frame):
    return crc16_modbus(frame[:-2]) == struct.unpack("<H", frame[-2:])[0]


def tcp_to_rtu(adu):
    """Cio' che fa un gateway Modbus TCP -> RTU: toglie l'MBAP, usa l'Unit ID come indirizzo slave."""
    unit = adu[6]
    return build_rtu(unit, adu[7:])


def silent_interval_ms(baud, bits_per_char=11):
    """
    Pausa di fine frame (3,5 caratteri). Un carattere RTU = 11 bit
    (start + 8 dati + parita' + stop, oppure 2 stop senza parita').
    Oltre 19200 baud la specifica fissa 1,75 ms.
    """
    if baud > 19200:
        return 1.75
    return 3.5 * bits_per_char / baud * 1000


def hx(b):
    return " ".join(f"{x:02X}" for x in b)


def main():
    if len(sys.argv) > 1:
        data = bytes(int(x, 16) for x in sys.argv[1:])
        crc = crc16_modbus(data)
        print(f"Frame : {hx(data)}\nCRC   : 0x{crc:04X} -> da trasmettere come {crc & 0xFF:02X} {crc >> 8:02X}")
        print(f"Totale: {hx(data + struct.pack('<H', crc))}")
        return

    print("1) Esempio classico: slave 1, FC03, leggi 10 registri dall'indirizzo 0")
    f = build_rtu(1, struct.pack(">BHH", 0x03, 0, 10))
    print(f"   {hx(f)}   (CRC valido: {check_rtu(f)})\n")

    print("2) La STESSA richiesta del laboratorio (modello 103 SunSpec) in TCP e in RTU")
    pdu = struct.pack(">BHH", 0x03, 40072, 50)
    adu = struct.pack(">HHHB", 7, 0, len(pdu) + 1, 1) + pdu
    print(f"   Modbus TCP: {hx(adu)}")
    print(f"               [MBAP: {hx(adu[:7])}] [PDU: {hx(adu[7:])}]")
    rtu = tcp_to_rtu(adu)
    print(f"   Modbus RTU: {hx(rtu)}")
    print(f"               [slave: {hx(rtu[:1])}] [PDU: {hx(rtu[1:-2])}] [CRC: {hx(rtu[-2:])}]\n")

    print("3) Un bit sbagliato sul cavo -> CRC non valido, lo slave scarta il frame in silenzio")
    corrupted = bytearray(rtu)
    corrupted[3] ^= 0x01
    print(f"   {hx(corrupted)}   (CRC valido: {check_rtu(bytes(corrupted))})\n")

    print("4) Tempo di silenzio tra frame (3,5 caratteri):")
    for baud in (9600, 19200, 38400, 115200):
        print(f"   {baud:>6} baud -> {silent_interval_ms(baud):.2f} ms")
    print("\n5) Quanto dura una lettura di 50 registri a 9600 baud?")
    req_chars, resp_chars = 8, 5 + 2 * 50   # richiesta 8 byte; risposta: slave+FC+count+dati+CRC
    t = (req_chars + resp_chars) * 11 / 9600 * 1000 + 2 * silent_interval_ms(9600)
    print(f"   ~{t:.0f} ms solo di trasmissione (senza il tempo di elaborazione dello slave).")
    print("   Con 30 inverter sullo stesso bus un giro completo di polling richiede ~"
          f"{30 * t / 1000:.1f} s: ecco perche' il dimensionamento del bus RS-485 conta.")


if __name__ == "__main__":
    main()
