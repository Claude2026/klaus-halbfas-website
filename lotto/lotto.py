#!/usr/bin/env python3
"""Rechenwerkzeug des Lotto-Agenten-Teams (Lotto "6 aus 45" und EuroMillionen).

Grundsatz: Jede Kombination ist gleich wahrscheinlich. Das Werkzeug sagt keine
Zahlen vorher. Es rechnet exakte Chancen, prueft Ziehungsdaten auf Abweichungen
vom Zufall, widerlegt "heisse Zahlen" im Ruecktest und erzeugt Tipps, die
moeglichst selten von anderen gespielt werden (hoehere Quote im Gewinnfall).

Nur Standardbibliothek. Aufruf: python3 lotto/lotto.py <befehl> --help
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import re
import secrets
import sys
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from math import comb


@dataclass(frozen=True)
class Spiel:
    key: str
    name: str
    n_haupt: int      # Groesse des Zahlenfelds
    k_haupt: int      # gezogene / getippte Hauptzahlen
    n_zusatz: int     # Groesse des Zusatzfelds (0 = Zusatzzahl aus dem Hauptfeld)
    k_zusatz: int     # gezogene Zusatzzahlen bzw. Sternzahlen
    preis: float      # Preis je Tipp in Euro (Annahme, vor dem Spielen pruefen)
    raster: int       # Spalten des Tippfelds am Schein (Annahme)


def tsd(x: float) -> str:
    """Ganzzahl mit Punkt als Tausendertrennzeichen."""
    return f"{x:,.0f}".replace(",", ".")


SPIELE = {
    "lotto": Spiel("lotto", "Lotto 6 aus 45", 45, 6, 0, 1, 1.50, 6),
    "euromillionen": Spiel("euromillionen", "EuroMillionen", 50, 5, 12, 2, 2.50, 10),
}

# ---------------------------------------------------------------- Chancen


def raenge(sp: Spiel):
    """Exakte Gewinnraenge als Liste (Bezeichnung, guenstige Faelle, alle Faelle)."""
    if sp.key == "lotto":
        gesamt = comb(45, 6)
        # Tipp: 6 Zahlen. Ziehung: 6 Gewinnzahlen + 1 Zusatzzahl aus den restlichen 39.
        def faelle(richtige, zz):
            rest = 6 - richtige
            if zz:
                return comb(6, richtige) * comb(38, rest - 1) if rest >= 1 else 0
            return comb(6, richtige) * comb(38, rest)
        liste = [("6 Richtige", faelle(6, False)), ("5 + Zusatzzahl", faelle(5, True)),
                 ("5 Richtige", faelle(5, False)), ("4 + Zusatzzahl", faelle(4, True)),
                 ("4 Richtige", faelle(4, False)), ("3 + Zusatzzahl", faelle(3, True)),
                 ("3 Richtige", faelle(3, False)), ("0 + Zusatzzahl", faelle(0, True))]
        return [(b, f, gesamt) for b, f in liste]
    gesamt = comb(50, 5) * comb(12, 2)
    paare = [(5, 2), (5, 1), (5, 0), (4, 2), (4, 1), (3, 2), (4, 0),
             (2, 2), (3, 1), (3, 0), (1, 2), (2, 1), (2, 0)]
    out = []
    for h, s in paare:
        f = comb(5, h) * comb(45, 5 - h) * comb(2, s) * comb(10, 2 - s)
        out.append((f"{h} + {s} Sterne", f, gesamt))
    return out


def cmd_chancen(args):
    for sp in _spiele(args.spiel):
        rs = raenge(sp)
        gesamt = rs[0][2]
        print(f"\n{sp.name} - {tsd(gesamt)} moegliche Tipps")
        print(f"{'Rang':<18}{'Chance 1 zu':>16}{'Wahrsch.':>14}")
        summe = 0
        for bez, f, _ in rs:
            summe += f
            print(f"{bez:<18}{tsd(gesamt / f):>16}{f / gesamt:>14.8%}")
        print(f"{'irgendein Gewinn':<18}{gesamt / summe:>16.1f}{summe / gesamt:>14.4%}")


# ---------------------------------------------------------------- Daten


def lade(pfad: str, sp: Spiel):
    """Liest Ziehungen aus CSV. Je Zeile: optional Datum, dann Hauptzahlen, dann Zusatz-/Sternzahlen.

    Trennzeichen beliebig (; , Tab Leerzeichen). Zeilen ohne passende Zahl von Werten
    werden uebersprungen und gezaehlt. Rueckgabe: Liste (haupt, zusatz), aelteste zuerst
    in Dateireihenfolge.
    """
    brauch = sp.k_haupt + sp.k_zusatz
    ziehungen, verworfen = [], 0
    with open(pfad, newline="", encoding="utf-8-sig") as fh:
        for zeile in fh:
            zeile = zeile.strip()
            if not zeile:
                continue
            # Datum (2024-01-31, 31.01.2024) entfernen, dann Ganzzahlen sammeln
            ohne = re.sub(r"\d{1,4}[.\-/]\d{1,2}[.\-/]\d{1,4}", " ", zeile)
            zahlen = [int(x) for x in re.split(r"[;,\s]+", ohne) if x.isdigit()]
            if len(zahlen) != brauch:
                verworfen += 1
                continue
            haupt, zus = zahlen[:sp.k_haupt], zahlen[sp.k_haupt:]
            n_zus = sp.n_zusatz or sp.n_haupt
            ok = (len(set(haupt)) == sp.k_haupt and all(1 <= z <= sp.n_haupt for z in haupt)
                  and len(set(zus)) == sp.k_zusatz and all(1 <= z <= n_zus for z in zus)
                  and (sp.n_zusatz or not set(zus) & set(haupt)))
            if not ok:
                verworfen += 1
                continue
            ziehungen.append((tuple(sorted(haupt)), tuple(sorted(zus))))
    return ziehungen, verworfen


def _ziehe(sp: Spiel, rng):
    haupt = rng.sample(range(1, sp.n_haupt + 1), sp.k_haupt)
    if sp.n_zusatz:
        zus = rng.sample(range(1, sp.n_zusatz + 1), sp.k_zusatz)
    else:
        zus = rng.sample([z for z in range(1, sp.n_haupt + 1) if z not in haupt], sp.k_zusatz)
    return tuple(sorted(haupt)), tuple(sorted(zus))


def cmd_simuliere(args):
    """Erzeugt KUENSTLICHE Ziehungen (kein echtes Archiv) zum Testen der Auswertung."""
    sp = SPIELE[args.spiel]
    rng = random.Random(args.seed)
    w = csv.writer(sys.stdout, delimiter=";")
    for i in range(args.anzahl):
        h, z = _ziehe(sp, rng)
        w.writerow([f"SIM-{i + 1:05d}", *h, *z])


# ---------------------------------------------------------------- Statistik


def chi2_p(x: float, df: int) -> float:
    """Ueberschreitungswahrscheinlichkeit der Chi-Quadrat-Verteilung (regularisierte Gammafunktion)."""
    a, x = df / 2.0, x / 2.0
    if x <= 0:
        return 1.0
    lg = math.lgamma(a)
    if x < a + 1:  # Reihenentwicklung der unteren Gammafunktion
        term = summe = 1.0 / a
        n = a
        for _ in range(10000):
            n += 1
            term *= x / n
            summe += term
            if abs(term) < abs(summe) * 1e-15:
                break
        return max(0.0, 1.0 - summe * math.exp(-x + a * math.log(x) - lg))
    b = x + 1 - a  # Kettenbruch (Lentz) der oberen Gammafunktion
    c, d = 1e300, 1.0 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return min(1.0, h * math.exp(-x + a * math.log(x) - lg))


def haeufigkeitstest(zaehler: Counter, n: int, k: int, ziehungen: int):
    """Chi-Quadrat-Test auf Gleichverteilung bei Ziehen ohne Zuruecklegen.

    Korrekturfaktor (n-1)/(n-k), weil die k Zahlen einer Ziehung nicht unabhaengig sind.
    """
    erwartet = ziehungen * k / n
    roh = sum((zaehler.get(z, 0) - erwartet) ** 2 / erwartet for z in range(1, n + 1))
    stat = roh * (n - 1) / (n - k)
    return stat, n - 1, chi2_p(stat, n - 1), erwartet


def cmd_analyse(args):
    sp = SPIELE[args.spiel]
    zs, verworfen = lade(args.csv, sp)
    if len(zs) < 50:
        sys.exit(f"Zu wenige gueltige Ziehungen ({len(zs)}); mindestens 50 noetig.")
    t = len(zs)
    print(f"{sp.name}: {t} gueltige Ziehungen, {verworfen} Zeilen verworfen")
    haupt = Counter(z for h, _ in zs for z in h)
    stat, df, p, erw = haeufigkeitstest(haupt, sp.n_haupt, sp.k_haupt, t)
    sd = math.sqrt(t * (sp.k_haupt / sp.n_haupt) * (1 - sp.k_haupt / sp.n_haupt))
    print(f"\nHauptzahlen: erwartet je Zahl {erw:.1f} +/- {sd:.1f} (1 Standardabweichung)")
    rang = sorted(range(1, sp.n_haupt + 1), key=lambda z: -haupt.get(z, 0))
    print("  haeufigste:", ", ".join(f"{z} ({haupt[z]}x)" for z in rang[:6]))
    print("  seltenste :", ", ".join(f"{z} ({haupt.get(z, 0)}x)" for z in rang[-6:]))
    print(f"  Chi-Quadrat = {stat:.1f} bei {df} Freiheitsgraden, p = {p:.3f}")
    tests = [p]
    if sp.n_zusatz:
        stern = Counter(z for _, s in zs for z in s)
        s2, d2, p2, _ = haeufigkeitstest(stern, sp.n_zusatz, sp.k_zusatz, t)
        print(f"Sternzahlen: Chi-Quadrat = {s2:.1f} bei {d2} Freiheitsgraden, p = {p2:.3f}")
        tests.append(p2)
    # Unabhaengigkeit: Ueberschneidung aufeinanderfolgender Ziehungen
    ueber = [len(set(zs[i][0]) & set(zs[i + 1][0])) for i in range(t - 1)]
    mu = sp.k_haupt ** 2 / sp.n_haupt
    n, k = sp.n_haupt, sp.k_haupt
    var = k * (k / n) * (1 - k / n) * (n - k) / (n - 1)
    z = (sum(ueber) / len(ueber) - mu) / math.sqrt(var / len(ueber))
    pz = math.erfc(abs(z) / math.sqrt(2))
    print(f"Wiederholung zur Vorziehung: im Mittel {sum(ueber) / len(ueber):.3f} Zahlen, "
          f"erwartet {mu:.3f}, z = {z:+.2f}, p = {pz:.3f}")
    tests.append(pz)
    schwelle = 0.01 / len(tests)  # Bonferroni
    auff = [x for x in tests if x < schwelle]
    print(f"\nUrteil (Schwelle p < {schwelle:.4f} nach Bonferroni-Korrektur):")
    if auff:
        print("  AUFFAELLIG - Daten und Dateireihenfolge pruefen, bevor daraus etwas abgeleitet wird.")
    else:
        print("  Kein Hinweis auf Abweichung vom Zufall. Haeufige und seltene Zahlen liegen im")
        print("  Bereich normaler Schwankung und sagen nichts ueber die naechste Ziehung.")


def cmd_ruecktest(args):
    """Prueft 'heisse', 'kalte' und 'ueberfaellige' Zahlen gegen die Zufallserwartung."""
    sp = SPIELE[args.spiel]
    zs, _ = lade(args.csv, sp)
    start = args.anlauf
    if len(zs) <= start + 30:
        sys.exit("Zu wenige Ziehungen fuer den Ruecktest.")
    k, n = sp.k_haupt, sp.n_haupt
    treffer = {"heiss": [], "kalt": [], "ueberfaellig": []}
    zaehler, zuletzt = Counter(), {}
    for i, (h, _) in enumerate(zs):
        if i >= start:
            alle = range(1, n + 1)
            wahl = {
                "heiss": sorted(alle, key=lambda z: (-zaehler[z], z))[:k],
                "kalt": sorted(alle, key=lambda z: (zaehler[z], z))[:k],
                "ueberfaellig": sorted(alle, key=lambda z: (zuletzt.get(z, -1), z))[:k],
            }
            for name, tipp in wahl.items():
                treffer[name].append(len(set(tipp) & set(h)))
        zaehler.update(h)
        for z in h:
            zuletzt[z] = i
    mu = k * k / n
    sd = math.sqrt(k * (k / n) * (1 - k / n) * (n - k) / (n - 1))
    m = len(treffer["heiss"])
    print(f"{sp.name}: Ruecktest ueber {m} Ziehungen (Anlauf {start})")
    print(f"Zufallserwartung: {mu:.3f} richtige Hauptzahlen je Tipp")
    for name, tr in treffer.items():
        mittel = sum(tr) / m
        z = (mittel - mu) / (sd / math.sqrt(m))
        urteil = "kein Vorteil" if abs(z) < 2.58 else "auffaellig - Daten pruefen"
        print(f"  {name:<13} {mittel:.3f} im Mittel, z = {z:+.2f} -> {urteil}")


# ---------------------------------------------------------------- Tipps


def beliebtheit(haupt, sp: Spiel) -> float:
    """Heuristik: wie stark aehnelt der Tipp Mustern, die viele Menschen spielen?

    Hoeher = vermutlich oefter gespielt = Gewinn muss oefter geteilt werden.
    Gewichte sind Annahmen aus der Literatur zu Tippverhalten, nicht aus oesterreichischen
    Tippdaten geschaetzt.
    """
    h = sorted(haupt)
    k = len(h)
    s = 0.0
    geburtstag = sum(1 for z in h if z <= 31)
    s += 1.5 * max(0, geburtstag - k * 31 / sp.n_haupt)        # Geburtstagszahlen
    s += 1.0 * max(0, sum(1 for z in h if z <= 12) - 1)        # Monatszahlen
    diffs = [b - a for a, b in zip(h, h[1:])]
    if len(set(diffs)) == 1:
        s += 10                                                # arithmetische Folge
    lauf = laengster = 1
    for d in diffs:
        lauf = lauf + 1 if d == 1 else 1
        laengster = max(laengster, lauf)
    s += 2.0 * max(0, laengster - 2)                           # Zahlenreihen
    zeilen = Counter((z - 1) // sp.raster for z in h)
    spalten = Counter((z - 1) % sp.raster for z in h)
    s += 2.0 * max(0, max(zeilen.values()) - 3)                # Muster am Schein
    s += 2.0 * max(0, max(spalten.values()) - 2)
    s += 1.0 * max(0, max(Counter(z % 10 for z in h).values()) - 2)  # gleiche Endziffer
    s += 0.7 * sum(1 for z in h if z in (3, 7, 9, 11, 13, 17, 21))   # "Glueckszahlen"
    if h[-1] <= sp.n_haupt * 0.7:
        s += 1.5                                               # Feldrand unten nie genutzt
    return s


def cmd_tipps(args):
    sp = SPIELE[args.spiel]
    rng = secrets.SystemRandom()          # Betriebssystem-Zufall, nicht vorhersagbar
    gesperrt = set()
    if args.csv:
        gesperrt = {h for h, _ in lade(args.csv, sp)[0]}   # fruehere Gewinnreihen werden nachgespielt
    kand = []
    for _ in range(args.kandidaten):
        h, z = _ziehe(sp, rng)
        if h in gesperrt:
            continue
        kand.append((beliebtheit(h, sp), h, z))
    kand.sort(key=lambda x: x[0])
    pool = kand[:max(args.anzahl * 20, len(kand) // 10)]   # unbeliebtestes Zehntel
    rng.shuffle(pool)
    gewaehlt, benutzt = [], Counter()
    for _ in range(args.anzahl):                            # Tipps moeglichst ueberschneidungsarm
        bester = min(pool, key=lambda c: (sum(benutzt[x] for x in c[1]), c[0]))
        pool.remove(bester)
        gewaehlt.append(bester)
        benutzt.update(bester[1])
    median = kand[len(kand) // 2][0]
    zname = "Sterne" if sp.n_zusatz else None
    print(f"{sp.name}: {args.anzahl} Tipp(s), Einsatz {args.anzahl * sp.preis:.2f} EUR "
          f"(Preisannahme {sp.preis:.2f} EUR je Tipp)")
    for i, (score, h, z) in enumerate(gewaehlt, 1):
        zeile = "  ".join(f"{x:2d}" for x in h)
        if zname:
            zeile += "   | Sterne: " + "  ".join(f"{x:2d}" for x in z)
        print(f"  Tipp {i}: {zeile}   (Beliebtheit {score:.1f}, Median aller Tipps {median:.1f})")
    print(f"Gewinnchance je Tipp unveraendert: 1 zu {tsd(raenge(sp)[0][2])} auf den Hauptgewinn.")
    print("Der Nutzen liegt allein darin, einen Gewinn seltener teilen zu muessen.")


# ---------------------------------------------------------------- Erwartungswert


def cmd_erwartung(args):
    sp = SPIELE[args.spiel]
    preis = args.preis or sp.preis
    rs = raenge(sp)
    p_jp = rs[0][1] / rs[0][2]
    lam = args.tipps * p_jp                       # erwartete weitere Gewinner (Poisson)
    anteil = (1 - math.exp(-lam)) / lam if lam > 0 else 1.0
    ev_jp = p_jp * args.jackpot * anteil
    ev_rest = args.quote_rest * preis
    ev = ev_jp + ev_rest
    print(f"{sp.name}: Jackpot {tsd(args.jackpot)} EUR, {tsd(args.tipps)} Tipps im Umlauf")
    print(f"  Chance Hauptgewinn        1 zu {tsd(1 / p_jp)}")
    print(f"  erwarteter Anteil am Topf {anteil:.1%} (Teilen mit anderen Gewinnern)")
    print(f"  Erwartungswert Jackpot    {ev_jp:.3f} EUR")
    print(f"  Erwartungswert Rest       {ev_rest:.3f} EUR (Annahme: {args.quote_rest:.0%} des Einsatzes)")
    print(f"  Erwartungswert gesamt     {ev:.3f} EUR bei {preis:.2f} EUR Einsatz -> "
          f"{ev / preis:.1%} Rueckfluss, {ev - preis:+.2f} EUR je Tipp")
    p_kein = 1 - sum(f for _, f, _ in rs) / rs[0][2]
    print(f"  kein Gewinn               {p_kein:.1%} aller Tipps")
    if args.einsatz:
        n = int(args.einsatz // preis)
        print(f"  Budget {args.einsatz:.2f} EUR = {n} Tipp(s): Chance auf den Hauptgewinn "
              f"1 zu {tsd(1 / (1 - (1 - p_jp) ** n))}, erwarteter Verlust "
              f"{n * (preis - ev):.2f} EUR")


# ---------------------------------------------------------------- CLI


def _spiele(wahl):
    return list(SPIELE.values()) if wahl == "beide" else [SPIELE[wahl]]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="befehl", required=True)
    namen = list(SPIELE)

    a = sub.add_parser("chancen", help="exakte Gewinnchancen je Rang")
    a.add_argument("--spiel", choices=namen + ["beide"], default="beide")
    a.set_defaults(fn=cmd_chancen)

    a = sub.add_parser("analyse", help="Ziehungsarchiv auf Abweichung vom Zufall pruefen")
    a.add_argument("--spiel", choices=namen, required=True)
    a.add_argument("--csv", required=True)
    a.set_defaults(fn=cmd_analyse)

    a = sub.add_parser("ruecktest", help="heisse/kalte/ueberfaellige Zahlen gegen den Zufall testen")
    a.add_argument("--spiel", choices=namen, required=True)
    a.add_argument("--csv", required=True)
    a.add_argument("--anlauf", type=int, default=100)
    a.set_defaults(fn=cmd_ruecktest)

    a = sub.add_parser("tipps", help="selten gespielte Zufallstipps erzeugen")
    a.add_argument("--spiel", choices=namen, required=True)
    a.add_argument("--anzahl", type=int, default=2)
    a.add_argument("--kandidaten", type=int, default=20000)
    a.add_argument("--csv", help="Archiv; fruehere Gewinnreihen werden ausgeschlossen")
    a.set_defaults(fn=cmd_tipps)

    a = sub.add_parser("erwartung", help="Erwartungswert eines Tipps beim aktuellen Jackpot")
    a.add_argument("--spiel", choices=namen, required=True)
    a.add_argument("--jackpot", type=float, required=True, help="Hauptgewinn in Euro")
    a.add_argument("--tipps", type=int, required=True, help="geschaetzte Zahl abgegebener Tipps")
    a.add_argument("--preis", type=float)
    a.add_argument("--quote-rest", type=float, default=0.30,
                   help="Anteil des Einsatzes, der ueber die unteren Raenge zurueckfliesst (Annahme)")
    a.add_argument("--einsatz", type=float, help="eigenes Budget in Euro")
    a.set_defaults(fn=cmd_erwartung)

    a = sub.add_parser("simuliere", help="kuenstliche Ziehungen als CSV (nur zum Testen)")
    a.add_argument("--spiel", choices=namen, required=True)
    a.add_argument("--anzahl", type=int, default=2000)
    a.add_argument("--seed", type=int, default=1)
    a.set_defaults(fn=cmd_simuliere)

    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
