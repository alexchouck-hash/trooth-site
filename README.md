# Trooth Site

The official public website and documentation for **Trooth: The Single Data Connector and Provenance Pipe for Apps and Agents**.

Trooth resolves requests to verified sources, fetches real-time data, and wraps every response inside a cryptographic provenance envelope: source identity, event timestamps, freshness lag, audit lineage, and an Ed25519 signature.

## What is Inside This Repository

- **Astro Static Site:** Fast, responsive, accessible, mobile-first static website built with Astro 5.
- **Project Explainer:** Deep architectural walkthrough of the single connector, the six tools, and the provenance envelope.
- **Public Benchmark & Scorecards:** Real-time and mechanical evaluations of public sources (NWS, Open-Meteo, USGS, BLS, FRED) across six objective dimensions plus anchored accuracy (Rule H1).
- **Interactive Documentation:** Quickstart guides for Model Context Protocol (MCP) and REST API.
- **Provider Information:** How data owners list feeds, get metered, and earn revenue through the pipe.
- **Transparent Methodology:** Mathematical definitions of freshness lag, revision behavior, correction latency, completeness, schema stability, and internal consistency.

## Live Public Site

The site is published live at:
**[https://alexchouck-hash.github.io/trooth-site/](https://alexchouck-hash.github.io/trooth-site/)**

## Local Development

Prerequisites: Node.js 20+ or 22+.

```bash
# 1. Install dependencies
npm install

# 2. Start local development server
npm run dev
```

Visit `http://localhost:4321` in your browser.

## Building and Deploying

```bash
# Build static output to ./dist/
npm run build

# Deploy to GitHub Pages (gh-pages branch)
npm run deploy
```

Static output is compiled to `./dist/` and served live via GitHub Pages.

## Design and Style Principles

- Plain copy without marketing hype.
- No claims not backed by an objective scorecard.
- No em dashes anywhere in site text.
- Mobile-first, responsive typography, accessible color contrast.

## License

Apache-2.0. See [LICENSE](LICENSE).
