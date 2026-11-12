# Lezione 5 — Controllore centrale d'impianto (PPC / CCI) e comunicazione con la rete

## 5.1 Perché serve un controllore d'impianto

Ogni inverter regola potenza attiva e reattiva **ai propri morsetti**. Il gestore di rete però
vuole che certe grandezze siano rispettate al **punto di connessione** (POI, *point of
interconnection*), dove contano tutti gli inverter insieme, i cavi, i trasformatori, i servizi
ausiliari. Il **PPC** (*Power Plant Controller*) — in Italia, per gli impianti in MT, il
**CCI (Controllore Centrale di Impianto)** previsto dalla CEI 0-16 — è il "cervello" che:

1. **misura** al POI (analizzatore di rete / multimetro di precisione);
2. **riceve** setpoint e comandi dal gestore di rete o dallo SCADA;
3. **calcola** i comandi da dare a ciascun inverter (regolazione ad anello chiuso);
4. **invia** i comandi agli inverter e verifica che vengano eseguiti;
5. **riporta** misure e stati al gestore (osservabilità).

Funzioni tipiche: limitazione della potenza attiva, rampe di potenza, setpoint di potenza
reattiva o cos φ, regolazione Q(V) o di tensione, gestione di accumuli.

## 5.2 Architettura e protocolli

```
           Gestore di rete (DSO / TSO)          SCADA / O&M
                   ▲ IEC 61850 (MMS)                ▲ IEC 104, OPC UA, Modbus TCP
                   │ IEC 60870-5-104                │
            ┌──────┴────────────────────────────────┴──────┐
            │          PPC / CCI  (PLC o PC industriale)   │
            └──┬─────────────────┬───────────────────────┬─┘
     Modbus TCP│ / IEC 61850     │ Modbus TCP / SunSpec  │ I/O cablati
               ▼                 ▼  o protocollo propr.  ▼
        Analizzatore al POI   Inverter 1..N        Interruttori, protezioni
        (P, Q, V, f, cos φ)   (eventuali storage)
```

**Verso il basso** (PPC → campo): soprattutto **Modbus TCP**, con mappe SunSpec (modelli 123 o
704) o proprietarie; alcuni produttori offrono protocolli dedicati più veloci o comandi
*broadcast* per raggiungere tutti gli inverter con un solo messaggio. Nelle centrali più grandi
anche IEC 61850.

**Verso l'alto** (PPC → rete/SCADA):

| Protocollo | Dove si usa | Caratteristiche |
|---|---|---|
| **IEC 61850** (MMS su TCP porta 102, GOOSE su Ethernet) | sottostazioni, interfaccia CCI ↔ distributore in Italia (CEI 0-16 All. T) | modello dati a oggetti auto-descrittivo, report a eventi, file di configurazione SCL |
| **IEC 60870-5-104** (TCP porta 2404) | telecontrollo verso TSO, distributori, SCADA in Europa | punti indirizzati (IOA), invio spontaneo, timestamp, comandi con conferma |
| **DNP3** | Nord America | concetti simili a IEC 104 |
| **OPC UA** | integrazione tra sistemi SCADA/IT | modello a oggetti, sicurezza integrata |
| **Modbus TCP** | SCADA semplici, integrazioni locali | facile ma senza eventi, timestamp né sicurezza |

## 5.3 IEC 60870-5-104 in pratica

È il "Modbus dei telecontrolli", ma con concetti molto diversi. Esegui
`python3 lab/iec104.py` per vedere una sessione completa decodificata.

- **Indirizzamento**: *Common Address* (identifica la stazione/impianto) + *IOA* (indirizzo
  dell'oggetto informativo, es. 1001 = potenza attiva al POI). La lista dei punti (la "signal list"
  o "lista segnali") è concordata tra impianto e gestore: è il vero documento di progetto.
- **Tipi (Type ID)**: segnali singoli/doppi (stati interruttori), misure (normalizzate, scalate,
  float), con o senza timestamp, comandi, setpoint, interrogazione generale, sincronizzazione orologio.
- **Causa di trasmissione**: spontanea, periodica, risposta a interrogazione, attivazione,
  conferma… dice *perché* arriva quel messaggio.
- **Qualità**: ogni dato porta flag come *non valido*, *non aggiornato*, *sostituito*.
- **Sessione**: `STARTDT` apre il flusso, i messaggi I sono numerati e confermati (parametri
  k = 12 messaggi non confermati, w = 8), `TESTFR` mantiene viva la connessione; timeout t1/t2/t3.
- **Comandi**: possono essere *direct execute* o *select-before-operate* (prima seleziono, poi
  eseguo: protegge da comandi accidentali).

## 5.4 IEC 61850 in pratica

Nato per l'automazione delle sottostazioni, è diventato il riferimento anche per gli impianti di
produzione e per l'interfaccia con il distributore.

**Modello dati gerarchico** (auto-descrittivo: un client può "sfogliare" il server):

```
Server (IED)
└── Logical Device        es. "CCI1"
    └── Logical Node      es. MMXU1 (misure), XCBR1 (interruttore), CSWI1 (comando)...
        └── Data Object   es. TotW (potenza attiva totale), PhV (tensioni di fase)
            └── Data Attribute   es. mag.f (valore float), q (qualità), t (timestamp)

Riferimento completo:  CCI1/MMXU1.TotW.mag.f   [FC = MX, cioè grandezza misurata]
```

- I **Logical Node** sono standardizzati: le prime lettere indicano la famiglia (M = misure,
  X = apparecchiature di manovra, C = controllo, P = protezioni, G = generici, D = risorse
  distribuite secondo **IEC 61850-7-420**, Z = altre apparecchiature, ecc.).
- **Functional Constraint (FC)**: MX misure, ST stati, CO comandi, SP/SE setpoint e parametri, CF configurazione.
- **Servizi**: lettura/scrittura, **report** (bufferizzati o no: il server invia i dati quando
  cambiano o a intervalli), **controlli** (direct o select-before-operate, anche con *enhanced
  security*), log, file transfer.
- **Mappatura su protocolli**: client/server su **MMS** (TCP 102); **GOOSE** (multicast Ethernet
  di livello 2, millisecondi, per interblocchi e protezioni); **Sampled Values** (campioni di
  corrente/tensione).
- **SCL** (Substation Configuration Language, XML): ICD = capacità di un dispositivo,
  CID = configurazione di uno specifico dispositivo, SCD = intera sottostazione. Lo scambio di
  file SCL è parte integrante della messa in servizio.
- **Interoperabilità**: esistono test di conformità (UCA International Users Group). Server non
  testati possono non dialogare correttamente con i client dei gestori.
- **Sicurezza**: famiglia **IEC 62351** (es. 62351-3: TLS per i profili su TCP).

## 5.5 Il contesto italiano: il CCI per gli impianti in media tensione

> ⚠️ Il quadro normativo è cambiato più volte negli ultimi anni. Quanto segue è un orientamento:
> verifica sempre la **versione vigente** della CEI 0-16 (e delle sue varianti) e le delibere ARERA
> aggiornate prima di progettare o acquistare.

- **Norma CEI 0-16** (regola tecnica di connessione degli utenti attivi e passivi alle reti AT e MT
  dei distributori):
  - **Allegato O** — requisiti funzionali del **CCI**;
  - **Allegato T** — interfaccia di comunicazione del CCI verso il distributore basata su **IEC 61850**
    (introdotto con la variante V2 del 2021), con requisiti di cybersecurity (es. IEC 62351-3 per
    la comunicazione sicura, IEC 62443-4-1 per il processo di sviluppo sicuro).
  - Successive varianti (fino al 2025) hanno aggiornato gli allegati O, T e U.
- **ARERA 540/2021/R/eel**: ha reso obbligatorie le funzioni di **osservabilità** del CCI per gli
  impianti di produzione connessi in MT; **730/2022/R/eel** ne ha modificato le tempistiche;
  **385/2025/R/eel** ha ulteriormente aggiornato obblighi e funzionalità (diverse fonti riportano
  l'obbligo per impianti a partire da **100 kW** connessi in MT — verifica soglie e scadenze sul testo ufficiale).
- **Funzioni del CCI** (in sintesi):
  - **osservabilità**: invio in tempo reale al distributore (che le rende disponibili anche a Terna)
    di misure e stati dell'impianto (potenze, tensioni, stato degli interruttori…);
  - **regolazione/controllo** (funzioni attivabili su richiesta del distributore): limitazione
    della potenza attiva, regolazione della potenza reattiva/tensione;
  - il CCI **non** effettua regolazione di frequenza: quella resta affidata alle funzioni locali
    degli inverter.
- **Impianti connessi alla rete di trasmissione (AT/AAT)**: valgono i requisiti del **Codice di Rete
  Terna** e dei suoi allegati, con regolazione e telecontrollo concordati con Terna.

Lato campo, il CCI comunica tipicamente con gli inverter in **Modbus TCP** (SunSpec o mappe del
produttore) e con l'analizzatore al POI: tutto ciò che hai visto nelle lezioni 2–3 resta valido.

## 5.6 Le domande che contano davvero in un progetto di controllo

1. **Tempi**: quanto deve rispondere l'impianto a un nuovo setpoint? Il ciclo misura→calcolo→
   comando→effetto deve stare dentro quel tempo, inclusi polling Modbus, rampe degli inverter
   e ritardi di rete. Prova `lab/ppc.py` con `--period` diversi e due simulatori.
2. **Perdita di comunicazione**: cosa fa l'inverter se il PPC tace? E il PPC se il gestore tace?
   Mantiene l'ultimo setpoint, va a un valore di sicurezza, torna al default? (watchdog, timeout
   di ritorno, valori di *fallback*).
3. **Sincronizzazione oraria**: NTP o PTP; i timestamp devono essere coerenti tra campo, PPC e gestore.
4. **Qualità del dato**: una misura non valida va marcata come tale, non sostituita con 0.
5. **Sicurezza**: segmentazione di rete, VPN/router certificati verso il gestore, nessun servizio
   esposto, gestione di certificati e password.
6. **Documentazione**: lista segnali (IOA o riferimenti 61850), file SCL, mappe Modbus, verbali di
   prova end-to-end con il gestore.
