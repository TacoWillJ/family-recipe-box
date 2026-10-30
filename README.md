# Family Recipe Box

Grandma Sharp's recipe box, typed up and searchable, with photos of the original cards.

- `index.html` – the site (search, category tabs, one page per recipe)
- `recipes.json` – every recipe as structured data
- `img/` – card photos, numbered to match each recipe

To add a recipe, add an entry to `recipes.json` and its photos to `img/`.


## Publishing

The site is served from the `gh-pages` branch. After pushing to `main`, also run `git push origin main:gh-pages` or the website will not update.
