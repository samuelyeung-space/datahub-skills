# AI Handout Site

Static public frontend for the AI handout workflow. The website is the teacher-facing entry; the public GitHub copy supplies machine-readable instructions and learning materials. Private maintenance repositories remain private.

## Live

- Cloudflare Pages project `ai-handout-school`: <https://ai-handout-school.pages.dev> (deployed with `wrangler pages deploy`; only `index.html`, `ai.txt`, `404.html`, `_headers` are uploaded)

## Vercel

- Import repository: `samuelyeung-space/datahub-skills`
- Root Directory: `ai-handout-site`
- Framework Preset: `Other`
- Build Command: leave empty
- Output Directory: `.`

## Cloudflare Pages

- Connect repository: `samuelyeung-space/datahub-skills`
- Production branch: `main`
- Root directory: `ai-handout-site`
- Build command: leave empty
- Build output directory: `.`

`index.html` is the human-facing page. `ai.txt` is the plain-text machine entry. `_headers` is used by Cloudflare Pages; `vercel.json` supplies the equivalent Vercel configuration.
