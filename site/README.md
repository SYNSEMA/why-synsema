# The site: why.synsema.dev

Generated and served by Synsema. `build.syn` writes a static site to `site/dist/` (not committed): one home page and one page per case for every language, SVG charts, a 1200×630 Open Graph card per page for X and LinkedIn, `sitemap.xml` and `robots.txt`. English first, Spanish second.

```bash
synsema run   site/build.syn        # → site/dist/
synsema serve site/serve.syn        # → http://localhost:8120
```

The build reads code excerpts from `cases/` between text markers (`desde` / `hasta` in each case file). If a marker disappears, the build fails naming the file instead of publishing a stale excerpt.

## Deploy

1. `base_url` in `content/ui.json` must be the final URL (Open Graph cards and the sitemap use absolute URLs). Rebuild.
2. **With Synsema**, on a server the subdomain points to (DNS A/AAAA), with ports 80 and 443 open:
   ```bash
   synsema serve site/serve.syn --port 443 --domain why.synsema.dev --tls-auto you@example.com
   ```
   `--tls-auto` gets and renews the Let's Encrypt certificate. The same file serves locally and in production; only the flags change.
3. **Or any static host** (Cloudflare Pages, Netlify, GitHub Pages): upload `site/dist/` as is.
4. **Behind an existing edge** (how why.synsema.dev runs): copy `site/serve.syn` and `site/dist/` to the server, run `synsema serve site/serve.syn --port 8120 --bind 127.0.0.1 --trust-proxy 127.0.0.1` as a service, and let the reverse proxy in front terminate TLS and forward the host to it. To update: rebuild locally and copy `site/dist/` again; the static mounts pick up the new files without a restart.
5. Check the cards before announcing: LinkedIn Post Inspector and an X post preview with the public URL.

## Add a case

1. Copy a file in `content/cases/` with the next number (`06-something.json`).
2. Fill `id` (the URL: `/en/cases/<id>/`), `orden`, `fuente` (its folder in `cases/`), `grafico`, the `en` and `es` blocks, `codigo` (file + markers) and `reproducir`.
3. `synsema run site/build.syn`. Home page, top scoreboard, case navigation, cards and sitemap update by themselves.

Chart types (`grafico.tipo`): `barras` (vertical, with `max`), `barras_h` (horizontal, with `unidad`), `waffle` (one square per unit), `puntos` (n of `total`), `donas` (fraction of `total`). In `datos`, `synsema: true` marks the series drawn in cobalt; the rest is graphite.

Table cells: `+|text` (good, ✓), `-|text` (bad, ✗), `~|text` (neutral). State always comes with an icon and text, never color alone.

## Add a language

1. Add its code to `idiomas` in `content/ui.json` and a block in `textos` with the same keys.
2. Add that language's block to every case, plus `grafico.datos[].etiqueta` and `codigo[].titulo/nota`.
3. Rebuild. Pages appear under `/<code>/` with their `hreflang` links.

## Design

- Home page as an evidence room: a dark band with the thesis and the five numbers, then one band per case with its number and chart.
- Synsema in cobalt, the usual way in graphite. Red and green only for states, always with an icon.
- Charts are SVG generated at build time: they load instantly, get indexed and need no JavaScript. The PNG cards reuse the same SVG with a fixed color sheet.
- Fonts are self-hosted: Unbounded and IBM Plex, both under the SIL Open Font License (`fonts/OFL-*.txt`).
