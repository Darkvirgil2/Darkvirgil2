# Capitolo 6 — SunSpec: dare un significato ai registri

**Cosa imparerai:** perché le mappe dei registri dei produttori sono un problema; come
SunSpec organizza i dati in "modelli"; come un software scopre da solo i modelli presenti;
come funzionano i fattori di scala; come si leggono le misure di un inverter e come gli si
dà un comando.

## 6.1 Il problema: ogni produttore la sua mappa

Nel capitolo 4 abbiamo visto che Modbus non dice cosa c'è dentro i registri. Ogni produttore
pubblica la sua mappa, e le mappe sono tutte diverse. La potenza attiva può essere:

- per il produttore A, nel registro 30775, intero a 32 bit, in watt;
- per il produttore B, nel registro 40084, intero a 16 bit con fattore di scala;
- per il produttore C, nel registro 1012, numero float in kW.

Chi realizza un portale o un controllore d'impianto deve scrivere e collaudare un
"traduttore" (*driver*) per ogni modello di ogni produttore. Con decine di marche e di
versioni firmware diventa un lavoro enorme e una fonte continua di errori.

**SunSpec**, sviluppato dalla SunSpec Alliance, risolve il problema con una mappa
**standard e auto-descrittiva**: stessi dati, negli stessi punti, con le stesse regole, per
tutti i produttori che la adottano.

## 6.2 L'idea dei modelli

SunSpec divide le informazioni in blocchi chiamati **modelli**. Ogni modello raccoglie un
gruppo di dati legati tra loro e ha un numero identificativo:

- il **modello 1** contiene i dati di identificazione: produttore, modello, numero di serie;
- il **modello 103** contiene le misure di un inverter trifase;
- il **modello 123** contiene i comandi immediati, come la limitazione di potenza.

Un dispositivo espone i modelli che gli servono, uno dopo l'altro, come i capitoli di un
libro. Ogni modello inizia con due registri: il suo **numero (ID)** e la sua **lunghezza (L)**
in registri. Così chi legge sa sempre dove finisce un modello e dove inizia il successivo.

## 6.3 La mappa, dall'inizio alla fine

```
Indirizzo  Contenuto
40000      0x5375  ┐ "SunS": il marchio che dice "qui inizia una mappa SunSpec"
40001      0x6E53  ┘
40002      1          ID del primo modello (1 = Common)
40003      66         L: il modello 1 occupa 66 registri
40004–69   …          i 66 registri del modello 1
40070      103        ID del modello successivo (inverter trifase)
40071      50         L: 50 registri
40072–121  …          i 50 registri del modello 103
40122      123        ID del modello successivo (comandi)
40123      24         L: 24 registri
40124–147  …          i 24 registri del modello 123
40148      0xFFFF     ID speciale: fine della mappa
40149      0          L = 0
```

Ora riconosci l'indirizzo 40072 incontrato nei capitoli precedenti: è l'inizio dei dati del
modello 103.

## 6.4 La "scoperta" della mappa (discovery)

Un software che si collega a un inverter SunSpec sconosciuto procede così:

1. legge 2 registri all'indirizzo **40000**. Se trova `0x5375 0x6E53` ("SunS"), il dispositivo
   è SunSpec. Altrimenti prova gli indirizzi alternativi ammessi dallo standard, **0** e **50000**;
2. legge i 2 registri successivi: ID e lunghezza del primo modello;
3. salta in avanti di L registri e legge ID e lunghezza del modello seguente;
4. ripete finché trova l'ID 0xFFFF.

Alla fine sa quali modelli ci sono e a che indirizzo inizia ciascuno, senza aver consultato
nessun manuale.

> **Attenzione**
> La **posizione di un modello non è fissa**: dipende da quali modelli lo precedono. In un
> inverter il modello 103 può iniziare a 40072, in un altro a 40150. Fissa invece è la
> posizione dei dati **all'interno** del modello: la potenza è sempre al 13° registro del
> modello 103. Per questo si fa sempre la discovery invece di usare indirizzi "copiati".

## 6.5 Il fattore di scala

SunSpec rappresenta quasi tutte le misure come **interi a 16 bit**. Ma come si scrive 49,99 Hz
con un intero? Si scrive 4999 e si indica a parte che va diviso per 100. Questo "a parte" è il
**fattore di scala** (*scale factor*, SF): un intero con segno che dice per quale potenza di
dieci moltiplicare il valore.

> valore reale = valore letto × 10^SF

| SF | Significa | Esempio |
|---|---|---|
| −2 | dividi per 100 | 4999 → 49,99 Hz |
| −1 | dividi per 10 | 2301 → 230,1 V |
| 0 | lascia com'è | 18 500 → 18 500 W |
| 1 | moltiplica per 10 | 4523 → 45 230 W |

Perché non usare sempre lo stesso fattore? Perché un registro a 16 bit arriva al massimo a
32 767 (con segno). Un inverter da 20 kW può scrivere la potenza in watt (SF = 0), uno da
60 kW no: deve usare le decine di watt (SF = 1).

Più misure possono condividere lo stesso fattore di scala: le tre correnti di fase e la
corrente totale usano tutte `A_SF`; le sei tensioni usano `V_SF`.

> **Esempio**
> Nel modello 103 leggi: PhVphA = 2301, V_SF = 65 535.
> V_SF è un intero con segno: 65 535 − 65 536 = −1. Quindi PhVphA = 2301 × 10⁻¹ = **230,1 V**.

> **Attenzione**
> Leggi sempre il valore e il suo fattore di scala **nella stessa richiesta**. Alcuni
> dispositivi cambiano il fattore di scala mentre lavorano: combinare un valore nuovo con un
> fattore vecchio dà un numero 10 volte più grande o più piccolo.

## 6.6 Valori "non implementati"

Se un inverter non misura una grandezza, per esempio non ha un sensore di temperatura del
trasformatore, deve comunque riempire il registro. SunSpec stabilisce dei valori convenzionali
che significano **"non disponibile"**:

| Tipo | Valore "non implementato" |
|---|---|
| intero senza segno (uint16), enumerazione | 0xFFFF |
| intero con segno (int16), fattore di scala | 0x8000 |
| contatore a 32 bit (acc32) | 0 |

Un buon portale li mostra come "n/d" e non come 65 535 °C.

## 6.7 I modelli principali

| Modelli | Contenuto |
|---|---|
| 1 | **Common**: produttore, modello, opzioni, versione firmware, numero di serie, indirizzo |
| 101, 102, 103 | **Inverter** monofase, bifase, trifase, con interi e fattori di scala |
| 111, 112, 113 | come sopra, ma con valori float |
| 120 | **dati di targa**: potenza nominale e capacità |
| 121 | **impostazioni di base**: per esempio la potenza massima `WMax` |
| 122 | stato esteso |
| 123 | **comandi immediati**: connessione, limitazione di potenza, cos φ, potenza reattiva |
| 124 | accumulo (batterie) |
| 126 e seguenti | funzioni di rete a curva, come Volt-VAr e Freq-Watt |
| 160 | **MPPT multipli**: tensione, corrente e potenza di ogni ingresso DC |
| 201–204, 211–214 | **contatori** monofase e trifase |
| 302, 303, 307 | **sensori meteo**: irraggiamento, temperatura dei moduli, stazione meteo |
| 701 e seguenti | nuova famiglia di modelli per le risorse distribuite (standard IEEE 1547-2018) |
| 64000–65535 | modelli **proprietari** del singolo produttore |

Le definizioni complete sono pubblicate gratuitamente dalla SunSpec Alliance.

## 6.8 Il modello 103 da vicino

È il modello che leggerai più spesso. Le posizioni sono contate dall'inizio dei dati, cioè
subito dopo ID e L:

| Posizione | Nome | Significato |
|---|---|---|
| 0 | A | corrente AC totale |
| 1–3 | AphA, AphB, AphC | correnti delle tre fasi |
| 4 | A_SF | fattore di scala delle correnti |
| 5–7 | PPVphAB, PPVphBC, PPVphCA | tensioni concatenate (tra fase e fase) |
| 8–10 | PhVphA, PhVphB, PhVphC | tensioni di fase (tra fase e neutro) |
| 11 | V_SF | fattore di scala delle tensioni |
| **12** | **W** | **potenza attiva** (con segno) |
| 13 | W_SF | fattore di scala della potenza |
| 14, 15 | Hz, Hz_SF | frequenza |
| 16–21 | VA, VAr, PF con i loro SF | potenza apparente, reattiva, fattore di potenza |
| **22–23** | **WH** | **energia prodotta**, contatore a 32 bit |
| 24 | WH_SF | fattore di scala dell'energia |
| 25–30 | DCA, DCV, DCW con i loro SF | corrente, tensione e potenza lato DC |
| 31–35 | TmpCab, TmpSnk, TmpTrns, TmpOt, Tmp_SF | temperature |
| **36** | **St** | **stato di funzionamento** |
| 37 | StVnd | stato secondo il produttore |
| 38–39 | Evt1 | allarmi standard, un bit per ogni tipo di allarme |
| 40–49 | Evt2, EvtVnd1–4 | altri allarmi |

Lo **stato** `St` è un'enumerazione, cioè un numero che corrisponde a una situazione:

| St | Stato | Significato |
|---|---|---|
| 1 | OFF | spento |
| 2 | SLEEPING | in attesa, di solito di notte |
| 3 | STARTING | in avvio |
| 4 | MPPT | produce normalmente, alla massima potenza disponibile |
| 5 | THROTTLED | produce ma è **limitato** da un comando |
| 6 | SHUTTING_DOWN | in spegnimento |
| 7 | FAULT | guasto |
| 8 | STANDBY | pronto ma non connesso |

> **Esempio**
> La potenza è nella posizione 12: indirizzo 40072 + 12 = **40084**. Nella risposta alla
> lettura dei 50 registri, i suoi due byte sono il 25° e il 26° byte di dati. Se valgono
> `48 44`, il valore è 0x4844 = 18 500; con W_SF = 0 la potenza è 18 500 W.

## 6.9 Dare un comando: la limitazione di potenza

Il comando più usato in assoluto è la **limitazione della potenza attiva**: «non produrre più
del 40% della tua potenza massima». Con il modello 123 si fa così:

1. si scrive `WMaxLimPct`, la percentuale, tenendo conto del suo fattore di scala: con SF −2,
   il 40% si scrive 4000;
2. facoltativamente si impostano `WMaxLimPct_RmpTms`, il tempo di rampa per arrivare al nuovo
   valore, e `WMaxLimPct_RvrtTms`, il **tempo di ritorno**;
3. si scrive `WMaxLim_Ena = 1` per attivare il limite.

Conviene scrivere tutti questi registri, che sono consecutivi, con un'unica scrittura multipla
(codice 16), così il comando arriva completo in un solo messaggio.

### Il tempo di ritorno: una rete di sicurezza

Il **tempo di ritorno** (*revert timeout*) è il meccanismo di sicurezza più importante del
controllo. Se lo imposti a 60 secondi, l'inverter mantiene il limite per 60 secondi; se in
quel tempo nessuno rinnova il comando, il limite **decade da solo** e l'inverter torna al
funzionamento normale.

Perché è importante? Immagina che il controllore d'impianto si guasti mentre ha limitato gli
inverter al 10%. Senza tempo di ritorno l'impianto resterebbe al 10% per giorni, finché qualcuno
non se ne accorge. Con il tempo di ritorno, dopo un minuto torna a produrre. Lo stesso principio,
chiamato **watchdog** ("cane da guardia"), si ritrova in tutti i sistemi di controllo seri
(capitolo 8).

## 6.10 SunSpec nella realtà

- Molti inverter offrono **sia** la mappa SunSpec **sia** una mappa proprietaria, a volte più
  ricca. A volte SunSpec va attivato dal menu o dall'app.
- Non tutti implementano SunSpec in modo perfetto: modelli incompleti, fattori di scala insoliti,
  Unit ID particolari. Esiste una certificazione che riduce, ma non elimina, le sorprese.
- I prodotti più recenti adottano i modelli 7xx; in campo trovi ancora soprattutto 1, 103, 120,
  121, 123 e 160.

## Riepilogo

- SunSpec dà una **mappa standard** sopra Modbus, organizzata in **modelli** (ID + lunghezza + dati).
- La mappa inizia con **"SunS"** a 40000 (o 0, o 50000) e finisce con l'ID 0xFFFF.
- La **discovery** trova da sola i modelli; la posizione dei modelli varia, quella dei dati dentro il modello no.
- **Valore reale = valore × 10^SF**; leggi valore e SF insieme.
- Valori convenzionali indicano "non implementato".
- **Modello 103** = misure dell'inverter; **modello 123** = comandi, con il **tempo di ritorno** come sicurezza.

> **Prova**
> Nel [laboratorio Inverter SunSpec](#lab-inverter): premi «Discovery» e guarda nel registro
> dei frame le letture che percorrono la mappa; confronta i valori grezzi e quelli reali nella
> tabella; invia un limite del 30% con ritorno dopo 15 secondi e aspetta.

## Domande di verifica

**1.** Leggi Hz = 5002 e Hz_SF = 65 534. Quanto vale la frequenza?

<details markdown="1">
<summary>Risposta</summary>

Hz_SF con segno: 65 534 − 65 536 = −2. Frequenza = 5002 × 10⁻² = **50,02 Hz**.

</details>

**2.** In un inverter il marchio "SunS" è a 40000 e i modelli sono, nell'ordine: 1 (L = 66), 120 (L = 26), 103 (L = 50). A che indirizzo inizia il registro W del modello 103?

<details markdown="1">
<summary>Risposta</summary>

Modello 1: ID a 40002, dati 40004–40069. Modello 120: ID a 40070, L a 40071, dati 40072–40097.
Modello 103: ID a 40098, L a 40099, dati da **40100**. W è in posizione 12: **40112**. Ecco
perché la discovery è indispensabile: lo stesso dato si trova a 40084 in un altro inverter.

</details>

**3.** Vuoi limitare un inverter al 25% e WMaxLimPct_SF vale −2. Che numero scrivi?

<details markdown="1">
<summary>Risposta</summary>

25 / 10⁻² = **2500**.

</details>

**4.** Il registro TmpTrns contiene 0x8000. Cosa mostri sul portale?

<details markdown="1">
<summary>Risposta</summary>

"n/d" (non disponibile): 0x8000 è il valore SunSpec di "non implementato" per gli interi con
segno. Il dispositivo non ha quella misura. Mostrare −3276,8 °C sarebbe un errore.

</details>
