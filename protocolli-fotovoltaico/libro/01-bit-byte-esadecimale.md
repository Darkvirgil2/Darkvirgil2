# Capitolo 1 — Bit, byte e numeri esadecimali

**Cosa imparerai:** cosa sono bit e byte; come si scrive un numero in binario e in
esadecimale e come si torna al decimale; come si rappresentano i numeri negativi, quelli con
la virgola e i testi; cosa significano *big-endian* e *little-endian*.

Ogni messaggio che due dispositivi si scambiano è, alla fine, una sequenza di numeri. Per
leggere quei messaggi devi sapere come sono scritti quei numeri. È come imparare l'alfabeto
prima di leggere un libro: noioso per un'ora, poi non ci pensi più.

## 1.1 Il bit

Un circuito elettronico distingue facilmente due situazioni: c'è tensione oppure non c'è.
Su un cavo di comunicazione: una tensione positiva oppure negativa. Queste due situazioni si
indicano con le cifre **1** e **0**. Una singola cifra di questo tipo si chiama **bit**
(*binary digit*, cifra binaria).

Un bit da solo può rappresentare solo due cose: acceso o spento, aperto o chiuso, sì o no.
Per esempio "l'interruttore generale è chiuso" si può codificare con un solo bit.

## 1.2 Il byte

Per rappresentare informazioni più ricche si mettono in fila più bit. Un gruppo di **8 bit**
si chiama **byte**. Con 8 bit si possono formare 2 × 2 × 2 × 2 × 2 × 2 × 2 × 2 = **256**
combinazioni diverse, quindi un byte può rappresentare i numeri **da 0 a 255**.

Il byte è l'unità di misura di quasi tutto in informatica, e anche nei protocolli: quando
diremo che un messaggio è lungo 12 byte, intenderemo 12 gruppi da 8 bit, cioè 96 bit
trasmessi uno dopo l'altro.

## 1.3 Il sistema binario

Nel sistema decimale che usiamo ogni giorno ogni cifra vale dieci volte quella alla sua
destra: in 352 il 3 vale 300, il 5 vale 50, il 2 vale 2. Il sistema **binario** funziona allo
stesso modo, ma ogni posizione vale **il doppio** di quella alla sua destra:

| Posizione (da destra) | 8ª | 7ª | 6ª | 5ª | 4ª | 3ª | 2ª | 1ª |
|---|---|---|---|---|---|---|---|---|
| Valore della posizione | 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1 |

Per sapere quanto vale un numero binario si sommano i valori delle posizioni dove c'è un 1.

> **Esempio**
> Quanto vale il byte `00000110`?
> Ci sono degli 1 nelle posizioni che valgono 4 e 2: 4 + 2 = **6**.
>
> Quanto vale `11111111`? 128 + 64 + 32 + 16 + 8 + 4 + 2 + 1 = **255**, il massimo per un byte.

Il binario è perfetto per le macchine ma scomodo per noi: le stringhe di 0 e 1 sono lunghe e
facili da sbagliare. Per questo si usa quasi sempre un'altra notazione, l'esadecimale.

## 1.4 Il sistema esadecimale

Il sistema **esadecimale** (base 16) usa sedici simboli: le cifre da 0 a 9 e poi le lettere
**A, B, C, D, E, F**, che valgono rispettivamente 10, 11, 12, 13, 14 e 15.

Il motivo per cui è così usato è semplice: **una cifra esadecimale corrisponde esattamente a
4 bit**, quindi **un byte si scrive sempre con due cifre esadecimali**. Questa è la tabella
da tenere a portata di mano:

| Esadecimale | Binario | Decimale | | Esadecimale | Binario | Decimale |
|---|---|---|---|---|---|---|
| 0 | 0000 | 0 | | 8 | 1000 | 8 |
| 1 | 0001 | 1 | | 9 | 1001 | 9 |
| 2 | 0010 | 2 | | A | 1010 | 10 |
| 3 | 0011 | 3 | | B | 1011 | 11 |
| 4 | 0100 | 4 | | C | 1100 | 12 |
| 5 | 0101 | 5 | | D | 1101 | 13 |
| 6 | 0110 | 6 | | E | 1110 | 14 |
| 7 | 0111 | 7 | | F | 1111 | 15 |

Per far capire che un numero è esadecimale si scrive in genere il prefisso `0x` (per
esempio `0x9C`) oppure il suffisso `h` (`9Ch`). Nei messaggi stampati byte per byte, come
`01 03 9C 88 00 32`, il prefisso si omette: si sa già che ogni coppia è un byte esadecimale.

### Dall'esadecimale al decimale

Ogni posizione esadecimale vale sedici volte quella alla sua destra: 1, 16, 256, 4096…

> **Esempio**
> Quanto vale `0x9C`?
> 9 × 16 + C × 1 = 9 × 16 + 12 = 144 + 12 = **156**.
>
> Quanto vale `0x9C88`, scritto con due byte?
> 9 × 4096 + C × 256 + 8 × 16 + 8 = 36 864 + 3 072 + 128 + 8 = **40 072**.
>
> Incontrerai proprio questo numero nel capitolo 6: è l'indirizzo dove molti inverter
> tengono le loro misure.

### Dal decimale all'esadecimale

Si divide ripetutamente per 16 e si prendono i resti, letti dal basso verso l'alto.

> **Esempio**
> Convertiamo **50** in esadecimale.
> 50 ÷ 16 = 3 con resto 2. 3 ÷ 16 = 0 con resto 3. Leggendo i resti dal basso: **0x32**.
> Verifica: 3 × 16 + 2 = 50. ✔

Non devi diventare veloce nei calcoli: qualsiasi calcolatrice del telefono in modalità
"programmatore" lo fa per te. Devi però capire **cosa** stai convertendo e **perché**.

## 1.5 Numeri più grandi di un byte: le parole da 16 bit

Un byte arriva solo a 255. Una tensione di 230,0 V o una potenza di 18 500 W non ci stanno.
Si usano allora **due byte insieme**, cioè 16 bit, che permettono valori da **0 a 65 535**.
Un gruppo di 16 bit si chiama spesso **parola** (*word*) e, nel protocollo Modbus,
**registro**.

Il byte che contiene la parte "grande" del numero si chiama **byte alto** (o più
significativo), l'altro **byte basso**. Il valore è:

> valore = byte alto × 256 + byte basso

> **Esempio**
> I due byte `08 FD` valgono 0x08 × 256 + 0xFD = 8 × 256 + 253 = 2048 + 253 = **2301**.
> Vedremo nel capitolo 6 che, in un inverter, 2301 può voler dire 230,1 V.

## 1.6 L'ordine dei byte: big-endian e little-endian

Quando un numero occupa due byte bisogna decidere quale trasmettere per primo. Non esiste
una scelta giusta: è una convenzione, e ogni protocollo fa la sua.

- **Big-endian**: prima il byte alto, poi quello basso. È come scriviamo i numeri: prima le
  migliaia, poi le unità. Lo usa **Modbus**.
- **Little-endian**: prima il byte basso, poi quello alto. Lo usa **IEC 60870-5-104** (capitolo 9)
  e anche il controllo d'errore CRC di Modbus RTU (capitolo 5).

> **Esempio**
> Il numero 2301 (0x08FD) viaggia così:
> in big-endian `08 FD`; in little-endian `FD 08`.
> Se chi riceve si aspetta l'ordine sbagliato legge `FD 08` come 0xFD08 = **64 776**.

> **Attenzione**
> Un errore di ordine dei byte non produce un messaggio d'errore: produce un **numero
> sbagliato**. Se leggi valori assurdi ma "stabili", come una tensione di 64 776 V, sospetta
> subito l'ordine dei byte.

## 1.7 Numeri ancora più grandi: 32 bit e l'ordine delle parole

Un contatore di energia arriva facilmente a milioni di wattora, oltre i 65 535 di un registro.
Si usano allora **due registri**, cioè 32 bit, che arrivano a circa 4,29 miliardi.

> valore = primo registro × 65 536 + secondo registro (se la parola alta viene prima)

Qui nasce un secondo problema di ordine, stavolta tra **parole**: alcuni dispositivi mettono
prima la parola alta, altri prima quella bassa (*word swap*).

> **Esempio**
> Un contatore segna 1 234 567 Wh = 0x0012D687. Le due parole sono 0x0012 = 18 e
> 0xD687 = 54 919.
> Con la parola alta per prima, il dispositivo invia `[18, 54919]` → 18 × 65 536 + 54 919 = 1 234 567. ✔
> Se invece il dispositivo usa l'ordine inverso e tu non lo sai, leggi
> 54 919 × 65 536 + 18 = **3 599 171 602 Wh**, un valore assurdo.

## 1.8 I numeri negativi: il complemento a due

Alcune grandezze possono essere negative: la potenza reattiva, una temperatura d'inverno,
la potenza di una batteria che si sta caricando. Come si scrive un numero negativo con soli 0 e 1?

Il metodo universale si chiama **complemento a due**. Non serve conoscerne la teoria: basta
la regola pratica per 16 bit.

> Se il valore letto è **minore di 32 768** è positivo e vale quello che leggi.
> Se è **32 768 o più**, è negativo e vale **valore letto − 65 536**.

Così un registro "con segno" (*signed*, indicato come `int16`) va da −32 768 a +32 767, mentre
uno "senza segno" (*unsigned*, `uint16`) va da 0 a 65 535. **Gli stessi 16 bit** possono quindi
significare due numeri diversi: la specifica del dispositivo ti dice quale interpretazione usare.

> **Esempio**
> Leggi il registro `FF FE` = 65 534.
> Se è `uint16`, vale 65 534. Se è `int16`, vale 65 534 − 65 536 = **−2**.

## 1.9 I numeri con la virgola: il formato float

Molti contatori e alcuni protocolli usano il formato **float** (virgola mobile, standard
IEEE 754): 32 bit che rappresentano un numero con la virgola, come in notazione scientifica.
La sua struttura interna è complessa, ma non devi decifrarla a mano. Ti basta sapere che
occupa 4 byte (due registri), che anche per lui conta l'ordine dei byte e delle parole, e
riconoscerne qualche valore.

> **Esempio**
> 230,0 in float è `43 66 00 00`; 50,0 è `42 48 00 00`. In un protocollo little-endian
> come IEC 104, 50,0 viaggia come `00 00 48 42`.

Molti protocolli preferiscono usare interi con un **fattore di scala**: invece di inviare
230,1 inviano 2301 e dicono, in un'altra parte del messaggio, "dividi per 10". Lo vedremo in
dettaglio con SunSpec nel capitolo 6.

## 1.10 I testi: il codice ASCII

Anche le lettere sono numeri. Il codice **ASCII** assegna a ogni carattere un byte: `A` = 0x41,
`B` = 0x42, `a` = 0x61, la cifra `0` = 0x30, lo spazio = 0x20. Un testo è una sequenza di byte;
un registro da 16 bit contiene due caratteri.

> **Esempio**
> I byte `53 75 6E 53` sono le lettere **S u n S**: è il "marchio" con cui un inverter
> dichiara di seguire lo standard SunSpec (capitolo 6).

## 1.11 Valori speciali

Spesso un dispositivo non misura una certa grandezza ma deve comunque riempire il registro
corrispondente. Si usa allora un valore convenzionale che significa **"non disponibile"**: per
esempio 0xFFFF (65 535) o 0x8000 (32 768). Un buon software lo riconosce e mostra "n/d"; un
cattivo software mostra "65 535 W" sul grafico.

## Riepilogo

- Un **bit** vale 0 o 1; un **byte** sono 8 bit (0–255); un **registro** Modbus sono 16 bit (0–65 535).
- L'**esadecimale** scrive ogni byte con due cifre da 0 a F; si usa perché è compatto e corrisponde esattamente ai bit.
- Valore di due byte = byte alto × 256 + byte basso; di due registri = registro alto × 65 536 + registro basso.
- **Big-endian** = prima il byte alto (Modbus); **little-endian** = prima il basso (IEC 104, CRC).
- Gli stessi bit si possono leggere come **con segno** o **senza segno**: lo decide la specifica.
- Testi in **ASCII**, numeri con virgola in **float** o come interi con **fattore di scala**.

## Domande di verifica

**1.** Quanto vale in decimale il byte `0x64`?

<details markdown="1">
<summary>Risposta</summary>

6 × 16 + 4 = **100**.

</details>

**2.** Un registro contiene i byte `00 32`. Quanto vale?

<details markdown="1">
<summary>Risposta</summary>

0 × 256 + 0x32 = **50**.

</details>

**3.** Un inverter invia la potenza come `int16` e tu leggi 65 036. Che potenza sta indicando? Che cosa potrebbe significare fisicamente?

<details markdown="1">
<summary>Risposta</summary>

È ≥ 32 768, quindi è negativa: 65 036 − 65 536 = **−500**. Un valore negativo può indicare
che il dispositivo sta **assorbendo** potenza invece di erogarla: per esempio un inverter con
batteria che si sta caricando dalla rete, o i consumi notturni dell'inverter stesso.

</details>

**4.** Perché un errore nell'ordine dei byte è più pericoloso di un cavo scollegato?

<details markdown="1">
<summary>Risposta</summary>

Con un cavo scollegato non arriva nulla e il sistema se ne accorge subito. Con l'ordine dei
byte sbagliato arrivano numeri **validi ma sbagliati**, che possono finire nei grafici, nei
report e perfino nelle regolazioni senza che nessuno se ne accorga.

</details>

**5.** Converti 40 000 in esadecimale.

<details markdown="1">
<summary>Risposta</summary>

40 000 ÷ 16 = 2500 resto 0; 2500 ÷ 16 = 156 resto 4; 156 ÷ 16 = 9 resto 12 (C); 9 ÷ 16 = 0 resto 9.
Dal basso: **0x9C40**. Infatti in un messaggio Modbus l'indirizzo 40 000 compare come `9C 40`.

</details>
