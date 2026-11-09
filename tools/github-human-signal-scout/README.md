# GitHub Human Signal Scout

Research repository ecosystems from observed human popularity instead of LLM taste. MIT-licensed, read-only, Python 3.10+ stdlib CLI, no mandatory dependencies.

## Start

Run from this repository root:

    python3 tools/github-human-signal-scout/scout.py "QQ DSH 真人语音" --pages 2 --out report.json

Optional environment variable GITHUB_TOKEN improves rate limits. Keep tokens outside the repo.

Collect actual social-platform measurements using an optional JSON file:

    {
      "owner/repo": [
        {"platform":"Bilibili","url":"https://www.bilibili.com/video/REAL_ID",
         "metric":"views","count":12345,"verified":true,"observed_at":"2026-11-09"}
      ]
    }

Only set verified:true after confirming the original video/page. Counts above are a **format example**, not actual metrics or claims. Provide --social verified-observations.json.

Discovery records all queries, total reported matches, retrieved candidates, page truncation and errors. Ranking prioritizes 5*ln(1+stars) + 7*ln(1+forks) + 2*ln(1+sampled real issue comments) + 1.4*ln(1+verified social engagement) + release bonus. GitHub search is incomplete and capped; sampled issues exclude PRs. Different forks can be copies of one project; manually de-duplicate project families.

The tool is a **discovery and prioritization component**, not a replacement for repo-level code search, external social-platform searches, independent listening tests or rights checks. Follow the paired Skill at ../../skills/github-human-signal-scout/SKILL.md to inspect top candidates and model checkpoints.

Read-only: no cloned private voices, no QQ connection, no API keys written to disk, no messages or purchasing.

## License

MIT, see LICENSE.
