"""Genera web/corso.html dai capitoli del libro (cartella libro/).

Uso:  pip install markdown  &&  python3 build.py
"""
import json
import pathlib
import re

import markdown

HERE = pathlib.Path(__file__).resolve().parent
BOOK = HERE.parent / "libro"

# id della vista, file, numero, titolo breve per la navigazione, descrizione per l'indice
CHAPTERS = [
    ("introduzione", "00-introduzione.md", "0", "Prima di cominciare",
     "Cos'è un protocollo, come è organizzato il libro e come studiarlo"),
    ("bit-e-byte", "01-bit-byte-esadecimale.md", "1", "Bit, byte, esadecimale",
     "La lingua dei messaggi: binario, esadecimale, ordine dei byte, numeri negativi e con la virgola"),
    ("impianto", "02-impianto-e-attori.md", "2", "L'impianto e i suoi attori",
     "Dispositivi, grandezze elettriche, distributore e Terna: chi parla con chi e di cosa"),
    ("seriale-e-rete", "03-seriale-e-rete.md", "3", "Seriale e rete",
     "RS-485, Ethernet, indirizzi IP, porte, TCP; interrogazione, eventi e pubblicazione"),
    ("modbus", "04-modbus-concetti.md", "4", "Modbus: i concetti",
     "Master e slave, registri, codici funzione, richieste e risposte byte per byte, eccezioni"),
    ("modbus-campo", "05-modbus-sul-campo.md", "5", "Modbus sul campo",
     "RTU e CRC, TCP e MBAP, gateway, tempi di lettura, diagnosi dei guasti"),
    ("sunspec", "06-sunspec.md", "6", "SunSpec",
     "Modelli, discovery, fattori di scala, misure dell'inverter e limitazione di potenza"),
    ("monitoraggio", "07-monitoraggio.md", "7", "Il monitoraggio",
     "Datalogger, JSON, HTTPS, MQTT, API, Performance Ratio e qualità del dato"),
    ("controllo", "08-regolazione-e-controllore.md", "8", "Regolazione e controllore",
     "Perché la rete regola gli impianti, anello chiuso, PPC e perdita di comunicazione"),
    ("iec104", "09-iec-104.md", "9", "IEC 60870-5-104",
     "Telecontrollo: IOA, tipi, causa, qualità, sessione e decodifica di un messaggio"),
    ("iec61850", "10-iec-61850.md", "10", "IEC 61850",
     "Modello dati, nodi logici, report, controlli, GOOSE e file SCL"),
    ("normativa", "11-normativa-italiana.md", "11", "CEI 0-16 e CCI",
     "Le regole italiane per gli impianti in media tensione e il Controllore Centrale di Impianto"),
    ("glossario", "12-glossario.md", "A", "Glossario",
     "Tutti i termini del libro, con il capitolo in cui sono spiegati, e risorse per approfondire"),
]

BOX = {"Esempio": "esempio", "Attenzione": "attenzione", "Ricorda": "ricorda", "Prova": "prova"}


def render(md_text):
    html = markdown.markdown(md_text, extensions=["tables", "fenced_code", "md_in_html"])
    # riquadri: un blockquote che inizia con un'etichetta in grassetto
    def box(m):
        cls = BOX.get(m.group(1))
        return f'<blockquote class="box box-{cls}">\n<p><strong>{m.group(1)}</strong>' if cls else m.group(0)
    html = re.sub(r"<blockquote>\s*<p><strong>(\w+)</strong>", box, html)
    # "Cosa imparerai" in evidenza
    html = html.replace("<p><strong>Cosa imparerai:</strong>", '<p class="goals"><strong>Cosa imparerai:</strong>')
    html = html.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
    html = html.replace("<pre>", '<pre class="code">')
    return html


def main():
    sections, meta = [], []
    for vid, fname, num, short, desc in CHAPTERS:
        text = (BOOK / fname).read_text()
        title = re.match(r"# (.+)", text).group(1)
        # il titolo diventa "Capitolo N" + titolo pulito
        clean = re.sub(r"^(Capitolo \d+|Appendice \w) — ", "", title)
        label = re.match(r"^(Capitolo \d+|Appendice \w)", title).group(1)
        body = render(text.split("\n", 1)[1])
        sections.append(
            f'    <section class="view prose chapter" id="v-{vid}" hidden>\n'
            f'      <div class="chapnum">{label}</div>\n      <h1>{clean}</h1>\n{body}\n    </section>')
        meta.append({"id": vid, "n": num, "short": short, "title": clean, "desc": desc})

    page = (HERE / "template.html").read_text()
    assert "<!--CHAPTERS-->" in page and "/*CHAPTERS_JSON*/" in page
    page = page.replace("<!--CHAPTERS-->", "\n".join(sections))
    page = page.replace("/*CHAPTERS_JSON*/", json.dumps(meta, ensure_ascii=False))
    (HERE / "corso.html").write_text(page)
    print(f"ok: {len(CHAPTERS)} capitoli, {len(page)} caratteri")


if __name__ == "__main__":
    main()
