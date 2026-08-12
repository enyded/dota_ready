# ReAccept — landing page

Static site for the ReAccept landing page. Plain HTML/CSS, no build step, no JS framework.
Content and structure follow the "Landing page" section of `docs/PHASE10_PRODUCTION_PLAN.md` in
the main `dota` repo.

This directory is its own git repository (remote: `https://github.com/enyded/dota_ready.git`),
separate from the main monorepo — it's excluded from the monorepo's history via `.gitignore`
(`/landing/`).

## Preview locally

```powershell
cd landing
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Screenshots and localization

Screenshots live per-locale under `assets/screenshots/<locale>/`, e.g. `assets/screenshots/en/`,
`assets/screenshots/ru/`. `en/` is the **default/fallback set** — every screenshot must exist
there. A locale folder only needs to contain the files that actually differ for that language
(e.g. a screenshot with visible UI text); anything missing falls back to `en/`. This mirrors the
planned app/landing localization scope in `docs/PHASE10_PRODUCTION_PLAN.md` ("Localization")
without requiring a language switcher to exist yet — right now the page only renders `en/`, but
capturing screenshots per-locale from day one avoids a re-shoot later.

Filenames must stay identical across locale folders so the fallback lookup is a pure path swap:
- `app-main.png`, `app-match-found.png`, `app-notification.png`, `app-settings.png`,
  `app-info.png`, `app-allow-bg-activity.png` — Android app screens.
- `desk-main.png`, `desk-qr.png` — Windows desktop app screens.
- `og-cover.png` — generated cover image, not a screenshot (locale-specific OG previews are a
  nice-to-have, not required).
- `android-qr-placeholder.png` — generated QR code, not a manual screenshot; points at the
  stable `ReAccept.apk` release URL.

## Still TODO before launch

- [x] **Screenshots (`en/`)** — the product owner supplied the rebranded Windows and Android
  screenshots. The generated `og-cover.png` uses the same approved ReAccept icon and copy.
- [x] **Download links** — point at the stable GitHub Release aliases `ReAccept-Setup.exe` and
  `ReAccept.apk`; the QR code encodes the same Android URL.
- [x] **Support email** — `support.d2r@gmail.com`, wired into the footer, `privacy.html`, and
  `docs/PRIVACY_POLICY.md`.
- [ ] **Privacy Policy** — `privacy.html` mirrors `docs/PRIVACY_POLICY.md`, which is still a draft
  with bracketed placeholders ([DATE], [PUBLISHER LEGAL NAME], [HOSTING AND LOGGING DETAILS],
  [PROCESSORS], [RETENTION POLICY]). Fill those in before removing `noindex` — needs real legal/ops
  input, not something to fill in generically.
- [x] **Hosting** — deploying via GitHub Pages on this repo for now (Settings → Pages → Source:
  Deploy from a branch → `main` → `/` (root) → Save), served at
  `https://re-accept.com/`. `.nojekyll` is committed so GitHub serves the static files as-is
  instead of running them through a Jekyll build. DNS is managed by Cloudflare in DNS-only mode
  for the GitHub Pages apex and `www` records; `www` redirects to the apex domain.
- [ ] **SEO flip at launch** — both HTML files carry `<meta name="robots" content="noindex, nofollow">`
  and `robots.txt` disallows everything. This is intentional pre-launch (see
  `docs/PHASE10_PRODUCTION_PLAN.md`, "SEO and indexing") — do not remove until the product with
  billing is actually live. At that point: drop the noindex tags, replace `robots.txt` with an
  allow-all version, add `sitemap.xml`, and submit to Search Console/Bing.
- [x] **Mobile layout** — fixed a real overflow bug: flex items using non-stretch cross-axis
  alignment (`align-items: center`/`flex-start`) size to their content's intrinsic width unless
  given `min-width: 0` (or an explicit `width`), so a wide image or long heading blew out the
  whole page width instead of shrinking. Fixed via `min-width: 0` on `.steps li`/`.steps li > div`/
  `.callout-sequence figure`, and explicit `width: 100%` on the hero's flex children in the mobile
  media query. Also simplified the mobile nav to just the brand + Download button (the anchor
  links don't fit at phone widths and are redundant with the page's own sections).
