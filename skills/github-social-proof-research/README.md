# GitHub Social-Proof Research

**Humans first, code second.** Discover GitHub projects by actual Stars, Forks, issue comments and linked social demos *before* spending time reading their code. Built to correct the tendency of AI assistants to recommend polished but obscure projects while ignoring widely adopted ones.

## Reuse existing, popular tools

- [Agent-Reach](https://github.com/Panniantong/Agent-Reach) — search GitHub, Bilibili, Xiaohongshu, Reddit, YouTube, X and other platforms.
- [last30days](https://github.com/mvanhorn/last30days-skill) — research real recent discussions and audience engagement.
- [Octocode](https://github.com/bgauryy/octocode) — deep cross-repository code research, AST/LSP/PR tracing; has its own `octocode-research` Skill.
- Native GitHub Search REST and `gh search repos` — raw GitHub Stars, Forks and issue discussion APIs.

**The gap this project fills:** a single popularity-first Agent Skill plus a small, transparent, stdlib-only CLI which combines GitHub adoption metrics, discussions, optional human-supplied demo data and precise code links. It does not copy or bundle any upstream tool.

## Quick start

Requires Python 3.10+ and access to `api.github.com`. For public repositories no GitHub token is required until API quotas are exhausted; set `GITHUB_TOKEN` in your *own environment* to raise the limit. Never include the token in command line arguments or logs.

```bash
cd skills/github-social-proof-research
python3 socialscan.py \
  --query '"DeepSeek Harness" "QQ"' \
  --query '"OneBot" "TTS"' \
  --query '"QQ" "GPT-SoVITS"' \
  --seed Derpyu520/qq-bridge \
  --seed aureth-labs/dsh-aurabot-qq \
  --discussion-top 10 --inspect-top 5 \
  --output reports/qq-voice.json
```

Outputs: `reports/qq-voice.json` and `reports/qq-voice.md`. Query families are issued with Stars, Forks and best-match sorts, then deduplicated by repository. Full code inspection is restricted to top ranked projects and produces `file:line` URLs; it never executes third-party repositories.

Test offline, without credentials or network:

```bash
python3 -m unittest discover -s tests -v
```

## Add actual social-media validation

The GitHub API cannot independently tell you how many views an unrelated Bilibili, Reddit or Xiaohongshu demo received. Search via Agent-Reach/last30days or original platform, view the actual post, and supply a JSON list:

```json
[
  {
    "repo": "CREATOR/PROJECT",
    "platform": "bilibili",
    "url": "https://www.bilibili.com/video/BVxxxxxxxxxxx/",
    "observed_at": "2026-11-09T12:00:00Z",
    "views": null,
    "likes": null,
    "comments": null,
    "shares": null
  }
]
```

Fill **only observed** counts; `null` means not collected. The CLI imports them with `--social-file observed.json`, labeling them `supplied_unverified` because the CLI does not scrape/recheck the post. Do not replace genuine popularity with inferred engagement or self-generated AI quality scores.

## Output contract

Default sort: raw **Stars descending; Forks descending; sampled issue comments descending**. The optional logarithmic GitHub adoption index is transparent, never “naturalness” or “best voices” rating.

The report distinguishes:
- GitHub adoption and raw discussion links.
- Platform demonstration links/engagement if actually observed.
- TTS/RVC/voice-pack/API/QQ delivery code paths with line URLs.
- Missing source, rate-limit errors, nondefault branch/fork limitations and truncated discovery.

**Limits:** GitHub repo search returns at most 1,000 matches per query; topics, package indexes, creator references and source search can yield additional candidates. Stars and Forks are imperfect adoption proxies, and third-party demo popularity does not identify the exact source version without creator provenance.

## License & boundaries

Apache License 2.0, inherited from the public repository root [LICENSE](../../LICENSE). Read-only analysis; never installs, runs, contacts or controls the selected software. It does not reproduce third-party voice models, bypass QQ access restrictions or use somebody's private recordings.
