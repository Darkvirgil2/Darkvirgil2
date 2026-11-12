# Capitolo 11 — Le regole italiane: CEI 0-16 e il Controllore Centrale di Impianto

**Cosa imparerai:** chi scrive le regole per la connessione degli impianti in Italia; cos'è il
CCI e cosa deve fare; come comunica con il distributore; quali delibere ne hanno reso
obbligatoria l'installazione; cosa chiedere a un fornitore.

> **Attenzione**
> Le regole descritte in questo capitolo sono cambiate più volte negli ultimi anni e potranno
> cambiare ancora. Il capitolo serve a capire **la logica** del sistema. Prima di progettare,
> acquistare o collaudare, verifica sempre il testo **vigente** della norma CEI 0-16, con le sue
> varianti, e delle delibere ARERA.

## 11.1 Chi scrive le regole

- **ARERA**, l'Autorità di Regolazione per Energia Reti e Ambiente, stabilisce **gli obblighi**:
  chi deve fare cosa, entro quando, con quali incentivi o penali. Lo fa con **delibere**,
  identificate da numero e anno, come 540/2021/R/eel.
- Il **CEI**, il Comitato Elettrotecnico Italiano, scrive le **norme tecniche** che dicono **come**
  farlo. Per la connessione degli impianti alla rete le norme principali sono:
  - **CEI 0-16**: utenti connessi alle reti in **alta e media tensione** dei distributori;
  - **CEI 0-21**: utenti connessi in **bassa tensione**.
- I **distributori** (DSO) applicano le regole sulla propria rete e collaudano gli impianti.
- **Terna** stabilisce nel **Codice di Rete** le regole per gli impianti connessi alla rete di
  trasmissione nazionale.

Le norme CEI vengono aggiornate con **varianti** e possono avere **allegati**, indicati con
lettere, dedicati a temi specifici. Il CEI pubblica anche **fogli interpretativi** che chiariscono i
punti dubbi.

## 11.2 Perché serve il CCI

Nel capitolo 8 abbiamo visto che, con centinaia di migliaia di impianti fotovoltaici, il
gestore di rete deve poterli **osservare** e, quando serve, **regolare**. Per gli impianti connessi
in **media tensione** la soluzione italiana è il **Controllore Centrale di Impianto (CCI)**:
un dispositivo installato in ogni impianto, con funzioni e interfaccia di comunicazione
**standardizzate** dalla CEI 0-16. Standardizzare significa che il distributore può dialogare
nello stesso modo con migliaia di impianti diversi, indipendentemente dalla marca degli
inverter.

## 11.3 Cosa dice la CEI 0-16

Le parti della norma dedicate al CCI sono principalmente due allegati:

- **Allegato O**: definisce le **funzioni** del CCI, cioè cosa deve fare;
- **Allegato T**: definisce l'**interfaccia di comunicazione** tra il CCI e il distributore,
  basata su **IEC 61850** (capitolo 10). È stato introdotto con la variante V2 del 2021.

Varianti successive, fino al 2025, hanno aggiornato questi allegati e altri collegati, anche su
richiesta di ARERA. Il CEI ha pubblicato inoltre un foglio interpretativo (CEI 0-16;IS1:2023-07)
con le risposte, concordate con ARERA, alle domande più frequenti sugli Allegati O e T.

### Le funzioni del CCI

In sintesi le funzioni si dividono in due gruppi.

**Osservabilità.** Il CCI raccoglie in tempo reale misure e stati dell'impianto, come potenza
attiva e reattiva, tensione e stato degli interruttori, e li trasmette al distributore, che li
rende disponibili anche a Terna. Il sistema elettrico "vede" così cosa producono gli impianti
distribuiti sul territorio.

**Regolazione e controllo.** Su richiesta del distributore il CCI può ricevere comandi e regolare
l'impianto, per esempio limitando la potenza attiva o regolando la potenza reattiva e la tensione.
Queste funzioni vengono attivate dal distributore quando servono.

> **Ricorda**
> Il CCI **non** fa regolazione di frequenza: quella resta affidata alle funzioni locali degli
> inverter, che reagiscono in modo autonomo e molto più rapido (capitolo 8).

### Requisiti di comunicazione e sicurezza

L'interfaccia con il distributore usa IEC 61850, con il CCI nel ruolo di **server** e il sistema
del distributore nel ruolo di **client**. Poiché il CCI può ricevere comandi che influenzano la rete
elettrica, la norma richiede requisiti di **sicurezza informatica**, tra cui la comunicazione
protetta secondo **IEC 62351-3** e un processo di sviluppo sicuro del prodotto secondo
**IEC 62443-4-1**.

## 11.4 Gli obblighi: le delibere ARERA

- **Delibera 540/2021/R/eel**: ha reso obbligatorie le funzioni di **osservabilità** del CCI per gli
  impianti di produzione connessi in media tensione, con tempistiche diverse per i nuovi impianti
  e per quelli esistenti.
- **Delibera 730/2022/R/eel**: ha modificato le tempistiche della delibera precedente.
- **Delibera 385/2025/R/eel**: ha aggiornato gli obblighi e richiesto modifiche alle funzionalità
  del CCI. Diverse fonti riportano l'obbligo per gli impianti di produzione a partire da **100 kW**
  connessi in media tensione.

> **Attenzione**
> Soglie di potenza, scadenze ed eventuali contributi economici per l'adeguamento degli impianti
> esistenti vanno verificati sul testo ufficiale delle delibere, pubblicato su arera.it, e sulle
> comunicazioni del proprio distributore.

## 11.5 Come si inserisce il CCI nell'impianto

Mettendo insieme tutti i capitoli del libro:

```
                     Distributore (client IEC 61850) ──► Terna
                                ▲
                                │ IEC 61850 (MMS) su collegamento protetto
                                │
                     ┌──────────┴──────────┐
                     │         CCI         │ server IEC 61850
                     └──┬────────┬────────┬┘
                        │        │        │
          Modbus TCP o  │        │        │ Modbus TCP
          altro         ▼        ▼        ▼
                 Misuratore    Inverter  Interruttori,
                 al POI        (SunSpec  protezioni
                               o mappe
                               proprietarie)
```

- **Verso il distributore**: IEC 61850, come richiesto dall'Allegato T.
- **Verso il campo**: la norma non impone un protocollo. Nella pratica il CCI legge un misuratore
  al punto di connessione e comanda gli inverter, quasi sempre in Modbus TCP con SunSpec o con le
  mappe dei produttori (capitoli 4–6), oppure tramite il controllore d'impianto già presente.

Tutto ciò che hai studiato sul campo resta quindi valido: il CCI è un controllore d'impianto
(capitolo 8) con un'interfaccia verso la rete standardizzata.

## 11.6 Impianti in bassa e in alta tensione

- Per gli impianti connessi in **bassa tensione** valgono le regole della **CEI 0-21**.
- Per gli impianti connessi alla **rete di trasmissione** (alta e altissima tensione) valgono i
  requisiti del **Codice di Rete di Terna** e dei suoi allegati, con sistemi di regolazione e
  telecontrollo concordati con Terna, spesso con protocolli come IEC 60870-5-104 (capitolo 9).

## 11.7 Cosa chiedere a un fornitore di CCI

Una lista pratica, che riassume i temi del libro:

1. **Conformità** alla versione vigente della CEI 0-16, con riferimento agli Allegati O e T, e
   relativa documentazione.
2. **Certificazione IEC 61850** del server (test di conformità) e prove di interoperabilità con i
   sistemi del distributore.
3. **Compatibilità con gli inverter** dell'impianto: quali marche e modelli supporta, con quali
   protocolli (SunSpec, mappe proprietarie), con quali tempi di risposta.
4. **Misuratore al punto di connessione**: quale modello, con quale precisione e collegamento.
5. **Comportamento in caso di perdita di comunicazione**, verso il distributore e verso gli
   inverter (capitolo 8).
6. **Sicurezza informatica**: gestione dei certificati, aggiornamenti, accessi da remoto.
7. **Integrazione con il monitoraggio** esistente: il CCI e il datalogger possono convivere sugli
   stessi inverter? Quante connessioni Modbus accettano gli inverter? (capitolo 5)
8. **Messa in servizio e collaudo**: chi esegue le prove con il distributore e con quale procedura.

## Riepilogo

- **ARERA** fissa gli obblighi con le delibere; il **CEI** scrive le norme tecniche (**CEI 0-16** per MT e AT, **CEI 0-21** per BT).
- Il **CCI** permette al distributore di **osservare** e, quando serve, **regolare** gli impianti in media tensione.
- **Allegato O**: funzioni. **Allegato T**: interfaccia **IEC 61850** con il distributore, con requisiti di sicurezza (IEC 62351-3, IEC 62443-4-1).
- Delibere **540/2021**, **730/2022**, **385/2025**: verifica sempre soglie e scadenze aggiornate.
- Verso il campo il CCI usa gli strumenti dei capitoli 4–8: Modbus, SunSpec, anello chiuso.

## Domande di verifica

**1.** Qual è la differenza di ruolo tra ARERA e CEI?

<details markdown="1">
<summary>Risposta</summary>

ARERA stabilisce **gli obblighi** (chi deve installare cosa ed entro quando) con le sue
delibere; il CEI scrive le **norme tecniche** che dicono **come** realizzarli.

</details>

**2.** Nel dialogo IEC 61850 tra CCI e distributore, chi è il server e chi il client?

<details markdown="1">
<summary>Risposta</summary>

Il **CCI** è il **server**: espone il modello dati dell'impianto. Il sistema del **distributore** è
il **client**: si collega, riceve i report e invia i comandi.

</details>

**3.** Perché il CCI non deve occuparsi della regolazione di frequenza?

<details markdown="1">
<summary>Risposta</summary>

Perché la risposta in frequenza deve essere immediata e non può dipendere da una catena di
comunicazione. Gli inverter la realizzano localmente, misurando la frequenza ai propri morsetti.

</details>

**4.** Un impianto da 800 kW in media tensione ha già un controllore d'impianto che comanda gli inverter via Modbus. Il CCI lo sostituisce?

<details markdown="1">
<summary>Risposta</summary>

Dipende dall'architettura scelta: il CCI può comandare direttamente gli inverter oppure
dialogare con il controllore esistente. In ogni caso bisogna verificare la compatibilità, evitare
che due sistemi diano comandi in conflitto agli stessi inverter e controllare quante connessioni
Modbus gli inverter accettano.

</details>
