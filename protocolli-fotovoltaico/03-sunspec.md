# Lezione 3 — SunSpec: dare un significato ai registri Modbus

## 3.1 Il problema

Senza standard, ogni produttore di inverter inventa la sua mappa: la potenza attiva può
stare al registro 30775 come int32 in W, o al 40084 come int16 con scale factor, o in un
float… Integrare 5 marche diverse in un portale o in un controllore d'impianto significa
scrivere e testare 5 "driver".

**SunSpec** (SunSpec Alliance) definisce una mappa **standard e auto-descrittiva** sopra Modbus.

## 3.2 Come è organizzata la mappa

```
Indirizzo  Contenuto
40000      0x5375  "Su"   ┐ marker "SunS": "qui c'è una mappa SunSpec"
40001      0x6E53  "nS"   ┘
40002      1               ID del modello (1 = Common)
40003      66              L = lunghezza dei dati del modello, in registri
40004..69  ...             dati del modello 1 (produttore, modello, seriale…)
40070      103             ID del modello successivo (103 = inverter trifase)
40071      50              L
40072..121 ...             dati del modello 103
40122      123             …e così via
  ...
           0xFFFF          ID di fine catena
           0               L = 0
```

Un client non deve conoscere la mappa in anticipo: legge il marker, poi salta di modello in
modello (**discovery**). Indirizzi base ammessi: **40000** (il più comune), 0, 50000.
È esattamente ciò che fa `sunspec.discover()` nel laboratorio.

> Attenzione: la *posizione* di un modello non è fissa (dipende da quali modelli precedono),
> ma la posizione dei *punti dentro* un modello sì. Per questo si fa sempre la discovery.

## 3.3 Interi + scale factor

Quasi tutti i valori sono interi a 16 bit accompagnati da uno **scale factor** (tipo `sunssf`,
intero con segno): `valore reale = valore × 10^SF`.

| Punto | Grezzo | SF | Reale |
|---|---|---|---|
| PhVphA | 2301 | -1 | 230,1 V |
| Hz | 4999 | -2 | 49,99 Hz |
| W | 1850 | 1 | 18 500 W |

Più punti possono condividere lo stesso SF (es. `A`, `AphA`, `AphB`, `AphC` usano tutti `A_SF`).
Lo SF può essere fisso o cambiare a runtime: **leggi valore e SF nella stessa richiesta**,
altrimenti rischi di combinare un valore nuovo con uno SF vecchio.

Valori speciali di **"non implementato"**: `0xFFFF` (uint16/enum16), `0x8000` (int16/sunssf),
`0` per gli accumulatori `acc32`. Un portale serio li mostra come "n/d", non come 65535 W.

## 3.4 I modelli principali

| Modelli | Contenuto |
|---|---|
| 1 | **Common**: produttore, modello, versione, numero di serie, indirizzo |
| 101 / 102 / 103 | **Inverter** monofase / bifase (split) / trifase, interi + SF |
| 111 / 112 / 113 | Come sopra ma con valori float |
| 120 | **Nameplate**: dati di targa (potenza nominale `WRtg`, ecc.) |
| 121 | **Basic Settings**: impostazioni (`WMax`, limiti di tensione…) |
| 122 | Stato esteso e misure aggiuntive |
| 123 | **Immediate Controls**: connessione/disconnessione, limitazione di potenza, cos φ fisso, potenza reattiva |
| 124 | Accumulo (storage) |
| 126 e seguenti | Funzioni di rete a curva: Volt-VAr, Freq-Watt, ecc. |
| 160 | **MPPT multipli**: tensione/corrente/potenza per ingresso DC |
| 201–204 / 211–214 | **Contatori** (mono/trifase, interi o float) |
| 302, 303, 307… | **Sensori meteo**: irraggiamento, temperatura modulo, stazione meteo |
| 701 e seguenti | Nuova famiglia **DER** allineata a IEEE 1547-2018 (misure, capacità, controlli, curve) |
| 64000–65535 | Modelli **proprietari** del produttore |

Le definizioni ufficiali (in JSON) sono pubblicate dalla SunSpec Alliance su GitHub
(`sunspec/models`); la libreria Python ufficiale è **pySunSpec2**.

## 3.5 Il modello 103 in dettaglio (quello che leggerai di più)

Offset rispetto all'inizio dei dati (cioè dopo ID e L):

| Off | Punto | Tipo | Significato |
|---|---|---|---|
| 0–3 | A, AphA, AphB, AphC | uint16 | correnti AC (con `A_SF` all'offset 4) |
| 5–10 | PPVphAB… PhVphC | uint16 | tensioni concatenate e di fase (`V_SF` a 11) |
| 12 | W | int16 | **potenza attiva** (`W_SF` a 13) |
| 14 | Hz | uint16 | frequenza (`Hz_SF` a 15) |
| 16, 18 | VA, VAr | int16 | potenza apparente e reattiva |
| 20 | PF | int16 | fattore di potenza (in %) |
| 22–23 | WH | acc32 | **contatore di energia** (`WH_SF` a 24) |
| 25, 27, 29 | DCA, DCV, DCW | | grandezze lato DC |
| 31–34 | TmpCab, TmpSnk, TmpTrns, TmpOt | int16 | temperature (`Tmp_SF` a 35) |
| 36 | St | enum16 | **stato**: 1 Off, 2 Sleeping, 3 Starting, 4 MPPT, 5 Throttled, 6 Shutting down, 7 Fault, 8 Standby |
| 37 | StVnd | enum16 | stato specifico del produttore |
| 38–39 | Evt1 | bitfield32 | allarmi standard (sovratensione, isolamento, sovratemperatura…) |
| 40–49 | Evt2, EvtVnd1–4 | bitfield32 | altri allarmi / allarmi del produttore |

## 3.6 Comandare un inverter: il modello 123

Per limitare la potenza attiva (la funzione più usata dai controllori d'impianto):

1. scrivi `WMaxLimPct` = percentuale di `WMax` (con `WMaxLimPct_SF`);
2. opzionale: `WMaxLimPct_RmpTms` (rampa), `WMaxLimPct_RvrtTms` (**timeout di ritorno**);
3. scrivi `WMaxLim_Ena = 1` per attivare.

Il **timeout di ritorno** è una sicurezza fondamentale: se il controllore smette di rinnovare
il comando (si guasta, cade la rete), l'inverter torna al comportamento di default invece di
restare bloccato su un comando vecchio. Nel laboratorio è implementato: provalo con
`client_sunspec.py --limit 30 --revert 10` e rileggi dopo 10 secondi.

## 3.7 SunSpec nella realtà

- Molti inverter espongono **sia** una mappa SunSpec **sia** una mappa proprietaria più ricca:
  verifica nella documentazione quale è abilitata (a volte va attivata da menu/app).
- Alcuni implementano SunSpec "a modo loro" (modelli parziali, SF strani, unit id particolari):
  la certificazione SunSpec riduce, ma non elimina, le sorprese.
- I nuovi prodotti tendono verso i modelli **7xx** (IEEE 1547-2018); in campo trovi ancora
  soprattutto 1/103/120/121/123/160.
