"""
sunspec.py - Definizioni (parziali) dei modelli SunSpec e funzioni di decodifica.

SunSpec standardizza COSA c'e' nei registri Modbus di un inverter:
  * all'indirizzo base (di solito 40000) c'e' il marker "SunS" (0x5375 0x6E53)
  * seguono "modelli" in catena: [ID][L][L registri di dati] [ID][L][...] ... [0xFFFF][0]
  * ogni grandezza e' un intero; il valore reale = intero * 10^SF (scale factor)

Qui sono definiti solo i modelli usati nel laboratorio:
  1   = Common (identificativo del dispositivo)
  103 = Inverter trifase (variante "integer + scale factor")
  123 = Immediate Controls (comandi: limitazione di potenza, cos(phi), connessione)
I modelli completi sono pubblicati da SunSpec Alliance (https://sunspec.org).
"""

import struct

SUNSPEC_MARKER = (0x5375, 0x6E53)        # "SunS" in ASCII
SUNSPEC_BASE_ADDRESSES = (40000, 0, 50000)
END_MODEL_ID = 0xFFFF

# Valori che indicano "non implementato" per ciascun tipo
NOT_IMPLEMENTED = {
    "uint16": 0xFFFF,
    "enum16": 0xFFFF,
    "int16": 0x8000,
    "sunssf": 0x8000,
    "acc32": 0,          # per gli accumulatori 0 significa "non implementato"
    "bitfield32": 0xFFFFFFFF,
}

# Ogni punto: (nome, tipo, numero registri, nome scale factor o None, unita', descrizione)
MODEL_1 = [
    ("Mn", "string", 16, None, "", "Produttore"),
    ("Md", "string", 16, None, "", "Modello"),
    ("Opt", "string", 8, None, "", "Opzioni"),
    ("Vr", "string", 8, None, "", "Versione firmware"),
    ("SN", "string", 16, None, "", "Numero di serie"),
    ("DA", "uint16", 1, None, "", "Indirizzo del dispositivo"),
    ("Pad", "pad", 1, None, "", "Riempimento"),
]

MODEL_103 = [
    ("A", "uint16", 1, "A_SF", "A", "Corrente AC totale"),
    ("AphA", "uint16", 1, "A_SF", "A", "Corrente fase A"),
    ("AphB", "uint16", 1, "A_SF", "A", "Corrente fase B"),
    ("AphC", "uint16", 1, "A_SF", "A", "Corrente fase C"),
    ("A_SF", "sunssf", 1, None, "", ""),
    ("PPVphAB", "uint16", 1, "V_SF", "V", "Tensione concatenata AB"),
    ("PPVphBC", "uint16", 1, "V_SF", "V", "Tensione concatenata BC"),
    ("PPVphCA", "uint16", 1, "V_SF", "V", "Tensione concatenata CA"),
    ("PhVphA", "uint16", 1, "V_SF", "V", "Tensione di fase AN"),
    ("PhVphB", "uint16", 1, "V_SF", "V", "Tensione di fase BN"),
    ("PhVphC", "uint16", 1, "V_SF", "V", "Tensione di fase CN"),
    ("V_SF", "sunssf", 1, None, "", ""),
    ("W", "int16", 1, "W_SF", "W", "Potenza attiva AC"),
    ("W_SF", "sunssf", 1, None, "", ""),
    ("Hz", "uint16", 1, "Hz_SF", "Hz", "Frequenza di rete"),
    ("Hz_SF", "sunssf", 1, None, "", ""),
    ("VA", "int16", 1, "VA_SF", "VA", "Potenza apparente"),
    ("VA_SF", "sunssf", 1, None, "", ""),
    ("VAr", "int16", 1, "VAr_SF", "var", "Potenza reattiva"),
    ("VAr_SF", "sunssf", 1, None, "", ""),
    ("PF", "int16", 1, "PF_SF", "%", "Fattore di potenza"),
    ("PF_SF", "sunssf", 1, None, "", ""),
    ("WH", "acc32", 2, "WH_SF", "Wh", "Energia prodotta (contatore)"),
    ("WH_SF", "sunssf", 1, None, "", ""),
    ("DCA", "uint16", 1, "DCA_SF", "A", "Corrente DC"),
    ("DCA_SF", "sunssf", 1, None, "", ""),
    ("DCV", "uint16", 1, "DCV_SF", "V", "Tensione DC"),
    ("DCV_SF", "sunssf", 1, None, "", ""),
    ("DCW", "int16", 1, "DCW_SF", "W", "Potenza DC"),
    ("DCW_SF", "sunssf", 1, None, "", ""),
    ("TmpCab", "int16", 1, "Tmp_SF", "C", "Temperatura interna"),
    ("TmpSnk", "int16", 1, "Tmp_SF", "C", "Temperatura dissipatore"),
    ("TmpTrns", "int16", 1, "Tmp_SF", "C", "Temperatura trasformatore"),
    ("TmpOt", "int16", 1, "Tmp_SF", "C", "Altra temperatura"),
    ("Tmp_SF", "sunssf", 1, None, "", ""),
    ("St", "enum16", 1, None, "", "Stato operativo"),
    ("StVnd", "enum16", 1, None, "", "Stato specifico del produttore"),
    ("Evt1", "bitfield32", 2, None, "", "Eventi/allarmi"),
    ("Evt2", "bitfield32", 2, None, "", "Riservato"),
    ("EvtVnd1", "bitfield32", 2, None, "", "Eventi del produttore 1"),
    ("EvtVnd2", "bitfield32", 2, None, "", "Eventi del produttore 2"),
    ("EvtVnd3", "bitfield32", 2, None, "", "Eventi del produttore 3"),
    ("EvtVnd4", "bitfield32", 2, None, "", "Eventi del produttore 4"),
]

MODEL_123 = [
    ("Conn_WinTms", "uint16", 1, None, "s", "Finestra temporale per il comando Conn"),
    ("Conn_RvrtTms", "uint16", 1, None, "s", "Timeout di ritorno per Conn"),
    ("Conn", "enum16", 1, None, "", "0=DISCONNETTI 1=CONNETTI"),
    ("WMaxLimPct", "uint16", 1, "WMaxLimPct_SF", "%", "Limite potenza attiva in % di WMax"),
    ("WMaxLimPct_WinTms", "uint16", 1, None, "s", "Finestra temporale"),
    ("WMaxLimPct_RvrtTms", "uint16", 1, None, "s", "Timeout: dopo N s il limite decade"),
    ("WMaxLimPct_RmpTms", "uint16", 1, None, "s", "Tempo di rampa"),
    ("WMaxLim_Ena", "enum16", 1, None, "", "0=limite DISABILITATO 1=ABILITATO"),
    ("OutPFSet", "int16", 1, "OutPFSet_SF", "", "cos(phi) impostato"),
    ("OutPFSet_WinTms", "uint16", 1, None, "s", ""),
    ("OutPFSet_RvrtTms", "uint16", 1, None, "s", ""),
    ("OutPFSet_RmpTms", "uint16", 1, None, "s", ""),
    ("OutPFSet_Ena", "enum16", 1, None, "", ""),
    ("VArWMaxPct", "int16", 1, "VArPct_SF", "%", ""),
    ("VArMaxPct", "int16", 1, "VArPct_SF", "%", ""),
    ("VArAvalPct", "int16", 1, "VArPct_SF", "%", ""),
    ("VArPct_WinTms", "uint16", 1, None, "s", ""),
    ("VArPct_RvrtTms", "uint16", 1, None, "s", ""),
    ("VArPct_RmpTms", "uint16", 1, None, "s", ""),
    ("VArPct_Mod", "enum16", 1, None, "", ""),
    ("VArPct_Ena", "enum16", 1, None, "", ""),
    ("WMaxLimPct_SF", "sunssf", 1, None, "", ""),
    ("OutPFSet_SF", "sunssf", 1, None, "", ""),
    ("VArPct_SF", "sunssf", 1, None, "", ""),
]

MODELS = {
    1: ("Common", MODEL_1),
    103: ("Inverter trifase", MODEL_103),
    123: ("Immediate Controls", MODEL_123),
}

INVERTER_STATES = {
    1: "OFF", 2: "SLEEPING (notte)", 3: "STARTING", 4: "MPPT (produzione)",
    5: "THROTTLED (limitato)", 6: "SHUTTING_DOWN", 7: "FAULT", 8: "STANDBY",
}


def model_length(points):
    return sum(p[2] for p in points)


def point_offsets(points):
    """Mappa nome -> offset (in registri) rispetto all'inizio dei dati del modello."""
    offsets, off = {}, 0
    for name, _t, size, *_ in points:
        offsets[name] = off
        off += size
    return offsets


def to_signed16(value):
    return value - 0x10000 if value & 0x8000 else value


def regs_to_string(regs):
    raw = b"".join(struct.pack(">H", r) for r in regs)
    return raw.split(b"\x00", 1)[0].decode("ascii", errors="replace").strip()


def string_to_regs(text, size):
    raw = text.encode("ascii")[: size * 2].ljust(size * 2, b"\x00")
    return list(struct.unpack(f">{size}H", raw))


def decode_raw(ptype, regs):
    """Interpreta i registri di un punto secondo il suo tipo SunSpec. None = non implementato."""
    if ptype == "string":
        return regs_to_string(regs)
    if ptype == "pad":
        return None
    if ptype in ("acc32", "bitfield32"):
        value = (regs[0] << 16) | regs[1]   # word order big-endian: prima la word alta
    else:
        value = regs[0]
    if NOT_IMPLEMENTED.get(ptype) == value:
        return None
    if ptype in ("int16", "sunssf"):
        value = to_signed16(value)
    return value


def decode_model(model_id, regs):
    """
    Decodifica i registri di dati di un modello (esclusi ID e L).
    Restituisce {nome: (valore_scalato, unita', descrizione, valore_grezzo)}.
    """
    _title, points = MODELS[model_id]
    raw = {}
    off = 0
    for name, ptype, size, _sf, _u, _d in points:
        raw[name] = decode_raw(ptype, regs[off:off + size])
        off += size

    out = {}
    for name, ptype, _size, sf_name, unit, desc in points:
        if ptype in ("sunssf", "pad"):
            continue
        value = raw[name]
        if value is not None and sf_name:
            sf = raw.get(sf_name)
            value = None if sf is None else round(value * 10 ** sf, max(0, -sf))
        out[name] = (value, unit, desc, raw[name])
    return out


def discover(client, base_addresses=SUNSPEC_BASE_ADDRESSES):
    """
    Cerca il marker SunS e percorre la catena dei modelli.
    Restituisce (base, [(model_id, indirizzo_inizio_dati, lunghezza), ...]).
    """
    for base in base_addresses:
        try:
            if tuple(client.read_holding_registers(base, 2)) != SUNSPEC_MARKER:
                continue
        except Exception:
            continue  # indirizzo non valido su questo dispositivo: prova il successivo
        models = []
        addr = base + 2
        while True:
            model_id, length = client.read_holding_registers(addr, 2)
            if model_id == END_MODEL_ID:
                break
            models.append((model_id, addr + 2, length))
            addr += 2 + length
        return base, models
    raise RuntimeError("Marker 'SunS' non trovato: il dispositivo non e' SunSpec "
                       "(o usa un indirizzo base diverso)")


def read_model(client, models, model_id):
    """Legge e decodifica un modello gia' scoperto con discover()."""
    for mid, start, length in models:
        if mid == model_id:
            return decode_model(model_id, client.read_holding_registers(start, length))
    raise KeyError(f"Modello {model_id} non presente nel dispositivo")


def model_address(models, model_id):
    for mid, start, _length in models:
        if mid == model_id:
            return start
    raise KeyError(f"Modello {model_id} non presente nel dispositivo")


def set_power_limit(client, models, percent, revert_s=0):
    """
    Imposta la limitazione di potenza attiva tramite il modello 123.
    percent=None disabilita il limite.
    revert_s>0: se il comando non viene rinnovato entro N secondi l'inverter torna libero
    (meccanismo di sicurezza tipico dei controllori d'impianto: "watchdog").
    """
    start = model_address(models, 123)
    off = point_offsets(MODEL_123)
    if percent is None:
        client.write_single_register(start + off["WMaxLim_Ena"], 0)
        return
    sf = to_signed16(client.read_holding_registers(start + off["WMaxLimPct_SF"], 1)[0])
    raw = round(percent / 10 ** sf)
    # Scrittura "atomica" dei registri contigui da WMaxLimPct a WMaxLim_Ena
    values = [raw, 0, revert_s, 0, 1]   # Pct, WinTms, RvrtTms, RmpTms, Ena
    client.write_multiple_registers(start + off["WMaxLimPct"], values)
