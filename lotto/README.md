# Lotto-Team

Agenten-Team für Lotto „6 aus 45" und EuroMillionen. Start in Claude Code: `/lotto-team beide 10` (Spiel, Budget in Euro).

**Was das Team nicht kann:** Gewinnzahlen vorhersagen. Jede Kombination ist gleich wahrscheinlich, frühere Ziehungen sagen nichts über die nächste.
**Was es kann:** exakt rechnen, Archive auf Abweichungen vom Zufall prüfen, Vorhersage-Ideen im Rücktest widerlegen und Tipps erzeugen, die selten gespielt werden – damit ein Gewinn seltener geteilt wird.

| Agent | Aufgabe |
|---|---|
| `lotto-daten` | Ziehungsarchive, Jackpot, Preis – mit Quelle |
| `lotto-statistiker` | Zufallstests, Rücktest „heiß / kalt / überfällig" |
| `lotto-quant` | Chancen, Erwartungswert, Budgetwirkung |
| `lotto-tippstratege` | selten gespielte Zufallstipps im Budget |
| `lotto-pruefer` | unabhängige Schlussprüfung |

Die Agenten liegen in `.claude/agents/`, der Ablauf in `.claude/commands/lotto-team.md`.

## Rechenwerkzeug

```
python3 lotto/lotto.py chancen
python3 lotto/lotto.py analyse   --spiel lotto --csv lotto/daten/lotto.csv
python3 lotto/lotto.py ruecktest --spiel lotto --csv lotto/daten/lotto.csv
python3 lotto/lotto.py tipps     --spiel euromillionen --anzahl 2
python3 lotto/lotto.py erwartung --spiel euromillionen --jackpot 250000000 --tipps 60000000 --einsatz 10
```

Nur Python-Standardbibliothek. Archivformat: siehe `daten/README.md`.

## Annahmen im Werkzeug

- Tipp-Preis: 1,50 € (Lotto), 2,50 € (EuroMillionen) – vor dem Spielen prüfen, mit `--preis` überschreibbar.
- Rückfluss der unteren Gewinnränge: 30 % des Einsatzes (`--quote-rest`).
- Beliebtheitswertung der Tipps: Heuristik (Geburtstagszahlen, Reihen, Muster am Schein, Glückszahlen), nicht aus österreichischen Tippdaten geschätzt.

`.vercelignore` hält `lotto/` und `.claude/` aus dem Website-Deployment heraus.

Glücksspiel kann süchtig machen. Nur mit festem Budget spielen, das man verlieren kann. Hilfe in Österreich: Spielsuchthilfe, www.spielsuchthilfe.at.
