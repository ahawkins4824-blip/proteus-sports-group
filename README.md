# Proteus Sports Group website

The standalone Proteus Sports Group website, hosted with **GitHub Pages**.

- Website: https://ahawkins4824-blip.github.io/proteus-sports-group/
- Repository: https://github.com/ahawkins4824-blip/proteus-sports-group
- Deployment: pushes to `main` run `.github/workflows/pages.yml` and deploy the generated `_site` artifact to the `github-pages` environment.

## Build and preview

The build uses Python's standard library and has no framework or package installation dependencies.

```sh
python3 build.py
python3 prepare_github_pages.py --base-path /proteus-sports-group --site-url https://ahawkins4824-blip.github.io/proteus-sports-group
```

`dist` contains source assets, styles, scripts and generated pages. `_site` is the final Pages artifact and is ignored by Git. To preview the project URL locally, serve a parent directory containing `_site` at a `proteus-sports-group` subdirectory; the live site uses that repository prefix for navigation, media and dynamic Academy links.

Authored icons are shared inline SVG artwork defined in `icons.py`, so phone browsers do not substitute emoji or different font glyphs. Keep vector icons intact during dynamic label updates.

Edit copy, programmes (in display order, including the Academy sports and their contact emails), stats, Canterbury reach, the six-stage pathway, coaching philosophy, partner lists, the 2026 update and photo alt text in `content.json`; homepage structure in `home_v2.py`; shared pages in `build.py`; and styles/interactions in `dist/styles.css`, `dist/motion.css`, `dist/scale.css` (numbers band, partners, photo mosaic, programme extras, 2026 page), `dist/app.js` and `dist/motion.js`. Re-run both build commands after changes.

## Included

The homepage, nine programme pages (Individual & Performance Coaching, 2027 Athlete Academy, Early Years & Fundamentals, School Sports & Coaching, Holiday Programmes, Coach Development, Community Organisation, Active Age Programme, Teacher Aid), programme explorer, 2026 update page, team/approach page, contact page, existing privacy policy, 404 page and legacy URL aliases. The homepage has a numbers band, a nine-programme carousel with quick links, an action photo mosaic, the Academy feature, a trust section with testimonials, a 2026 update band, authentic video and a curated Instagram reel/post grid. Mobile navigation, accessible FAQs, local fonts and reduced-motion controls are included.

The contact form has two modes, set by `FORM_ACCESS_KEY` at the top of `build.py`. While the key is empty, the form prepares an email draft for the visitor to send from their own email app; it does not submit or store messages. To make the form send messages directly, create a free Web3Forms access key for info@proteus.nz (web3forms.com), paste it into `FORM_ACCESS_KEY` and rebuild. If sending fails, the form falls back to the email draft. The site no longer links to the old Squarespace form.

Holiday dates and prices live in `content.json` under the Holiday Programmes entry (`camps.upcoming`): add `name`, `dates`, `location` and `cost` for each programme and rebuild. Each programme also has its own `faq` and `meta` (search description). Testimonials are in `testimonials`.

After adding or replacing a photo in `dist/assets`, run `python3 optimise_images.py` (needs Pillow) before building. It writes the smaller copies and `image-manifest.json` that the build uses for responsive images.

Images and videos are original Proteus material. Action photos (`dist/assets/pa-*.webp`) come from the Proteus shared Drive folder; see `dist/assets/action-photo-sources.json`. Active Age uses a branded graphic panel until suitable photos are available. Provenance and font licences are in `dist/assets`. Saved approved designs remain under `dist/approved-v1`, `dist/approved-v2` and `dist/approved-v3`; exported copies retain working links and noindex metadata.

## Hosting and domain

The Pages export rewrites project-relative routes and assets, canonical URLs, the sitemap, saved-design links and dynamic Academy contact links. GitHub Pages does not process Cloudflare's `_redirects` file, so the export omits it and retains HTML redirect fallback pages for old URLs.

The public address above uses GitHub Pages. **proteus.nz remains on the original Squarespace site until its domain manager changes DNS and the custom domain is configured in this repository's Pages settings.** Do not use the obsolete ChatGPT Sites DNS records from the earlier hosting setup.

The site is served at https://www.proteus.nz (custom domain set in GitHub Pages settings; DNS in Cloudflare with the GitHub records set to DNS only). `ORIGIN` in `build.py` is https://www.proteus.nz, and the workflow's configure-pages step supplies the export URL and base path. When editing DNS, preserve the email (Microsoft 365) records. The original design/source backups remain in the local project's `versions` directory.
