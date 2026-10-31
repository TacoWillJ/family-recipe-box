# Family Recipe Box: deploy notes

The live site (tacowillj.github.io/family-recipe-box) is served from the **gh-pages** branch, not main.

After committing to main, ALWAYS also run:

    git push origin main main:gh-pages

Then confirm both branches point at the same commit with `git ls-remote origin`.
Pushing only main leaves the website out of date.

## Adding photos

New card photos: resize to max 1600px, then crop to the card with
`tools/cardcrop.py` (`card_box(im)` finds the paper region at the photo's center; returns None if unsure,
in which case keep the photo uncropped). `tools/autocrop.py` is an older edge-trimmer; it fails on photos
with lots of table, so prefer cardcrop. Always review a contact sheet before committing; skip any crop that touches text.

## Cookbook PDFs

After adding or changing recipes, rebuild the downloads before committing:

    NODE_PATH=$(npm root -g) python3 tools/build_pdf.py

This regenerates cookbook.pdf and cookbook-with-photos.pdf (keep the photo one under 15 MB). The site's
"Download cookbook" buttons link to them. Publish both PDFs to the Claude artifact as well.
