# Silas Bambil — academic portfolio

Quarto source for the portfolio intended for https://sdbambil1.github.io/.

## Content

Home, Research, Projects & Software, Curriculum Vitae, and Contact. Includes the supplied portrait, Georgia Statistics Day conference photograph, and original CV PDF. Manuscripts, software in development, and planned projects are labeled by status.

## Publishing

The GitHub Actions workflow renders the Quarto website and deploys only `_site/` after a push to `main`. The source repository must be named `sdbambil1.github.io`. Enable Pages in repository Settings → Pages and select **GitHub Actions** as the publishing source. Enforce HTTPS when GitHub makes the setting available. Official build and deployment actions are pinned to immutable commit revisions, and the deploy job uses GitHub's temporary token with only Pages and OIDC permissions.

## Editing

Edit the `.qmd` files and `styles-academic.css`, then commit to `main`. Photos are in `assets/` and the original CV is in `files/`. No local server is needed to visit the published site. For local editing, open `Silas-Bambil.Rproj` and use RStudio's Render button or `source("preview.R")`.

## Security and hosting differences

A Python post-render step preserves hash-based script restrictions, a no-referrer policy, and safe new-tab link attributes. It requires only Python's standard library. Pages hosts static files; the custom response handler and its HTTP security headers from the earlier host do not run here. In particular, page metadata cannot enforce frame-ancestors, X-Frame-Options, Permissions-Policy, or custom HSTS. HTTPS is managed by GitHub Pages. There are no public data-entry endpoints or external script CDNs in this site.

## Build locally

Install Quarto 1.8.27 or later and Python 3, then run `quarto render`. Rendered output is ignored by Git and generated again in Actions.
