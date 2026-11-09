---
name: github-human-signal-scout
description: Discover real open-source implementations by evidence of human attention and adoption—stars, forks, comments, videos and user reception—before technical source audits. 
---

# Human Signal GitHub Research

The **human use and enthusiasm signals come first**. Do not substitute LLM personal judgments about which architecture is attractive for what real people actually share, fork, discuss or use.

1. Define observable user outcomes (example: an AI in QQ sends natural expressive voice messages). Start from creator demonstrations, Bilibili/YouTube/Douyin, QQ/Discord communities, the linked repo and voice model.
2. Enumerate multiple repo-discovery paths: creator videos and descriptions; GitHub topics; multilingual terms; implementation signatures; README citations; dependency and fork graphs; curated registries; cross-platform bot projects, not only repositories with DSH in their name.
3. Run: python3 tools/github-human-signal-scout/scout.py 'QQ DSH 真人语音' --pages 2 --out report.json
4. Prioritize **stars, forks, independent issue/comment activity, source-linked video views/likes, and real community acceptance**. Record actual observed numbers and dates; rate changes and fork families matter. Do not invent missing platform metrics.
5. For socially validated candidates, deeply examine voice packs / checkpoint license, API model IDs, request schema, cloned reference recordings, code path to QQ OneBot 'record' and transcoding to SILK, and real demo output. Trace siblings, imports, references and authors.
6. Listen to actual demo audio before ranking *audio naturalness*. Source reading explains how a popular system works; it does not prove how good the audio sounds.
7. Output a comparable table: repository, stars, forks, issue discussion, source-linked video metrics, human experience reports, real voice models, API parameters, QQ sending implementation, rights and open questions.

Do not claim exhaustiveness: GitHub search max 1,000 per query, missed/unindexed/untagged repos, manipulated stars and correlated forks. GitHub open_issues includes PRs; only sampled real issues count toward discussion. No sending messages, cloning unauthorized people, publishing or installing without authorization.
