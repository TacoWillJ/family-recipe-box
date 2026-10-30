# Family Recipe Box: deploy notes

The live site (tacowillj.github.io/family-recipe-box) is served from the **gh-pages** branch, not main.

After committing to main, ALWAYS also run:

    git push origin main main:gh-pages

Then confirm both branches point at the same commit with `git ls-remote origin`.
Pushing only main leaves the website out of date.

## Adding photos

New card photos: resize to max 1600px, then auto-crop the table with
`python3 tools/autocrop.py <in_dir> <out_dir>` (trims only edge rows/cols that are mostly wood).
Review the result before committing; skip the crop if it touches any text.
