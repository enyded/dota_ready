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
- `app-main.png`, `app-match-found.png`, `app-notification.png`, `app-party-notification.png`,
  `app-settings.png`, `app-info.png`, `app-allow-bg-activity.png` — Android app screens.
- `desk-main.png`, `desk-qr.png` — Windows desktop app screens.
- `og-cover.png` — generated cover image, not a screenshot (locale-specific OG previews are a
  nice-to-have, not required).
- `android-qr-placeholder.png` — generated QR code, not a manual screenshot; points at the
  stable `ReAccept.apk` release URL.

Public asset URLs carry a shared `rev` query parameter in the HTML. Bump it whenever an image or
stylesheet is replaced under the same filename so GitHub Pages and browser caches fetch the new
file immediately.

## Still TODO before launch

- [x] **Screenshots (`en/`)** — the product owner supplied the rebranded Windows and Android
  screenshots. The generated `og-cover.png` uses the same approved ReAccept icon and copy.
- [x] **Download links** — point at the stable GitHub Release aliases `ReAccept-Setup.exe` and
  `ReAccept.apk`; the QR code encodes the same Android URL.
- [x] **Support email** — `support@re-accept.com`, wired into the footer and every legal page;
  the source documents live under `docs/legal/` in the main repository.
- [x] **Legal pages published** — `privacy.html`, `terms.html`, and `disclaimer.html` publish the
  English documents maintained under `docs/legal/`, including Firebase/Crashlytics, Telegram,
  Google Play subscriptions, retention, security, and verified support deletion. The policy has
  no `noindex` directive and `robots.txt` allows every public page and presentation asset.
- [x] **Hosting** — deploying via GitHub Pages on this repo for now (Settings → Pages → Source:
  Deploy from a branch → `main` → `/` (root) → Save), served at
  `https://re-accept.com/`. `.nojekyll` is committed so GitHub serves the static files as-is
  instead of running them through a Jekyll build. DNS is managed by Cloudflare in DNS-only mode
  for the GitHub Pages apex and `www` records; `www` redirects to the apex domain.
- [x] **SEO launch gate opened** — removed the landing-page `noindex`, changed `robots.txt` to
  allow crawling, and published `sitemap.xml` for the landing page, focused search page, and
  legal pages.
- [x] Submit `https://re-accept.com/sitemap.xml` to Google Search Console.
- [ ] Submit `https://re-accept.com/sitemap.xml` to Bing Webmaster Tools.
- [x] **Mobile layout** — fixed a real overflow bug: flex items using non-stretch cross-axis
  alignment (`align-items: center`/`flex-start`) size to their content's intrinsic width unless
  given `min-width: 0` (or an explicit `width`), so a wide image or long heading blew out the
  whole page width instead of shrinking. Fixed via `min-width: 0` on `.steps li`/`.steps li > div`/
  `.callout-sequence figure`, and explicit `width: 100%` on the hero's flex children in the mobile
  media query. Also simplified the mobile nav to just the brand + Download button (the anchor
  links don't fit at phone widths and are redundant with the page's own sections).

## Landing localization

Localize the landing for the same languages bundled in Android and used by the Play listing:
English, German, Spanish, Indonesian, Polish, Brazilian Portuguese, Russian, Turkish, Ukrainian,
and Vietnamese.

- [x] Use stable locale paths (`/de/`, `/es/`, `/id/`, `/pl/`, `/pt-br/`, `/ru/`, `/tr/`,
  `/uk/`, `/vi/`) while keeping English at `/` as `x-default`.
- [x] Localize the home page and `/accept-dota-2-match-from-phone/` copy, titles, descriptions,
  Open Graph text, accessibility text, and calls to action without changing product claims.
- [x] Add reciprocal `hreflang` links and localized entries to `sitemap.xml`.
- [x] Reuse English screenshots as fallback and replace only captures containing visible text
  when an approved localized version exists.
- [x] Keep English as the controlling legal version until reviewed legal translations exist;
  label convenience translations clearly rather than silently changing their effect.

Localized copy is maintained in `locales/pages.json`; shared markup lives in `templates/`.
Generated locale pages and `sitemap.xml` are committed so GitHub Pages can serve them without a
build step. After changing copy or templates, regenerate and validate from the landing repository:

```powershell
python scripts/build_locales.py
python scripts/validate_locales.py
```

The validator checks canonical URLs, reciprocal `hreflang`, structured data, page language,
internal links, local assets, and the localized sitemap URL set. English remains hand-maintained
at `/` and `/accept-dota-2-match-from-phone/`; the validator includes both English pages.
