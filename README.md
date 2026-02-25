# jordilluisfigueras

Personal website with a Hugo-based blog section.

## Local development

```bash
hugo server -D
```

## Production build

```bash
hugo --minify
```

The generated site is written to `public/`.

## GitHub Pages

A workflow is provided at `.github/workflows/hugo.yml`.

1. In GitHub: **Settings → Pages**.
2. Set **Build and deployment** to **GitHub Actions**.
3. Push to `main` and GitHub will build and deploy automatically.
