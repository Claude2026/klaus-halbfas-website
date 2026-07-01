# klaus-halbfas.com — „Das Rätsel" Landingpage

Statische, deploybare Version der Buch-Landingpage. Aus dem React/Bundle-Entwurf in sauberes
vanilla HTML/CSS/JS umgebaut. Keine Build-Runtime nötig — einfach hochladen.

## Inhalt

```
klaus-halbfas-website/
├── index.html          ← die komplette Seite (HTML + CSS + JS inline)
├── vercel.json         ← Caching-/Security-Header für Vercel
├── assets/
│   ├── cover.jpg       ← Buchcover (122 KB)
│   ├── beach.jpg       ← Strandbild „Digitale Auszeit" (171 KB, optimiert)
│   └── author.jpg      ← Autorenfoto (82 KB, optimiert)
└── README.md
```

Gesamtgröße ca. 0,4 MB (Bilder für Web optimiert; Original-PNGs waren ~4 MB).

## Deploy auf Vercel

**Variante A – Drag & Drop:** Auf vercel.com → „Add New… Project" → den Ordner
`klaus-halbfas-website` ziehen. Fertig.

**Variante B – CLI:** Im Ordner `vercel --prod` ausführen.

Domain `klaus-halbfas.com` im Vercel-Projekt unter Settings → Domains zuweisen.

## Wichtig

- **Impressum & Datenschutz:** Der Footer verlinkt auf `/impressum.html` und `/datenschutz.html`.
  Diese beiden Dateien bitte aus dem bisherigen Stand mit hochladen (sie sind hier nicht enthalten,
  damit der bestehende rechtliche Text nicht überschrieben wird).
- **Benachrichtigen-Formular:** nutzt aktuell den kostenlosen Dienst
  [formsubmit.co](https://formsubmit.co) und schickt Eintragungen an klaus@halbfas.com.
  Beim allerersten Absenden bestätigt formsubmit die Adresse einmalig per E-Mail.
  Alternativ kann das `action`-Attribut im Formular (in `index.html`, Abschnitt „KONTAKT")
  auf einen anderen Dienst/Newsletter (z. B. Mailchimp, Brevo) geändert werden.
- **Schriften:** „Newsreader" wird via Google Fonts geladen.

## Funktionen

Countdown (360 h, live), Scroll-Reveal-Animationen, Cover-Tilt im Hero,
ausklappbare Leseprobe, Reichhaltige SEO-/Open-Graph-Meta-Tags und schema.org-Buchdaten.
