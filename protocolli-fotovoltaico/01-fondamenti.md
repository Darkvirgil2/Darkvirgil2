# Lezione 1 — Fondamenti: come "parlano" i dispositivi di un impianto

## 1.1 La mappa di un impianto fotovoltaico

Prima dei protocolli, conviene avere chiaro **chi parla con chi**:

```
                         INTERNET / RETE DEL GESTORE
        ┌─────────────────────────┬───────────────────────────────┐
        │                         │                               │
  Portale di monitoraggio   Gestore di rete (DSO, es.      Operatore O&M,
  (cloud del produttore     e-distribuzione) / TSO (Terna) SCADA di flotta
  o indipendente)                 ▲  IEC 61850 / IEC 104          ▲
        ▲  HTTPS, MQTT, SFTP      │                               │
        │                         │                               │
  ┌─────┴──────┐           ┌──────┴───────────┐                   │
  │ Datalogger │           │ Controllore      │◄──────────────────┘
  │ / gateway  │           │ d'impianto       │   Modbus TCP, IEC 104, OPC UA
  └─────┬──────┘           │ (PPC / CCI)      │
        │                  └──────┬───────────┘
        │   Modbus RTU (RS-485) / Modbus TCP / protocolli proprietari
  ──────┴─────────────────────────┴──────────────────────────────────── rete di campo
     │            │             │              │               │
  Inverter    Inverter     Contatore /     Stazione        Protezione
  di stringa  centralizz.  analizzatore    meteo           (SPI / SPG)
                           al POI          (piranometro)
```

Tre "mondi" con esigenze diverse:

| Mondo | Esigenza principale | Tempi tipici | Protocolli tipici |
|---|---|---|---|
| **Campo** (inverter, sensori, contatori) | leggere/scrivere valori in modo semplice ed economico | 0,1–5 s | Modbus RTU/TCP, SunSpec, proprietari |
| **Monitoraggio** (portali, O&M) | raccogliere storici, KPI, allarmi; robustezza ai buchi di rete | 1–15 min | HTTPS/REST, MQTT, FTP/SFTP con CSV |
| **Controllo e rete** (PPC, CCI, gestore) | comandi affidabili, tempi certi, sicurezza, tracciabilità | 100 ms – pochi s | IEC 61850, IEC 60870-5-104, (DNP3 in Nord America) |

## 1.2 I livelli: dal cavo al significato

Un protocollo industriale va sempre letto "a strati". Esempio: un inverter letto da un datalogger via Ethernet.

| Strato | Domanda a cui risponde | Esempio |
|---|---|---|
| Fisico | Che cavo, che tensioni? | RS-485 a 2 fili, Ethernet in rame, fibra ottica, 4G |
| Collegamento | Come si delimita un messaggio? Chi parla? | Frame RTU con CRC; Ethernet MAC |
| Rete/trasporto | Come arriva a destinazione? | IP + TCP (porta 502 per Modbus, 2404 per IEC 104, 102 per IEC 61850 MMS) |
| Applicazione | Che operazione faccio? | "Leggi 50 registri da 40072" (Modbus FC03) |
| **Modello dati** | Cosa significano quei numeri? | "Il registro 40084 è la potenza attiva in W × 10^SF" (SunSpec) |

> **Idea chiave**: Modbus ti dice *come* leggere un registro, ma non *cosa* ci trovi dentro.
> Per questo esistono i **modelli dati** (SunSpec per Modbus, IEC 61850 per il mondo delle
> sottostazioni). Metà dei problemi pratici nasce dallo strato "modello dati", non dal cavo.

## 1.3 RS-485: il bus seriale ancora ovunque

- Coppia di fili intrecciata (+ riferimento comune), segnale **differenziale** → resiste ai disturbi.
- Fino a ~1200 m e 32 "carichi unitari" per segmento (di più con transceiver a carico ridotto).
- Topologia **a catena (daisy chain)**, non a stella. Le derivazioni lunghe creano riflessioni.
- **Terminazione** da 120 Ω ai due estremi del bus (solo ai due estremi!).
- **Polarizzazione** (bias) per tenere la linea in uno stato definito quando nessuno trasmette.
- Half-duplex: parla uno alla volta → serve un **master** che decide i turni.

Problemi tipici sul campo: A/B invertiti (i produttori non usano la stessa convenzione!),
terminazioni mancanti o in eccesso, schermo collegato a terra in più punti, velocità/parità
diverse tra dispositivi, due dispositivi con lo stesso indirizzo.

## 1.4 Paradigmi di comunicazione

1. **Master/slave (client/server) a polling** — Modbus. Il master chiede, lo slave risponde. Semplice,
   prevedibile, ma il master deve chiedere tutto continuamente anche se nulla cambia.
2. **Report spontanei / a eventi** — IEC 60870-5-104, IEC 61850 (report, GOOSE), DNP3. Il dispositivo
   invia i dati quando cambiano oltre una soglia (*deadband*) o periodicamente. Meno traffico,
   reazione più rapida agli eventi, timestamp alla sorgente.
3. **Publish/subscribe** — MQTT. Chi produce dati li pubblica su un *topic* presso un *broker*;
   chi è interessato si iscrive. Ottimo verso il cloud: il datalogger apre la connessione verso
   l'esterno (niente porte aperte in ingresso nell'impianto).
4. **Request/response su HTTP (REST)** — le API dei portali. Comodo per integrare software, non
   pensato per il tempo reale.

## 1.5 Rappresentazione dei dati: dove si sbaglia sempre

- **Endianness**: Modbus trasmette i registri a 16 bit in *big-endian*; IEC 104 usa *little-endian*.
- **Word order** per valori a 32 bit (float, contatori): alcuni dispositivi mettono prima la word
  alta, altri la bassa ("word swap"). SunSpec impone la word alta per prima.
- **Signed/unsigned**: 65534 letto come unsigned è -2 come signed (complemento a due).
- **Scale factor / moltiplicatori**: 2301 può significare 230,1 V.
- **Indirizzi base 0 o base 1**: "registro 40001" nella documentazione può essere l'indirizzo 40000
  nel frame (vedi Lezione 2).
- **Valori "non implementato"**: 0xFFFF, 0x8000, NaN — da non trasformare in numeri sul portale.
- **Unità e convenzioni di segno**: potenza reattiva induttiva/capacitiva, energia immessa/prelevata.

## Cosa portarti a casa

Quando affronti un nuovo dispositivo chiediti sempre, in quest'ordine:
mezzo fisico → parametri di collegamento (indirizzo, baud, parità / IP, porta) →
protocollo → **mappa dei registri / modello dati** → tipi, scale, unità → frequenza di lettura.
