---
name: github-social-proof-research
description: Discover GitHub projects by real popularity and human discussion first (Stars, Forks, issue comments, social demos); then trace source code, models, voice packs, API calls and message delivery. Avoid subjective AI evaluations.
license: Apache-2.0
---

# Human popularity first. Code archaeology second.

This is a **public OSS discovery skill**, not a generic quality-review checklist. User preference: human popularity, real-world demonstrations and active discussion before model judgement. A project with one Star and a polished README does not automatically outrank a project with thousands of Stars, many Forks, real videos and authentic comments.

## Required research sequence

1. **Expand the search universe** beyond the name the user guessed. Include adjacent ecosystems and functional phrases, code entrypoints, integrations, competing frameworks and creator demos. For DSH/QQ voice, query DSH, DeepSeek Harness, qq-bridge, OneBot, NapCat, AstrBot, MaiBot, RVC, GPT-SoVITS, CosyVoice, VoxCPM, Breeze, TTS, qq_send_voice and send_group_msg. Search popular curated registries and creator links as well as GitHub.
2. **Rank candidates by actual social signals before deep source review.** Retrieve GitHub Stars, Forks, open issues, and **real issue comment counts** separately. Sample the most-discussed issues and show links to discussions. A fork lineage is not an independent clean-room implementation; note it.
3. **Search actual community demonstration and reception**, not merely README mentions. Use Agent-Reach, last30days, native Bilibili/YouTube/X/Reddit/Xiaohongshu search and the linked creator's profile. Record actual post URL, author, date, views, likes, comments and whether audio/video was accessible. Distinguish independent user demonstrations from self-promotional clips. Don't invent or estimate missing figures. **Not collected is not zero.**
4. **Inspect how popular projects really work.** Read actual code, configs and references: model, API host and auth type (never secrets), voice pack filename/weights, reference transcript, emotion/prosody, audio conversion, OneBot QQ record message path, and failure handling. Trace from the agent tool to audio generation to platform send with real `file:line` URLs. Octocode's research skill / AST / LSP help when available.
5. **Use social proof to prioritize; use code to describe.** Never increase a project's adoption rank because its implementation looks elegant. Keep `Popularity / Human reception` and `Implementation verified` in separate columns. A viral demo does not by itself prove a public GitHub repo is the code used; connect them via author-provided links.
6. **Report search coverage.** Show original queries, registries, number of candidates, how many fetched, any GitHub API rate limits or truncation, unsearched platforms and next discoverable leads. Never call a finite search exhaustive.

## Runnable GitHub first-pass tool

`socialscan.py` is an adjacent zero-dependency Python CLI. It only calls GitHub's public read APIs, does not run a candidate project, and ranks by raw Stars then Forks. It can sample issue discussion, trace source code lines, and import externally observed social post engagement. This is complementary to Agent-Reach + last30days + Octocode; no dependency or credentials are silently installed.

```bash
python3 socialscan.py \
  --query '"DeepSeek Harness" "QQ"' \
  --query '"OneBot" "TTS"' \
  --query '"QQ" "GPT-SoVITS"' \
  --require 'QQ|OneBot|NapCat|AstrBot' \
  --require '语音|声音|voice|TTS|RVC|CosyVoice|speech' \
  --seed Derpyu520/qq-bridge \
  --seed aureth-labs/dsh-aurabot-qq \
  --discussion-top 10 --inspect-top 5 \
  --output qq-voice.json
```

Social metrics come from independently visited posts or research tools. Put observed URLs and numeric counts in a JSON array following `examples/social-signals.example.json`; run with `--social-file social.json`. That file is imported as **externally supplied, not auto-verified**.

## Rating and output contract

Default sort: raw GitHub **Stars desc, Forks desc, sampled issue comments desc**. A transparent logarithmic GitHub adoption index may be reported for comparison, but is **never a rating of TTS realism or user satisfaction**.

Required columns: repository URL; Stars; Forks; real discussion links and sampled comment counts; public video link / views / likes / comments if observed; actual model and voice pack and license; API/QQ delivery entrypoint with code links; explicit unknowns. Flag fork duplicates, bot-only comments, API failures and no independent demos.

## Rules

- Apache-2.0 via public repository root LICENSE. Never copy others' model weights, private voices or source into this project.
- Respect user authorization. Research read-only: no QQ binding, installing third-party code, marketing outreach or other external actions.
- Never copy/paste access tokens, log authorization headers, extract browser cookies or scrape protected groups.
- GitHub Search REST has a **1,000-result maximum per query** and rate limits. GitHub code indexing can omit forks and nondefault branches.
- A massive Star count indicates adoption/visibility, but quality claims such as "声音很真人" still require hearing a real posted recording and reviewing real user comments.

### Objective feature eligibility

A high-Star DSH account-balance widget can be genuinely popular yet unrelated to QQ speech. Supply two repeated `--require` patterns: one for the messaging ecosystem, one for the voice feature. The CLI checks repository name/description and then public README text before taking the highest social-adoption candidates. It reports how many were excluded, and how many could not be checked within the README budget. The patterns establish functional relevance, not an AI quality judgement.
