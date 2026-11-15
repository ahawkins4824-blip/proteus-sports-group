# Website hosting

This website is hosted through GitHub Pages in `ahawkins4824-blip/proteus-sports-group`. The user explicitly chose GitHub Pages instead of ChatGPT Sites. Do not create or deploy a Sites project for this website.

Work in this checkout. Build with `python3 build.py`, then `python3 prepare_github_pages.py --base-path /proteus-sports-group --site-url https://ahawkins4824-blip.github.io/proteus-sports-group`. Pushes to main trigger the Pages workflow. Verify the workflow and live URL after publishing. Keep the approved design and saved snapshots intact unless the user requests changes.

The enquiry form is an email draft builder until `FORM_ACCESS_KEY` in `build.py` holds a Web3Forms key; only then does it send messages directly. Do not claim it sends or stores messages while the key is empty. Squarespace is being retired: do not link to it. Run `python3 optimise_images.py` after adding photos. proteus.nz DNS still requires a separate custom-domain cutover; earlier ChatGPT Sites DNS instructions are obsolete.

Use the shared `icons.py` SVG artwork for authored UI icons. Do not replace arrows, play/pause or other icon artwork with font symbols that can become emoji on phones.
