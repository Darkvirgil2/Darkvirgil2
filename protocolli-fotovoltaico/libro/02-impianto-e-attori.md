# Capitolo 2 — L'impianto fotovoltaico e i suoi attori

**Cosa imparerai:** com'è fatto un impianto dal punto di vista di chi deve monitorarlo e
controllarlo; quali dispositivi producono informazioni; quali grandezze elettriche si
misurano e cosa significano; chi sono i soggetti esterni che vogliono quei dati.

Prima di parlare di protocolli conviene sapere **chi** comunica e **di cosa**. In questo
capitolo percorriamo l'impianto seguendo l'energia, dal pannello alla rete, e annotiamo ogni
dispositivo che "ha qualcosa da dire".

## 2.1 Il percorso dell'energia

```
 Sole
  │
  ▼
 Moduli FV ──► Stringhe ──► Inverter ──► Quadro BT ──► Trasformatore ──► Cabina di ──► Rete del
 (corrente      (moduli      (DC → AC)    (bassa        BT/MT            consegna      distributore
  continua)     in serie)                 tensione)    (solo impianti   (punto di     (media
                                                       in MT)           connessione)  tensione)
```

1. **Moduli fotovoltaici.** Trasformano la luce in corrente **continua** (DC).
2. **Stringhe.** I moduli sono collegati in serie a formare stringhe, che arrivano a diverse
   centinaia di volt in continua. Negli impianti grandi le stringhe confluiscono in
   **quadri di campo** (*string box*), che possono misurare la corrente di ogni stringa.
3. **Inverter.** Converte la corrente continua in corrente **alternata** (AC) a 50 Hz, quella
   della rete. È il dispositivo più "intelligente" dell'impianto: misura quasi tutto, decide
   quanta potenza estrarre dai moduli e accetta comandi. Contiene uno o più **MPPT**, i
   circuiti che cercano continuamente il punto di funzionamento in cui i moduli danno la
   massima potenza.
4. **Quadro di bassa tensione.** Raccoglie le uscite degli inverter. In un impianto domestico
   l'energia va direttamente alla rete in bassa tensione (BT, 230/400 V).
5. **Trasformatore e cabina.** Negli impianti più grandi (tipicamente da qualche centinaio di
   kW in su) la tensione viene alzata alla **media tensione** (MT, in Italia di solito 15 o
   20 kV) e l'energia passa per la **cabina di consegna**.
6. **Punto di connessione (POI).** È il confine tra l'impianto e la rete pubblica. Il gestore di
   rete guarda soprattutto cosa succede qui.

## 2.2 Chi produce informazioni

Lungo questo percorso ci sono i dispositivi che comunicano:

| Dispositivo | Cosa sa | Cosa può fare |
|---|---|---|
| **Inverter** | potenza, tensioni e correnti AC e DC, frequenza, temperature, energia prodotta, stato, allarmi | ridurre la potenza, regolare la potenza reattiva, disconnettersi |
| **Quadri di campo** | correnti delle singole stringhe | (di solito niente) |
| **Analizzatore di rete al POI** | potenze, tensioni, correnti, fattore di potenza nel punto di connessione | niente: misura soltanto |
| **Contatori fiscali** | energia prodotta, immessa e prelevata, con valore legale | niente: li legge il distributore |
| **Stazione meteo** | irraggiamento solare, temperatura dei moduli e dell'aria, vento | niente |
| **Protezioni** (SPI, SPG) | stato degli interruttori, interventi delle protezioni | aprire l'interruttore se la rete è fuori dai limiti |
| **Datalogger** | raccoglie i dati di tutti gli altri | li invia al portale di monitoraggio |
| **Controllore d'impianto** (PPC o CCI) | misure al POI e richieste del gestore | comandare gli inverter |

L'**SPI** (Sistema di Protezione di Interfaccia) stacca l'impianto dalla rete se tensione o
frequenza escono dai limiti; l'**SPG** (Sistema di Protezione Generale) protegge dai guasti
come i cortocircuiti. Il datalogger e il controllore d'impianto hanno capitoli dedicati (7 e 8).

## 2.3 Le grandezze elettriche, spiegate una per una

I protocolli trasportano quasi sempre le stesse grandezze. Vale la pena fissarne bene il
significato, perché confonderle porta a errori gravi nell'interpretazione dei dati.

**Tensione (V, volt).** È la "spinta" elettrica. In BT la tensione tra una fase e il neutro è
circa 230 V; tra due fasi (**tensione concatenata**) circa 400 V. In MT si parla di kV. Lato DC
di un inverter si trovano spesso tra 600 e 1000 V o più.

**Corrente (A, ampere).** È la quantità di elettricità che scorre. In un sistema trifase si
misura su ciascuna delle tre fasi, indicate con A, B, C oppure L1, L2, L3.

**Potenza attiva (W, watt; kW, MW).** È l'energia trasferita in ogni istante, quella che fa
"lavoro utile". Quando diciamo che un impianto "sta producendo 80 kW" parliamo di potenza
attiva, indicata con **P**.

**Energia (Wh, kWh, MWh).** È la potenza accumulata nel tempo: 80 kW per 2 ore fanno 160 kWh.
I dispositivi la forniscono come **contatore** che cresce sempre.

> **Attenzione**
> Potenza ed energia sono cose diverse, come la velocità e i chilometri percorsi. La potenza
> è istantanea (kW), l'energia è cumulata (kWh). Molti errori nei report nascono dal
> sommare potenze come se fossero energie, o viceversa.

**Potenza reattiva (var, kvar).** In corrente alternata una parte della potenza "va e viene"
tra generatore e rete senza produrre lavoro utile: è la potenza reattiva, **Q**. Non serve a
far funzionare i carichi, ma influisce sulla **tensione** della rete. Per questo il gestore
può chiedere agli impianti di assorbirne o erogarne un po' (capitolo 8).

**Potenza apparente (VA, kVA).** Combina attiva e reattiva: S = √(P² + Q²). Un inverter ha un
limite di potenza apparente: se deve erogare molta Q, gli resta meno spazio per la P.

**Fattore di potenza (cos φ).** Indica che parte della potenza apparente è attiva: cos φ = P / S.
Vale 1 quando non c'è reattiva. A volte è espresso in percentuale (100%).

**Frequenza (Hz).** Il numero di oscillazioni al secondo della corrente alternata: in Europa 50 Hz.
Dipende dall'equilibrio tra produzione e consumo in tutta la rete europea: se si produce più
di quanto si consuma la frequenza sale, altrimenti scende. Varia di pochi centesimi di Hz.

**Irraggiamento (W/m²).** La potenza della luce solare su un metro quadrato. Al sole pieno è
intorno a 1000 W/m². Si misura con un **piranometro** o una **cella di riferimento** ed è
indispensabile per capire se l'impianto produce quanto dovrebbe (capitolo 7).

> **Esempio**
> Un inverter da 20 kW, al sole pieno, potrebbe riportare: P = 18,5 kW; Q = 0 kvar;
> cos φ = 1; tensioni di fase 230 V; correnti circa 26,8 A per fase; frequenza 49,99 Hz;
> lato DC 650 V e 29 A; temperatura interna 43 °C; energia totale 1 234 567 kWh.

## 2.4 Chi vuole questi dati, e perché

Le informazioni dell'impianto servono a soggetti diversi, con esigenze molto diverse.

**Il proprietario e il gestore degli asset.** Vogliono sapere quanto si produce e quanto si
guadagna: energia giornaliera e mensile, confronto con le attese, guasti che fanno perdere
produzione. Dati ogni 5–15 minuti vanno benissimo.

**L'operatore di manutenzione (O&M).** Vuole allarmi tempestivi e precisi (quale inverter, quale
stringa, quale errore) per mandare la squadra giusta con il ricambio giusto.

**Il distributore (DSO).** È la società che gestisce la rete locale a cui l'impianto è
collegato; in gran parte d'Italia è e-distribuzione, ma ce ne sono altri. Vuole **osservare**
gli impianti, cioè conoscerne in tempo reale la produzione, e in alcuni casi **regolarli**
per mantenere la tensione della sua rete nei limiti.

**Il gestore della rete di trasmissione (TSO).** In Italia è **Terna**. Gestisce l'alta
tensione e l'equilibrio dell'intero sistema elettrico nazionale. Ha bisogno di sapere quanto
producono le fonti rinnovabili per prevedere e bilanciare il sistema.

**Il GSE** (Gestore dei Servizi Energetici) gestisce incentivi e contratti di ritiro
dell'energia; usa soprattutto i dati di energia dei contatori.

Queste esigenze si traducono in tempi e requisiti diversi:

| Chi | Tempo di aggiornamento | Cosa conta di più |
|---|---|---|
| Proprietario, portale | 5–15 minuti | completezza dello storico |
| Manutenzione | da secondi a minuti | allarmi chiari e affidabili |
| Distributore, Terna | da 1 a pochi secondi | dati in tempo reale, affidabilità, sicurezza informatica |
| Controllore d'impianto | sotto il secondo | rapidità e certezza dei comandi |

## 2.5 I tre "mondi" della comunicazione

Mettendo insieme quanto visto, la comunicazione di un impianto si divide in tre mondi, che
ritroverai per tutto il libro:

```
               ┌───────────────────────────────────────────────┐
               │   3. MONDO DELLA RETE ELETTRICA               │
               │   distributore, Terna — IEC 61850, IEC 104    │
               └──────────────────────▲────────────────────────┘
                                      │
 ┌──────────────────────────┐   ┌─────┴──────────────────┐
 │ 2. MONDO DEL MONITORAGGIO │   │ Controllore d'impianto │
 │ portali, O&M — Internet,  │   │ (PPC / CCI)            │
 │ HTTPS, MQTT               │   └─────┬──────────────────┘
 └────────────▲─────────────┘         │
              │ Datalogger            │
 ┌────────────┴──────────────────────┴───────────────────┐
 │   1. MONDO DEL CAMPO                                    │
 │   inverter, contatori, meteo — Modbus, SunSpec          │
 └─────────────────────────────────────────────────────────┘
```

1. **Il campo**: i dispositivi dentro l'impianto. Protocolli semplici ed economici, soprattutto
   Modbus (capitoli 4–6).
2. **Il monitoraggio**: dal datalogger al portale via Internet (capitolo 7).
3. **La rete elettrica**: dal controllore d'impianto al gestore di rete, con protocolli più
   robusti e sicuri (capitoli 8–11).

## Riepilogo

- L'energia va da moduli → stringhe → inverter → quadro → (trasformatore e cabina) → punto di connessione.
- L'**inverter** è il dispositivo che sa e può fare di più; l'**analizzatore al POI** misura ciò che vede la rete.
- **Potenza** (kW) ≠ **energia** (kWh). La **reattiva** (kvar) influenza la tensione; la **frequenza** riflette l'equilibrio di tutta la rete.
- I dati servono a proprietari, manutentori, **distributore** e **Terna**, con tempi da minuti a frazioni di secondo.
- Tre mondi: **campo**, **monitoraggio**, **rete elettrica**.

## Domande di verifica

**1.** Un portale mostra «Produzione oggi: 85 kW». Cosa c'è di sbagliato?

<details markdown="1">
<summary>Risposta</summary>

La produzione di una giornata è un'**energia** e si misura in kWh. 85 kW è una potenza
istantanea. O l'unità è sbagliata, o il portale sta mostrando la potenza del momento con
un'etichetta sbagliata.

</details>

**2.** Perché l'analizzatore al punto di connessione non dà lo stesso valore della somma delle potenze degli inverter?

<details markdown="1">
<summary>Risposta</summary>

Tra inverter e punto di connessione ci sono cavi e trasformatore, che hanno delle perdite, e
i servizi ausiliari dell'impianto (ventilazione, illuminazione, sistemi di sicurezza) che
consumano una parte dell'energia. Il punto di connessione vede il risultato netto.

</details>

**3.** Chi è il DSO e chi è il TSO in Italia?

<details markdown="1">
<summary>Risposta</summary>

Il **DSO** è il distributore che gestisce la rete locale a media e bassa tensione (per gran
parte del territorio e-distribuzione). Il **TSO** è **Terna**, che gestisce la rete di
trasmissione ad alta tensione e l'equilibrio del sistema nazionale.

</details>

**4.** Un inverter da 100 kVA deve erogare 60 kvar di potenza reattiva. Quanta potenza attiva può ancora erogare al massimo?

<details markdown="1">
<summary>Risposta</summary>

S² = P² + Q², quindi P = √(100² − 60²) = √(10 000 − 3 600) = √6 400 = **80 kW**.

</details>
