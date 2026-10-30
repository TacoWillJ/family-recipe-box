# Family Recipe Box: deploy notes

The live site (tacowillj.github.io/family-recipe-box) is served from the **gh-pages** branch, not main.

After committing to main, ALWAYS also run:

    git push origin main main:gh-pages

Then confirm both branches point at the same commit with `git ls-remote origin`.
Pushing only main leaves the website out of date.
