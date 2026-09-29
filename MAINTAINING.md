# Maintaining the MINDS Lab website

The site is built with [Astro](https://astro.build). Routine updates are edits to Markdown, YAML, or BibTeX files; no HTML is needed.

## Where things are

| What | File(s) |
|---|---|
| Papers | `src/data/papers.bib` |
| People | `src/content/people/<name>.md`, photos in `public/img/people/` |
| News | `src/content/news/<date>-<topic>.md` |
| Research areas | `src/content/research/<n>-<topic>.md`, optional figures in `public/img/research/` |
| Teaching | `src/data/teaching.yaml` |
| Join / Open positions | `src/pages/join.astro` (English and Korean text) |
| PI page | `src/pages/pi.astro` |
| Front page text | top of `src/pages/index.astro` |
| Site name, email, address, links, menu | `src/data/site.ts` |
| Colors and fonts | `src/styles/global.css` |

## Common updates

**New member.** Copy an existing file in `src/content/people/`, change the fields, and put a photo (portrait, about 800×1000 px) in `public/img/people/`. `role` is one of `pi, postdoc, phd, ms, visiting, ug, alumni`.

**Member leaves.** In their file set `role: alumni`, `end: "YYYY"` (or `YYYY-MM`) and `next_position: ...`. Remove `email` if it will stop working.

**News.** Add a file in `src/content/news/`:

```
---
date: 2026-10-01
title: Optional headline
---
Text in Markdown.
```

**Paper.** Add a BibTeX entry to `src/data/papers.bib`. Optional fields: `selected = {true}` (Selected list and front page), `arxiv = {2602.16636}`, `status = {under review}`. Fields such as `abstract`, `local-url`, `google_scholar_id` are removed from the BibTeX that visitors see.

**Research figure.** Put an image in `public/img/research/` and add `image: /img/research/<file>` to the area's Markdown file. It replaces the drawn schematic.

## Automatic paper check

`.github/workflows/paper-sync.yml` runs every Monday (09:00 KST) and can be started by hand (Actions → Paper check → Run workflow). It:

1. lists works from OpenAlex (ORCID 0000-0003-1974-028X) and arXiv;
2. adds new entries to `papers.bib`, and updates arXiv-only entries when the journal version appears;
3. writes one news item for each paper published in the last 180 days that has no news item yet (news items are linked to papers by `paper: "<doi>"`);
4. opens a pull request "Paper check: new papers and news".

Review the pull request (wrong author with the same name, duplicates, wording of the news) and merge it. One-time setting: Settings → Actions → General → Workflow permissions → allow GitHub Actions to create pull requests.

## Hosting

**Cloudflare Pages** (chosen): Cloudflare dashboard → Workers & Pages → Create → Pages → Connect to Git → select this repository.
- Production branch: `master` (use `astro-site` until it is merged)
- Framework preset: Astro · Build command: `npm run build` · Output directory: `dist`
- Environment variable: `NODE_VERSION = 22`

Every other branch and pull request gets its own preview URL.

**GitHub Pages** (optional, keeps https://kyujungjun.github.io working): after merging to `master`, set Settings → Pages → Source to "GitHub Actions". `.github/workflows/deploy-github-pages.yml` then publishes the same site.

## Working on the site locally

```
npm install
npm run dev      # http://localhost:4321, reloads on save
npm run build    # checks that everything builds
```
