# AI Project Guide: Gmeek + gjken.github.io

This note is for AI assistants or future maintainers who need to understand the two related folders quickly.

## Folder Roles

### `D:\Study\html\Gmeek`

This folder is the blog generator/template source.

It contains:

- `Gmeek.py`: the core Python static-site generator.
- `templates\`: Jinja2 HTML templates for index, post, tag/search, footer, and base layout.
- `requirements.txt`: Python dependencies required by the generator.
- `.github\workflows\static.yml`: a simple GitHub Pages deploy workflow for static content only.

This folder is not the actual blog content repository. It does not currently include `config.json`, so running `Gmeek.py` directly from here will fail unless a blog repository's config and content are copied in first.

### `D:\Study\html\gjken.github.io`

This folder is the actual blog repository.

It contains:

- `config.json`: the real blog configuration.
- `.github\workflows\Gmeek.yml`: the workflow that clones `gjken/Gmeek`, runs `Gmeek.py`, commits generated files, and deploys GitHub Pages.
- `blogBase.json`: generated/cache metadata used for incremental builds.
- `docs\`: generated static site output for GitHub Pages.
- `docs\post\`: generated article HTML files.
- `docs\postList.json`: generated article index used by tag/search page.
- `backup\`: generated markdown backups of issue bodies.
- `static\`: custom static assets copied into the generated site.

The blog content source is GitHub Issues in the `gjken.github.io` repository.

## How They Work Together

The workflow is:

1. A blog article is created or edited as a GitHub Issue in `gjken.github.io`.
2. `.github\workflows\Gmeek.yml` is triggered by `issues` events, manual dispatch, or schedule.
3. The workflow clones the generator from `https://github.com/gjken/Gmeek.git` into `/opt/Gmeek`.
4. The workflow copies the blog repository files into `/opt/Gmeek`.
5. `Gmeek.py` reads `config.json`, pulls GitHub Issues through the GitHub API, and generates static files.
6. Generated files are copied back into `gjken.github.io`.
7. The workflow commits updated generated files.
8. GitHub Pages deploys the `docs/` directory.

In short:

```text
gjken.github.io Issues
  -> gjken.github.io/.github/workflows/Gmeek.yml
  -> clone gjken/Gmeek
  -> run Gmeek.py
  -> generate docs/
  -> deploy docs/ to GitHub Pages
```

## Important Files

### Generator Side: `Gmeek`

- `Gmeek.py`
  - Reads `config.json`.
  - Fetches repository labels and issues.
  - Converts issue markdown to HTML using GitHub's Markdown API.
  - Generates post pages, index pages, tag/search page, RSS, `blogBase.json`, and `postList.json`.

- `templates\base.html`
  - Shared HTML shell.
  - Loads Primer CSS, favicon, custom head injection, theme script, footer, and shared scripts.

- `templates\plist.html`
  - Home/index page template.
  - Renders article list, labels, comment count, dates, RSS, custom links, and theme button.

- `templates\post.html`
  - Article page template.
  - Renders post HTML, utterances comments, code-copy UI, source issue link, and theme controls.

- `templates\tag.html`
  - Tag/search page template.
  - Loads `postList.json` in the browser and performs client-side filtering/search.

### Blog Side: `gjken.github.io`

- `config.json`
  - Main blog config.
  - Current notable settings:
    - `title`: `GJKen`
    - `displayTitle`: `GJKen`
    - `i18n`: `CN`
    - `urlMode`: `issue`
    - `GMEEK_VERSION`: `main`
  - Because `urlMode` is `issue`, generated post URLs are stable numeric URLs such as `post/15.html`.

- `.github\workflows\Gmeek.yml`
  - The real build/deploy workflow.
  - It runs on:
    - `workflow_dispatch`
    - issue opened/edited
    - weekly schedule
  - It clones `gjken/Gmeek`, installs dependencies, runs `Gmeek.py`, commits generated output, and deploys `docs/`.

- `docs\postList.json`
  - Generated article index for the tag/search page.
  - Useful for quickly checking article count, titles, labels, dates, and generated URLs.

- `blogBase.json`
  - Generated metadata/cache.
  - Used by `Gmeek.py` for incremental single-issue rebuilds.

## Current Known State

As last inspected:

- `gjken.github.io` has 14 generated posts.
- Generated post URLs use issue numbers, for example `post/15.html`.
- There is no single-page article configured in `singeListJson`.
- Labels include categories such as `教程`, `网站`, `CDN`, `Github`, `软件`, `Game`, `Anime`, `日常`, `VPS`, `Win`, `图片处理`, `翻墙`, `3D`, `JS`, `CSS`, and `Bug`.

## Useful Implementation Details

### Issue Requirements

An issue must have at least one label to become a generated page.

The first label has special meaning:

- If the first label is listed in `singlePage`, the issue becomes a root-level page such as `about.html`.
- Otherwise it becomes a normal blog post under `docs\post\`.

### Per-Post Custom Config

`Gmeek.py` attempts to parse custom JSON from the last line of an issue body after `##`.

Supported per-post fields include:

- `timestamp`
- `style`
- `script`
- `head`
- `ogImage`

### URL Modes

Configured in `config.json`:

- `issue`: use issue number, stable URLs.
- `pinyin`: convert title to pinyin.
- `ru_translit`: transliterate Russian titles.

The actual blog currently uses `issue`.

## Maintenance Tips

- To change generation logic, edit `D:\Study\html\Gmeek\Gmeek.py` or templates.
- To change blog identity, links, injected scripts, or visual config, edit `D:\Study\html\gjken.github.io\config.json`.
- To change generated site content, edit GitHub Issues in `gjken.github.io`; do not manually edit `docs\post\*.html` unless debugging.
- Avoid reading all of `docs\post\`, `static\`, or `backup\` unless necessary; they can be large/noisy generated or asset folders.
- For quick article metadata, inspect `docs\postList.json` instead of generated post HTML.

## Potential Improvements

- Add an `email` field to `gjken.github.io\config.json`, because the workflow reads `.email` for `git config user.email`.
- Consider expanding issue triggers in `Gmeek.yml` to include `labeled`, `unlabeled`, `reopened`, and `closed` if label or state changes should regenerate the site immediately.
- Consider keeping this guide copied in both repositories so future AI assistants can discover the relationship from either folder.
