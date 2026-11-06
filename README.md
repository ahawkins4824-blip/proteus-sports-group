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

Edit copy in `content.json`, homepage structure in `home_v2.py`, shared pages in `build.py`, and styles/interactions in `dist/styles.css`, `dist/motion.css`, `dist/app.js` and `dist/motion.js`. Re-run both build commands after changes.

## Included

The homepage, six programme pages, programme explorer, team/approach page, contact page, existing privacy policy, 404 page and legacy URL aliases. The homepage has one programme carousel, six visible programme buttons, authentic video and a curated Instagram reel/post grid. Mobile navigation, accessible FAQs, local fonts and reduced-motion controls are included.

The contact form prepares an email draft for the visitor to review and send in their email app. It does not submit or store messages itself. The alternative online form remains at https://proteus-sports.squarespace.com/contact-1; keep that service available while linked.

Images and videos are original Proteus material. Provenance and font licences are in `dist/assets`. Saved approved designs remain under `dist/approved-v1`, `dist/approved-v2` and `dist/approved-v3`; exported copies retain working links and noindex metadata.

## Hosting and domain

The Pages export rewrites project-relative routes and assets, canonical URLs, the sitemap, saved-design links and dynamic Academy contact links. GitHub Pages does not process Cloudflare's `_redirects` file, so the export omits it and retains HTML redirect fallback pages for old URLs.

The public address above uses GitHub Pages. **proteus.nz remains on the original Squarespace site until its domain manager changes DNS and the custom domain is configured in this repository's Pages settings.** Do not use the obsolete ChatGPT Sites DNS records from the earlier hosting setup.

For a later custom-domain cutover, configure the approved domain in GitHub Pages first, follow GitHub's current DNS instructions, then change `ORIGIN` in `build.py` to the permanent URL. The workflow's configure-pages step supplies the correct export URL and base path. Preserve email and unrelated DNS records. The original design/source backups remain in the local project's `versions` directory.
