# Appendice A — Glossario

| Termine | Significato | Capitolo |
|---|---|---|
| **ADU** | Il messaggio Modbus completo: "busta" più PDU | 5 |
| **Anello chiuso** | Regolazione che misura il risultato e corregge il comando continuamente | 8 |
| **API** | Interfaccia con cui un programma mette dati e funzioni a disposizione di altri programmi | 7 |
| **APDU** | Il messaggio IEC 104 completo, che inizia con il byte 68 | 9 |
| **ARERA** | Autorità di Regolazione per Energia Reti e Ambiente | 11 |
| **ASCII** | Codice che associa un byte a ogni carattere | 1 |
| **Banda morta** (*deadband*) | Variazione minima che fa inviare una misura | 9, 10 |
| **Baud** | Velocità di una linea seriale, circa i bit al secondo | 3 |
| **Big-endian** | Ordine dei byte con il byte alto per primo (Modbus) | 1 |
| **Bit, byte** | Cifra binaria (0/1); gruppo di 8 bit (0–255) | 1 |
| **Broker** | Server MQTT che riceve e smista i messaggi | 7 |
| **Bus** | Linea di comunicazione condivisa da più dispositivi | 3 |
| **CCI** | Controllore Centrale di Impianto previsto dalla CEI 0-16 (Allegato O) | 11 |
| **CEI 0-16 / 0-21** | Norme di connessione alle reti in MT/AT e in BT | 11 |
| **Client / server** | Chi apre la connessione e chiede / chi attende e risponde | 3 |
| **Codice funzione** (FC) | Primo byte della PDU Modbus: dice l'operazione richiesta | 4 |
| **Complemento a due** | Metodo per rappresentare i numeri negativi | 1 |
| **cos φ** | Fattore di potenza: rapporto tra potenza attiva e apparente | 2 |
| **CP56Time2a** | Formato di data e ora al millisecondo usato in IEC 104 | 9 |
| **CRC** | Codice di controllo che rivela errori di trasmissione in Modbus RTU | 5 |
| **CSV** | Tabella di testo con valori separati da virgole o punti e virgola | 7 |
| **Datalogger** | Dispositivo che raccoglie i dati dell'impianto e li invia al portale | 7 |
| **Discovery** | Ricerca automatica dei modelli SunSpec presenti in un dispositivo | 6 |
| **DSO / TSO** | Distributore della rete locale / gestore della trasmissione (Terna) | 2 |
| **Eccezione** | Risposta Modbus di rifiuto: codice funzione + 0x80 e codice d'errore | 4 |
| **Elenco segnali** | Documento che assegna un significato a ogni IOA in IEC 104 | 9 |
| **Esadecimale** | Notazione in base 16 (0–9, A–F); un byte = due cifre | 1 |
| **Fattore di scala** (SF) | Potenza di 10 per cui moltiplicare un valore SunSpec | 6 |
| **Float** | Formato a 32 bit per i numeri con la virgola (IEEE 754) | 1 |
| **Gateway** | Dispositivo che traduce tra due protocolli o reti, per esempio Modbus TCP e RTU | 5 |
| **GOOSE** | Messaggio IEC 61850 veloce inviato su Ethernet a più dispositivi | 10 |
| **IED** | Dispositivo elettronico intelligente nel linguaggio IEC 61850 | 10 |
| **Indirizzo comune** (CA) | Indirizzo della stazione in IEC 104 | 9 |
| **Indirizzo IP** | Numero che identifica un dispositivo in una rete, come 192.168.1.20 | 3 |
| **Interrogazione generale** | Richiesta dello stato completo di tutti i dati di una stazione | 9 |
| **IOA** | Indirizzo di un singolo dato in IEC 104 | 9 |
| **JSON** | Formato di testo per dati strutturati, con coppie nome: valore | 7 |
| **Little-endian** | Ordine dei byte con il byte basso per primo (IEC 104, CRC) | 1 |
| **Mappa dei registri** | Documento che dice cosa contiene ogni registro di un dispositivo | 4 |
| **Master / slave** | In Modbus: chi interroga / chi risponde | 4 |
| **MBAP** | Intestazione di 7 byte di Modbus TCP | 5 |
| **MMS** | Protocollo client-server di IEC 61850 su TCP, porta 102 | 10 |
| **Modello** (SunSpec) | Blocco di registri con ID e lunghezza, come il 103 per l'inverter trifase | 6 |
| **MPPT** | Circuito dell'inverter che cerca il punto di massima potenza dei moduli | 2 |
| **MQTT** | Protocollo leggero a pubblicazione e iscrizione per l'invio di dati | 7 |
| **Nodo logico** | Funzione elementare nel modello IEC 61850, come MMXU (misure) | 10 |
| **PDU** | Il contenuto di un messaggio Modbus: codice funzione + dati | 4 |
| **Polling** | Interrogazione periodica di un dispositivo | 3 |
| **Porta** | Numero che identifica un servizio su un dispositivo in rete, come 502 per Modbus | 3 |
| **POI** | Punto di connessione tra impianto e rete | 2 |
| **Potenza attiva / reattiva / apparente** | P in W; Q in var; S in VA, con S² = P² + Q² | 2 |
| **PPC** | Controllore d'impianto (*Power Plant Controller*) | 8 |
| **PR** | *Performance Ratio*: energia prodotta rispetto a quella attesa con il sole misurato | 7 |
| **Qualità** (di un dato) | Indicatori che dicono se un dato è valido, aggiornato, sostituito | 9, 10 |
| **Registro** | Casella da 16 bit nel modello dati di Modbus | 4 |
| **Report** | Invio automatico di dati da un server IEC 61850 a un client | 10 |
| **REST** | Stile di API basato su richieste HTTP a indirizzi che descrivono le risorse | 7 |
| **RS-485** | Standard seriale differenziale a due fili, su bus | 3 |
| **SCL** | Linguaggio XML dei file di configurazione IEC 61850 (ICD, CID, SCD) | 10 |
| **Select before operate** | Comando in due fasi, prima seleziona e poi esegui | 9, 10 |
| **SPI / SPG** | Sistema di Protezione di Interfaccia / Generale | 2 |
| **Store and forward** | Memorizzare i dati in locale e inviarli quando la connessione torna | 7 |
| **SunSpec** | Standard che definisce mappe di registri comuni per i dispositivi delle rinnovabili | 6 |
| **TCP** | Protocollo che crea connessioni affidabili su rete IP | 3 |
| **Tempo di ritorno** | Tempo dopo cui un comando non rinnovato decade (*revert timeout*) | 6, 8 |
| **Timeout** | Tempo massimo di attesa di una risposta | 4 |
| **Unit ID** | Indirizzo dello slave in Modbus TCP, usato dai gateway | 5 |
| **UTC** | Tempo universale coordinato, senza ora legale | 7 |
| **VPN** | Collegamento cifrato che rende sicuro l'accesso remoto | 3 |
| **Watchdog** | Meccanismo che porta il sistema in uno stato sicuro se manca un segnale atteso | 6, 8 |

## Per approfondire

**Specifiche e norme**

- Modbus Organization: *Modbus Application Protocol Specification* e *Modbus over Serial Line* (gratuite, modbus.org).
- SunSpec Alliance: specifiche e modelli SunSpec (gratuiti, sunspec.org).
- IEC 60870-5-104, serie IEC 61850 (inclusa la parte 7-420), IEC 62351: a pagamento sul sito IEC. Molti produttori pubblicano guide introduttive gratuite.
- MQTT: specifiche OASIS (mqtt.org).

**Italia**

- Norma CEI 0-16 con le varianti, Allegati O e T, foglio interpretativo IS1:2023-07 (ceinorme.it).
- Delibere ARERA 540/2021/R/eel, 730/2022/R/eel, 385/2025/R/eel (arera.it).
- Codice di Rete di Terna (terna.it).

**Strumenti per esercitarsi**

- Wireshark: analizza Modbus TCP, IEC 104, MMS e GOOSE.
- Client Modbus da computer, come QModMaster o Modbus Poll.
- Librerie: pymodbus, pySunSpec2, lib60870, libiec61850.
- Un convertitore USB–RS-485 e un contatore Modbus economico per provare un bus vero.
