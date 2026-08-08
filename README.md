# Dota Ready — landing page

Static site for the Dota Ready landing page. Plain HTML/CSS, no build step, no JS framework.
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

## Still TODO before launch

- **Screenshots** — `assets/screenshots/` currently has no real images. Needed: pairing/QR flow,
  phone notification, accept flow, the Android background-permission screen, and an OG cover image
  (`og-cover.png`, referenced by the Open Graph tags in `index.html`).
- **Download links** — point at `https://github.com/enyded/dota_ready/releases/latest/download/...`.
  This repo is also where release assets should be published (per the "Release file distribution"
  section of the production plan) — filenames must stay stable across releases for these links to
  keep working.
- **Support email** — replace `REPLACE_SUPPORT_EMAIL` in `index.html`'s footer.
- **Privacy Policy** — `privacy.html` mirrors `docs/PRIVACY_POLICY.md`, which is still a draft with
  bracketed placeholders ([DATE], [PUBLISHER LEGAL NAME], etc.). Fill those in before removing
  `noindex`.
- **Domain** — no custom domain wired up yet (pending the VPS/domain purchase decision in the
  production plan's Open items). Until then this can be hosted via GitHub Pages on this repo
  (Settings → Pages → deploy from `main`) at `https://enyded.github.io/dota_ready/`.
- **SEO flip at launch** — both HTML files carry `<meta name="robots" content="noindex, nofollow">`
  and `robots.txt` disallows everything. This is intentional pre-launch (see
  `docs/PHASE10_PRODUCTION_PLAN.md`, "SEO and indexing") — do not remove until the product with
  billing is actually live. At that point: drop the noindex tags, replace `robots.txt` with an
  allow-all version, add `sitemap.xml`, and submit to Search Console/Bing.
