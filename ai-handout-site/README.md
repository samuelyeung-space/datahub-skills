# AI Handout Site

Static public frontend for the AI handout workflow. The website is the teacher-facing entry; the public GitHub copy supplies machine-readable instructions and learning materials. Private maintenance repositories remain private.

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
