---
title: "First post: how we did all this"
date: 2026-02-25
tags: ["meta", "workflow", "hugo"]
draft: false
---

This post explains how we built the new blog section for this website.

The short version: we combined **ChatGPT** (for planning and content decisions) and **Codex CLI** (for direct file edits, structure setup, and deployment wiring).

## Workflow used

1. Define the exact blog requirements in one detailed prompt.
2. Use Codex CLI to create all required Hugo files and templates.
3. Add a first post, CSS, and GitHub Actions deployment.
4. Iterate from local feedback (menu links, local file navigation, visual style).

## Prompt used

```text
You are to set up a static blog section for an existing website using Hugo.

OBJECTIVE
Create a clean, minimal blog section similar in spirit to:
https://rkirov.github.io/posts/

The blog must:
- Be built with Hugo
- Use Markdown for posts
- Have a /posts/ index page listing posts in reverse chronological order
- Each post must have:
  - Title
  - Date
  - Optional tags
  - Estimated reading time
- Generate an RSS feed
- Use clean academic typography
- Support LaTeX math via KaTeX
- Support syntax-highlighted code blocks
- Be deployable to GitHub Pages

PROJECT STRUCTURE
Create the following structure:

.
├── hugo.toml
├── content/
│   └── posts/
│       └── first-post.md
├── layouts/
│   ├── _default/
│   │   └── baseof.html
│   ├── index.html
│   └── posts/
│       ├── list.html
│       └── single.html
├── static/
│   └── css/
│       └── style.css
└── assets/ (if needed)

IMPLEMENTATION DETAILS

1. CONFIGURATION (hugo.toml)
   - BaseURL placeholder
   - Title
   - Enable RSS
   - Enable taxonomies: tags
   - Enable syntax highlighting
   - Enable KaTeX rendering

2. POST FORMAT
   Posts must use frontmatter like:

   ---
   title: "Sample Post"
   date: 2026-02-25
   tags: ["math", "example"]
   draft: false
   ---

3. /posts/ INDEX PAGE
   - Show all posts
   - Reverse chronological
   - Display:
       Title (linked)
       Date
       Reading time
       Tags
       Short summary (first 200 chars)
   - Clean vertical layout

4. SINGLE POST PAGE
   - Title at top
   - Date under title
   - Reading time
   - Tag links
   - Clean typography
   - Max content width ~700px
   - Math rendering
   - Code highlighting

5. STYLING
   Create a minimal CSS file:
   - Serif body font (e.g., Georgia or similar system serif)
   - Sans-serif headings
   - Comfortable line height (1.6+)
   - Subtle link styling
   - No heavy colors
   - Responsive layout

6. HOMEPAGE
   Modify homepage to:
   - Show site title
   - Link to /posts/
   - Optionally show latest 3 posts

7. GITHUB PAGES DEPLOYMENT
   Add instructions:
   - Hugo build command
   - Output to /docs or /public
   - GitHub Actions workflow for automatic deployment

8. CREATE ONE EXAMPLE POST
   Include:
   - Code block example
   - Inline math example
   - Display math example
   - Multiple sections

OUTPUT
Generate:
- All required config files
- All layout templates
- CSS
- Example post
- GitHub Actions workflow file
- Brief deployment instructions

Ensure the solution is production-ready, minimal, and clean.
Avoid using external themes — implement templates manually.
```

This post is a small record of the process and a baseline for future improvements.

---

**Disclosure (2026-02-25).** Parts of this post were drafted with Codex CLI using the ChatGPT **OpenAI o3** model in this session, and then revised manually.
