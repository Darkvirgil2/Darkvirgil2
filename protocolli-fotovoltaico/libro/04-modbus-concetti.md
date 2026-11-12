# Capitolo 4 — Modbus: i concetti

**Cosa imparerai:** perché Modbus è ovunque; i ruoli di master e slave; come sono organizzati
i dati in "registri"; cosa sono i codici funzione; come leggere riga per riga una richiesta e
una risposta reali; cosa succede quando qualcosa va storto.

## 4.1 Un protocollo del 1979 che non passa di moda

Modbus è stato creato nel 1979 dall'azienda Modicon per far comunicare i suoi controllori
industriali. La specifica è pubblica e gratuita ed è molto semplice da implementare. Per
questo quasi ogni dispositivo industriale lo supporta: inverter, contatori, analizzatori di
rete, stazioni meteo, quadri di campo, batterie.

Nel fotovoltaico è il protocollo del **mondo del campo**: lo usano il datalogger per leggere
gli inverter e il controllore d'impianto per comandarli.

Modbus esiste in due varianti principali, che condividono lo stesso "cuore":

- **Modbus RTU**: viaggia su linea seriale, quasi sempre RS-485;
- **Modbus TCP**: viaggia su rete Ethernet/IP, dentro una connessione TCP.

## 4.2 Master e slave

In Modbus c'è sempre **uno che chiede** e **uno che risponde**.

- Il **master** (oggi chiamato anche *client*) è chi interroga: il datalogger, il controllore
  d'impianto, il software di un tecnico.
- Lo **slave** (o *server*) è chi risponde: l'inverter, il contatore, la stazione meteo.

Uno slave **non parla mai di sua iniziativa**. Anche se ha un allarme gravissimo, aspetta che
il master glielo chieda. È il modello a interrogazione visto nel capitolo 3.

Sul bus seriale ogni slave ha un **indirizzo** da 1 a 247, impostato dal menu o dall'app del
dispositivo. Il master scrive l'indirizzo all'inizio di ogni richiesta; solo lo slave con
quell'indirizzo risponde, gli altri ignorano il messaggio.

> **Attenzione**
> Due dispositivi con lo stesso indirizzo sullo stesso bus rispondono insieme, i loro
> segnali si sovrappongono e la risposta arriva corrotta. È uno dei guasti più frequenti
> dopo la sostituzione di un inverter.

## 4.3 I dati: un casellario di registri

L'idea centrale di Modbus è semplicissima. Immagina che ogni dispositivo abbia un grande
**casellario** con migliaia di caselle numerate. In ogni casella c'è un numero da 16 bit
(0–65 535). Il master può chiedere: «dammi il contenuto delle caselle dalla 40072 alla 40121»
oppure «scrivi 30 nella casella 40127».

Queste caselle si chiamano **registri**. Modbus definisce quattro "casellari" diversi:

| Tabella | Contenuto di una casella | Si può scrivere? | Uso tipico |
|---|---|---|---|
| **Coils** | 1 bit | sì | comandi on/off |
| **Discrete inputs** | 1 bit | no | stati, come un contatto aperto o chiuso |
| **Input registers** | 16 bit | no | misure |
| **Holding registers** | 16 bit | sì | misure, impostazioni e comandi |

Nel fotovoltaico si usano quasi solo i **registri da 16 bit**, e moltissimi inverter mettono
tutto negli **holding registers**.

> **Ricorda**
> **Modbus non dice cosa c'è nei registri.** Dice solo come leggerli e scriverli. Che il
> registro 40084 contenga la potenza attiva lo decide il produttore del dispositivo e lo
> scrive in un documento chiamato **mappa dei registri** (*register map*). Senza quel
> documento, i numeri letti non hanno significato. Il capitolo 6 mostra come SunSpec risolve
> questo problema.

### Il pasticcio dei numeri: 40001 o 40000?

Nella documentazione troverai i registri numerati in due modi diversi, ed è la fonte di
errore più comune in assoluto.

- **Numerazione "di documentazione"** (detta anche *Modicon*): la prima cifra indica la tabella
  (4 = holding register, 3 = input register) e la numerazione parte da **1**. Il primo holding
  register è "40001".
- **Indirizzo di protocollo**: il numero che viaggia davvero nel messaggio. Parte da **0** e
  non contiene la cifra della tabella, perché la tabella è indicata dal codice funzione.

Quindi "registro 40001" della documentazione corrisponde all'**indirizzo 0** nel messaggio,
"40002" all'indirizzo 1, e così via. Alcuni produttori, e lo standard SunSpec, scrivono invece
direttamente l'indirizzo di protocollo, che può essere un numero come 40000.

> **Esempio**
> Una mappa dice "Potenza attiva: registro 30775". Con la numerazione di documentazione è
> un input register, indirizzo 30775 − 30001 = **774**. Se il tuo software si aspetta
> l'indirizzo di protocollo e tu scrivi 30775, leggerai una casella completamente diversa
> o riceverai un errore.

> **Attenzione**
> Se leggi valori "spostati di uno", per esempio trovi la tensione dove ti aspetti la
> corrente, quasi sempre il problema è la differenza tra numerazione da 0 e da 1.

## 4.4 I codici funzione

Ogni richiesta inizia dicendo **che cosa** il master vuole fare, con un numero chiamato
**codice funzione** (*function code*, FC). I più usati nel fotovoltaico:

| Codice | Nome | Cosa fa |
|---|---|---|
| **03** | Read Holding Registers | legge uno o più holding register consecutivi |
| **04** | Read Input Registers | legge uno o più input register consecutivi |
| **06** | Write Single Register | scrive un solo registro |
| **16** (0x10) | Write Multiple Registers | scrive più registri consecutivi in una volta |

Esistono altri codici (01, 02, 05, 15 per i bit; 43 per l'identificazione del dispositivo),
ma con questi quattro si fa quasi tutto.

Limiti da ricordare: una lettura può chiedere al massimo **125 registri**, una scrittura
multipla al massimo **123**. Per leggere di più servono più richieste.

## 4.5 Leggere una richiesta, byte per byte

Arriviamo al punto centrale del capitolo. Vogliamo leggere **50 holding register** a partire
dall'**indirizzo 40072** di un inverter. La parte "comune" del messaggio, chiamata **PDU**
(*Protocol Data Unit*), è:

```
03  9C 88  00 32
```

Leggiamola con quanto imparato nel capitolo 1:

| Byte | Significato | Come si legge |
|---|---|---|
| `03` | codice funzione | 3 = Read Holding Registers |
| `9C 88` | indirizzo iniziale | 0x9C88 = 40 072 (big-endian: prima il byte alto) |
| `00 32` | quantità di registri | 0x0032 = 50 |

Sono solo 5 byte, eppure contengono una richiesta completa: «leggi 50 holding register a
partire da 40 072».

## 4.6 Leggere la risposta

Lo slave risponde con:

```
03  64  [100 byte di dati]
```

| Byte | Significato |
|---|---|
| `03` | ripete il codice funzione: «ecco la risposta alla tua lettura» |
| `64` | numero di byte di dati che seguono: 0x64 = 100, cioè 50 registri × 2 byte |
| poi | i 50 registri, ciascuno in due byte, prima il byte alto |

> **Esempio**
> Se i primi 6 byte di dati sono `0D 9B 04 8C 04 87`, i primi tre registri valgono
> 0x0D9B = 3483, 0x048C = 1164, 0x0487 = 1159.
> Cosa significano? Modbus non lo sa: bisogna guardare la mappa dei registri. Nel capitolo 6
> scopriremo che, in un inverter SunSpec, sono correnti espresse in centesimi di ampere:
> 34,83 A, 11,64 A e 11,59 A.

## 4.7 Scrivere un registro

Per scrivere il valore **30** nel registro **40127**, il master invia con il codice 06:

```
06  9C BF  00 1E
```

codice 06, indirizzo 0x9CBF = 40 127, valore 0x001E = 30. Se tutto va bene, lo slave risponde
**ripetendo esattamente la stessa PDU**: è la conferma che la scrittura è avvenuta.

## 4.8 Quando qualcosa va storto: le eccezioni

Se lo slave riceve una richiesta che non può soddisfare, non resta in silenzio: risponde con
una **eccezione**. La risposta ha:

- il codice funzione con il bit più alto a 1, cioè **codice + 0x80** (03 diventa 0x83, 06 diventa 0x86);
- un byte con il **codice d'errore**.

| Codice | Nome | Significato pratico |
|---|---|---|
| 01 | Illegal function | il dispositivo non supporta quel codice funzione (per esempio vuole lo 04 e non lo 03) |
| 02 | Illegal data address | l'indirizzo non esiste, oppure la lettura "sconfina" in una zona vuota, oppure il registro è di sola lettura |
| 03 | Illegal data value | valore non accettabile (per esempio un limite del 150%) o quantità oltre 125 |
| 04 | Server device failure | errore interno del dispositivo |
| 06 | Server device busy | il dispositivo è occupato: riprova più tardi |
| 0B | Gateway target failed to respond | un gateway non ha ricevuto risposta dal dispositivo dietro di lui (capitolo 5) |

> **Esempio**
> Risposta `83 02`: «non posso eseguire la tua lettura (0x83 = 0x03 + 0x80) perché
> l'indirizzo non è valido (02)».

> **Ricorda**
> Un'**eccezione** significa che il dispositivo **ha ricevuto e capito** la richiesta ma non
> la può eseguire: il problema è nella richiesta. Un **timeout**, cioè nessuna risposta,
> significa che il messaggio non è arrivato o non era per lui: il problema è nel collegamento,
> nell'indirizzo o nei parametri. Distinguere i due casi dimezza i tempi di diagnosi.

## 4.9 Il ciclo di vita di una lettura

Mettendo insieme tutto, ogni lettura segue sempre questi passi:

1. il master prepara la richiesta: indirizzo dello slave, codice funzione, indirizzo, quantità;
2. la invia sul bus o sulla connessione TCP;
3. avvia un **timer** (*timeout*), tipicamente da 0,5 a 3 secondi;
4. lo slave interessato risponde con i dati, oppure con un'eccezione;
5. se il timer scade senza risposta, il master può riprovare (*retry*) e poi segnalare un errore di comunicazione;
6. il master interpreta i dati secondo la mappa dei registri.

## Riepilogo

- Modbus: un **master** chiede, gli **slave** rispondono; gli slave non parlano mai per primi.
- I dati sono in **registri** da 16 bit; il significato di ogni registro sta nella **mappa** del produttore.
- Occhio a **40001 contro 40000**: numerazione di documentazione da 1, indirizzo di protocollo da 0.
- Codici funzione principali: **03, 04** (lettura), **06, 16** (scrittura).
- Una richiesta di lettura è `FC + indirizzo + quantità`; la risposta è `FC + numero di byte + dati`.
- **Eccezione** = richiesta capita ma rifiutata (FC + 0x80 e codice d'errore); **timeout** = nessuna risposta.

> **Prova**
> Nel [laboratorio, scheda Inverter SunSpec](#lab-inverter), premi «Leggi ora» e trova nel
> registro dei frame la richiesta `03 9C 88 00 32`. Poi premi i pulsanti di «Prova gli
> errori» e osserva le risposte di eccezione.

## Domande di verifica

**1.** Scrivi la PDU per leggere 10 holding register a partire dall'indirizzo 0.

<details markdown="1">
<summary>Risposta</summary>

`03 00 00 00 0A`: codice 03, indirizzo 0x0000, quantità 0x000A = 10.

</details>

**2.** Una risposta inizia con `03 14`. Quanti registri contiene?

<details markdown="1">
<summary>Risposta</summary>

0x14 = 20 byte di dati, cioè **10 registri**.

</details>

**3.** Il master invia `04 00 00 00 02` e riceve `84 01`. Cosa significa e cosa fai?

<details markdown="1">
<summary>Risposta</summary>

0x84 = 0x04 + 0x80: eccezione sul codice 04. Il codice 01 indica che la funzione non è
supportata: il dispositivo probabilmente non ha input register. Riprova con il codice **03**
(holding register).

</details>

**4.** Il master invia una richiesta allo slave 5 e non riceve nulla. Elenca tre possibili cause.

<details markdown="1">
<summary>Risposta</summary>

Per esempio: lo slave ha un indirizzo diverso da 5; i parametri seriali (velocità, parità)
non coincidono; il cavo è interrotto o A e B sono invertiti; il dispositivo è spento. In
tutti i casi il problema è prima del livello applicativo, perché non c'è stata nemmeno
un'eccezione.

</details>
