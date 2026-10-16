# klaus-halbfas.com

Persönliche Website von Klaus Halbfas — Operations-Leader & Autor.

- `index.html` — Profil-Startseite
- `das-raetsel.html` — Buchseite „Das Rätsel" (erreichbar unter /das-raetsel)
- `blitztext.html` — Diktier-Werkzeug „Blitztext" (erreichbar unter /blitztext): Sprache zu Text, optional geglättet und übersetzt (DE ↔ EN)
- `api/process.js` — Vercel-Funktion für Glätten/Übersetzen über die Claude-API (braucht `ANTHROPIC_API_KEY` in den Vercel-Umgebungsvariablen)
- `impressum.html`, `datenschutz.html`
- `assets/` — Bilder und lokal gehostete Schriften (keine externen Requests)
- `vercel.json` — Clean URLs + Security-Header

Statische Seite, kein Build nötig (nur `api/` nutzt npm-Abhängigkeiten, die Vercel selbst installiert). Deploy via Vercel (GitHub-Integration).
