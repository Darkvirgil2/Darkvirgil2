# Glossario e risorse

## Glossario

| Termine | Significato |
|---|---|
| **ADU / PDU** | Application/Protocol Data Unit: il frame completo / la parte "funzione + dati" |
| **APCI / ASDU** | In IEC 104: intestazione di controllo / unità dati applicativa |
| **CCI** | Controllore Centrale di Impianto (CEI 0-16, Allegato O) |
| **CID / ICD / SCD** | File SCL IEC 61850: configurato / capacità / sottostazione |
| **Common Address** | IEC 104: indirizzo della stazione |
| **Deadband** | Variazione minima che fa scattare l'invio spontaneo di una misura |
| **DSO / TSO** | Distribution / Transmission System Operator (distributore / Terna) |
| **GOOSE** | Messaggi IEC 61850 multicast veloci di livello 2 |
| **IOA** | Information Object Address (IEC 104) |
| **Logical Node** | Funzione elementare nel modello IEC 61850 (es. MMXU = misure) |
| **MBAP** | Intestazione di 7 byte di Modbus TCP |
| **MMS** | Manufacturing Message Specification: protocollo client/server di IEC 61850 |
| **MPPT** | Inseguitore del punto di massima potenza (ingresso DC dell'inverter) |
| **POI** | Point of Interconnection: punto di connessione alla rete |
| **PPC** | Power Plant Controller |
| **PR** | Performance Ratio |
| **Scale factor (SF)** | Esponente di 10 che trasforma l'intero grezzo nel valore reale (SunSpec) |
| **SPI / SPG** | Sistema di Protezione di Interfaccia / Generale |
| **Unit ID** | Indirizzo dello slave in Modbus TCP (fondamentale con i gateway) |
| **Watchdog / revert timeout** | Ritorno automatico a uno stato sicuro se i comandi non vengono rinnovati |

## Risorse per approfondire

**Standard e specifiche**
- Modbus Organization — *Modbus Application Protocol Specification* e *Modbus over Serial Line* (gratuite): modbus.org
- SunSpec Alliance — specifiche SunSpec Modbus e modelli (repository GitHub `sunspec/models`), libreria `pySunSpec2`: sunspec.org
- IEC 61850 (serie), IEC 61850-7-420 (risorse energetiche distribuite), IEC 60870-5-101/104, IEC 62351 (sicurezza): a pagamento su webstore.iec.ch; molte guide introduttive gratuite sono pubblicate dai produttori di IED e gateway
- MQTT 3.1.1 / 5.0: mqtt.org e OASIS

**Italia**
- Norma **CEI 0-16** e varianti (in particolare Allegati O, T, U) — CEI (ceinorme.it); il CEI ha pubblicato anche un **foglio interpretativo** (IS1:2023-07) con risposte alle domande sugli Allegati O e T
- Delibere **ARERA** 540/2021/R/eel, 730/2022/R/eel, 385/2025/R/eel — arera.it
- **Codice di Rete Terna** e allegati — terna.it

**Strumenti**
- Wireshark (dissector Modbus, IEC 104, MMS, GOOSE)
- Client Modbus grafici (es. QModMaster, Modbus Poll), simulatori (es. diagslave, ModRSsim2)
- Librerie: pymodbus, libmodbus, lib60870 / libiec61850 (MZ Automation), Eclipse Paho (MQTT)
