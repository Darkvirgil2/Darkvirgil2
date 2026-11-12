"""Genera web/corso.html dalle lezioni Markdown. Uso: pip install markdown && python3 build.py"""
import json, pathlib, re, markdown

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent

REPL = {
    "02-modbus.md": [
        ("Prova: `python3 lab/modbus_rtu.py` (calcola CRC, tempi di bus, conversione TCP→RTU).",
         "Prova nel [laboratorio Modbus RTU](#lab-rtu): calcolo del CRC, tempi del bus, conversione TCP→RTU."),
        ("Prova: avvia `python3 lab/sim_inverter.py --trace` e in un altro terminale\n`python3 lab/client_sunspec.py --trace`: vedrai ogni byte in entrambe le direzioni.",
         "Prova nel [laboratorio Inverter](#lab-inverter): il registro dei frame mostra ogni byte in entrambe le direzioni."),
        ("Vedi il calcolo in `modbus_rtu.py`.", "Vedi il calcolo nel [laboratorio Modbus RTU](#lab-rtu)."),
    ],
    "03-sunspec.md": [
        ("È esattamente ciò che fa `sunspec.discover()` nel laboratorio.",
         "È esattamente ciò che fa il pulsante «Discovery» nel [laboratorio](#lab-inverter)."),
        ("Nel laboratorio è implementato: provalo con\n`client_sunspec.py --limit 30 --revert 10` e rileggi dopo 10 secondi.",
         "Provalo nel [laboratorio](#lab-inverter): limita al 30% con ritorno dopo 10 s e osserva cosa succede."),
    ],
    "04-monitoraggio.md": [
        ("Principi di un buon datalogger (li trovi in `lab/datalogger.py`):", "Principi di un buon datalogger:"),
    ],
    "05-controllo-impianto.md": [
        ("Esegui\n`python3 lab/iec104.py` per vedere una sessione completa decodificata.",
         "Nel\n[laboratorio IEC 104](#lab-iec104) trovi una sessione completa decodificata."),
        ("Prova `lab/ppc.py` con `--period` diversi e due simulatori.",
         "Prova il [controllore del laboratorio](#lab-ppc) con guadagni diversi."),
    ],
}

FILES = {
    "fondamenti": "01-fondamenti.md", "modbus": "02-modbus.md", "sunspec": "03-sunspec.md",
    "monitoraggio": "04-monitoraggio.md", "controllo": "05-controllo-impianto.md",
    "glossario": "07-glossario-e-risorse.md",
}

page = (HERE / "template.html").read_text()
for key, fname in FILES.items():
    text = (SRC / fname).read_text()
    for old, new in REPL.get(fname, []):
        assert old in text, (fname, old[:40])
        text = text.replace(old, new)
    assert "python3" not in text, fname
    html = markdown.markdown(text, extensions=["tables", "fenced_code"])
    html = html.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
    html = html.replace("<pre>", '<pre class="code">')
    page = page.replace(f"<!--LESSON:{key}-->", html)
assert "<!--LESSON" not in page
(HERE / "corso.html").write_text(page)
print("ok", len(page))
