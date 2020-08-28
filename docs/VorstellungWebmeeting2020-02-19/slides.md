---
title: Webmeeting 19.02.2020 (inovex)
subtitle: Problematik Kommunikations / Wo läuft was?
author: Jan Unterbrink
date: 19.02.2020
office: Karlsruhe
---

# Kommunikations Problematik
- Resilience der Daten muss gegeben sein (besonders wichtig in der Kommunikation mit der Blockchain)
- Konsistenz der Daten
- Sicherheit in der Kommunikation (inklusive Akzeptanz von Gefahren)
- Blockchain als persistente Wahrheit?

# Sicherstellung der Resilience / Konsistenz
## HTTP Post
- Wiederholung der Nachricht bis die Verbindung erfolgreich war
- Was passiert bei Absturz des Clients?

## HTTP Get
- Unterdrückung von Nachrichten (Server verwaltet Diff)
- Datenleck

## Kafka / MQTT
- hohe zusätzliche Komplexität
- Datenleck über Datenspeicherung
- Unterdrückung von Nachrichten möglich

## Websockets
- zusätzliche Komplexität

# Wo läuft was?
- Bedrohungsszenarion werden unterschiedlich
- Keine Zeit auf die Umsetzung von nicht gebrauchten Komponenten investieren
- Spezielle Betrachtung von Architektur:
	- MQTT Broker (Wenn umgesetzt werden soll)
