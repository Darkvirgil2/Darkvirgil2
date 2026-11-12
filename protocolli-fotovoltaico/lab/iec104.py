#!/usr/bin/env python3
"""
iec104.py - Anatomia dei messaggi IEC 60870-5-104 (telecontrollo tra impianto e centro di controllo).

    python3 iec104.py                                    # costruisce e spiega una sessione tipica
    python3 iec104.py 68 04 07 00 00 00                  # decodifica un APDU dato in esadecimale

Differenze chiave rispetto a Modbus:
  * non c'e' polling continuo: l'impianto (stazione "controllata") invia i dati
    SPONTANEAMENTE quando cambiano, piu' un'interrogazione generale all'avvio;
  * ogni dato ha un indirizzo (IOA), un tipo, una qualita' e spesso un'etichetta temporale;
  * i messaggi sono numerati e confermati (numeri di sequenza N(S)/N(R)).

Struttura APDU:
    0x68 | lunghezza (1 byte) | 4 byte di controllo | [ASDU]
    ASDU = TypeID | VSQ | Causa di trasmissione (2) | Indirizzo comune (2) | IOA (3) | elemento
    Nota: in IEC 104 i campi multi-byte sono LITTLE-ENDIAN (al contrario di Modbus).
"""

import struct
import sys

START = 0x68

U_FUNCTIONS = {
    0x07: "STARTDT act (avvia trasferimento dati)",
    0x0B: "STARTDT con (conferma)",
    0x13: "STOPDT act",
    0x23: "STOPDT con",
    0x43: "TESTFR act (keep-alive)",
    0x83: "TESTFR con",
}

TYPE_IDS = {
    1: "M_SP_NA_1 - segnale singolo (es. interruttore aperto/chiuso)",
    3: "M_DP_NA_1 - segnale doppio",
    13: "M_ME_NC_1 - misura in virgola mobile",
    30: "M_SP_TB_1 - segnale singolo con tempo CP56Time2a",
    36: "M_ME_TF_1 - misura float con tempo CP56Time2a",
    45: "C_SC_NA_1 - comando singolo",
    50: "C_SE_NC_1 - setpoint in virgola mobile",
    100: "C_IC_NA_1 - interrogazione generale",
    103: "C_CS_NA_1 - sincronizzazione orologio",
}

CAUSES = {
    1: "periodica", 3: "spontanea", 5: "richiesta", 6: "attivazione",
    7: "conferma di attivazione", 10: "terminazione attivazione",
    20: "risposta a interrogazione generale", 44: "TypeID sconosciuto",
    47: "IOA sconosciuto",
}


def apdu(control, asdu=b""):
    return bytes([START, len(control) + len(asdu)]) + control + asdu


def u_frame(function):
    return apdu(bytes([function, 0, 0, 0]))


def s_frame(nr):
    return apdu(struct.pack("<HH", 0x0001, nr << 1))


def i_frame(ns, nr, asdu):
    return apdu(struct.pack("<HH", ns << 1, nr << 1), asdu)


def asdu_header(type_id, cause, common_addr, n_objects=1, originator=0, negative=False, test=False):
    vsq = n_objects & 0x7F
    cot = cause | (0x40 if negative else 0) | (0x80 if test else 0)
    return struct.pack("<BBBBH", type_id, vsq, cot, originator, common_addr)


def ioa(address):
    return struct.pack("<I", address)[:3]


def float_measure(common_addr, address, value, cause=3, quality=0):
    """M_ME_NC_1: misura float IEEE-754 + byte di qualita' (QDS)."""
    return asdu_header(13, cause, common_addr) + ioa(address) + struct.pack("<fB", value, quality)


def float_setpoint(common_addr, address, value, cause=6, select=False):
    """C_SE_NC_1: setpoint float + qualificatore (bit7 = select/execute)."""
    qos = 0x80 if select else 0x00
    return asdu_header(50, cause, common_addr) + ioa(address) + struct.pack("<fB", value, qos)


def quality_text(q):
    flags = [n for bit, n in ((0x01, "OV overflow"), (0x10, "BL bloccato"), (0x20, "SB sostituito"),
                              (0x40, "NT non aggiornato"), (0x80, "IV NON VALIDO")) if q & bit]
    return ", ".join(flags) if flags else "buona"


def decode(frame):
    lines = [" ".join(f"{b:02X}" for b in frame)]
    if frame[0] != START:
        return lines + ["  Byte iniziale diverso da 0x68: non e' un APDU IEC 104"]
    length = frame[1]
    c1, c2, c3, c4 = frame[2:6]
    lines.append(f"  APCI: start=0x68 lunghezza={length}")
    if c1 & 0x01 == 0:
        ns = (c1 >> 1) | (c2 << 7)
        nr = (c3 >> 1) | (c4 << 7)
        lines.append(f"  Formato I (dati numerati): N(S)={ns} N(R)={nr}")
    elif c1 & 0x03 == 0x01:
        nr = (c3 >> 1) | (c4 << 7)
        lines.append(f"  Formato S (solo conferma): N(R)={nr} -> ricevuti i messaggi fino a N(S)={nr - 1}, "
                     f"il prossimo atteso e' {nr}")
        return lines
    else:
        lines.append(f"  Formato U: {U_FUNCTIONS.get(c1, hex(c1))}")
        return lines

    asdu = frame[6:]
    type_id, vsq, cot, orig, ca = struct.unpack("<BBBBH", asdu[:6])
    cause = cot & 0x3F
    lines.append(f"  ASDU: TypeID={type_id} ({TYPE_IDS.get(type_id, '?')})")
    lines.append(f"        oggetti={vsq & 0x7F} sequenza={'si' if vsq & 0x80 else 'no'}")
    lines.append(f"        causa={cause} ({CAUSES.get(cause, '?')})"
                 f"{' NEGATIVA' if cot & 0x40 else ''}{' TEST' if cot & 0x80 else ''}"
                 f"  originatore={orig}  indirizzo comune (stazione)={ca}")
    address = int.from_bytes(asdu[6:9], "little")
    element = asdu[9:]
    if type_id == 13:
        value, q = struct.unpack("<fB", element[:5])
        lines.append(f"        IOA={address}  valore={value:.3f}  qualita'={quality_text(q)}")
    elif type_id == 50:
        value, qos = struct.unpack("<fB", element[:5])
        lines.append(f"        IOA={address}  setpoint={value:.3f}  {'SELECT' if qos & 0x80 else 'EXECUTE'}")
    elif type_id == 1:
        siq = element[0]
        lines.append(f"        IOA={address}  stato={'ON' if siq & 1 else 'OFF'}  qualita'={quality_text(siq & 0xF0)}")
    elif type_id == 100:
        lines.append(f"        IOA={address}  QOI={element[0]} (20 = interrogazione di stazione)")
    else:
        lines.append(f"        IOA={address}  elemento={element.hex(' ')}")
    return lines


def demo():
    CA = 1   # indirizzo comune: identifica l'impianto
    session = [
        ("Centro di controllo -> Impianto: apro il flusso dati", u_frame(0x07)),
        ("Impianto -> Centro: confermo", u_frame(0x0B)),
        ("Centro -> Impianto: interrogazione generale (mandami tutto)",
         i_frame(0, 0, asdu_header(100, 6, CA) + ioa(0) + bytes([20]))),
        ("Impianto -> Centro: potenza attiva al punto di connessione = 4321.5 kW",
         i_frame(0, 1, float_measure(CA, 1001, 4321.5, cause=20))),
        ("Impianto -> Centro: interruttore generale CHIUSO",
         i_frame(1, 1, asdu_header(1, 20, CA) + ioa(2001) + bytes([0x01]))),
        ("Impianto -> Centro: fine dell'interrogazione generale",
         i_frame(2, 1, asdu_header(100, 10, CA) + ioa(0) + bytes([20]))),
        ("Centro -> Impianto: setpoint limite di potenza 3000 kW",
         i_frame(1, 3, float_setpoint(CA, 5001, 3000.0))),
        ("Impianto -> Centro: conferma di attivazione del setpoint",
         i_frame(3, 2, float_setpoint(CA, 5001, 3000.0, cause=7))),
        ("Impianto -> Centro: la potenza e' scesa (invio SPONTANEO, nessuno l'ha chiesto)",
         i_frame(4, 2, float_measure(CA, 1001, 2998.7, cause=3))),
        ("Centro -> Impianto: confermo di aver ricevuto i tuoi messaggi 0..4", s_frame(5)),
        ("Nessun traffico per un po': test del collegamento", u_frame(0x43)),
    ]
    for title, frame in session:
        print(f"\n# {title}")
        print("\n".join(decode(frame)))


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)   # permette "| head" senza errori
    if len(sys.argv) > 1:
        print("\n".join(decode(bytes(int(x, 16) for x in sys.argv[1:]))))
    else:
        demo()
