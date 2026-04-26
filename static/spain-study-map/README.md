# Spain Study Map

Static geography-learning page for Spain's autonomous communities and provinces.

## What is included

- Four modes:
  - Study autonomous communities
  - Study provinces
  - Quiz 5 random autonomous communities
  - Quiz 8 random provinces
- English, Spanish, and Catalan interface buttons.
- Real Spain boundary map data via local TopoJSON.
- Greedy map coloring so adjacent regions get different colors.
- Static-file structure suitable for GitHub Pages.

## One-time setup before uploading

Run this once from inside this directory:

```bash
./fetch-assets.sh
```

That downloads all runtime dependencies into local files:

```text
assets/vendor/d3.v7.min.js
assets/vendor/topojson-client.min.js
assets/vendor/d3-composite-projections.min.js
assets/data/provinces.json
```

After that, the page does not call external websites at runtime.

## Local testing

Because the page loads a local JSON file, test it from a local server rather than by double-clicking `index.html`:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/
```

## Upload to GitHub Pages

Copy the entire folder, after running `fetch-assets.sh`, into your repository, for example:

```text
jordilluisfigueras/
  spain-study-map/
    index.html
    assets/
      css/
      js/
      vendor/
      data/
```

Then the page should be available at:

```text
https://kaminoite.github.io/jordilluisfigueras/spain-study-map/
```

## Third-party data and code

See `THIRD_PARTY_NOTICES.md`.
