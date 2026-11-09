#!/usr/bin/env python3
"""Social-proof-first GitHub discovery. Read-only; Python stdlib; Apache-2.0."""
from __future__ import annotations

import argparse
import base64
from collections import defaultdict
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen

GITHUB_API = "https://api.github.com"
SOCIAL_DOMAINS = ("bilibili.com", "youtube.com", "youtu.be", "reddit.com",
                  "x.com", "twitter.com", "xiaohongshu.com", "douyin.com",
                  "tiktok.com", "v2ex.com", "zhihu.com", "weibo.com")
QUERIES = [
    '"DeepSeek Harness" "QQ"', '"qq-bridge" voice',
    '"QQ" "GPT-SoVITS"', '"QQ" "CosyVoice"',
    '"OneBot" "TTS"', '"大肥鱼" 语音',
    '"QQ" "RVC"', '"QQ" "Breeze"',
]
SOURCE_RX = {
    "tts_model": re.compile(r"cosyvoice|gpt[-_]?sovits|rvc|voxcpm|index[-_]?tts|breeze|seed[-_]?tts|mimo|voiceclone", re.I),
    "qq_delivery": re.compile(r"send_group_msg|send_private_msg|qq_send_voice|qq_say_voice|sendVoice|Comp\.Record|onebot|ntsilk|['\"]record['\"]", re.I),
    "voice_config": re.compile(r"ref_audio_path|reference_audio|ref_audio|voice_id|speaker_id|voice_model|emotion|prompt_text|rvcPitch", re.I),
}
PATH_RX = re.compile(r"voice|tts|sovits|cosy|rvc|audio|speech|onebot|qq|README|config", re.I)
EXTENSIONS = (".py", ".ts", ".js", ".mjs", ".tsx", ".json", ".yaml", ".yml", ".md")


class GitHubError(RuntimeError):
    pass


class GitHubAPI:
    def __init__(self, token=None, fetch=None):
        self.token = token if token is not None else os.getenv("GITHUB_TOKEN", "")
        self.fetch = fetch
        self.calls = 0
        self.remaining = None

    def get(self, path, params=None):
        if not path.startswith("/") or "://" in path:
            raise GitHubError("Only relative GitHub REST paths are accepted")
        self.calls += 1
        if self.fetch is not None:
            return self.fetch(path, params or {})
        url = GITHUB_API + path + ("?" + urlencode(params) if params else "")
        headers = {"Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2022-11-28",
                   "User-Agent": "social-proof-research/0.1 (read-only)"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        try:
            with urlopen(Request(url, headers=headers), timeout=18) as response:
                self.remaining = response.headers.get("X-RateLimit-Remaining")
                raw = response.read(7_000_001)
            if len(raw) > 7_000_000:
                raise GitHubError("GitHub response over size cap")
            return json.loads(raw)
        except HTTPError as exc:
            raise GitHubError(f"GitHub HTTP {exc.code} at {path}; rate limit or permissions") from None
        except URLError:
            raise GitHubError(f"GitHub unreachable at {path}") from None


def slug_of(value):
    value = str(value).strip()
    if value.startswith("https://github.com/"):
        value = "/".join(urlparse(value).path.strip("/").split("/")[:2])
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        raise ValueError("Invalid GitHub owner/repo: " + value[:100])
    return value


def summarized(item):
    name = slug_of(item["full_name"])
    return {
        "repo": name, "url": item.get("html_url") or "https://github.com/" + name,
        "description": item.get("description") or "",
        "stars": int(item.get("stargazers_count") or 0),
        "forks": int(item.get("forks_count") or 0),
        "open_issues_including_prs": int(item.get("open_issues_count") or 0),
        "fork": bool(item.get("fork")), "parent": (item.get("parent") or {}).get("full_name"),
        "archived": bool(item.get("archived")),
        "default_branch": item.get("default_branch") or "main",
        "pushed_at": item.get("pushed_at"),
        "license_spdx": (item.get("license") or {}).get("spdx_id"),
        "discovery_routes": [], "discussion_sample": None,
        "external_social": [], "external_social_status": "not_collected",
        "implementation_sources": [],
    }


def discovery(api, queries, seeds, per_query=20, pages=1, limit=100):
    rows = {}
    record = {"queries": [], "errors": [], "incomplete_queries": [], "seed_count": 0}
    for query in queries:
        for sort in ("stars", "forks", "best-match"):
            for page in range(1, pages + 1):
                params = {"q": query, "page": page, "per_page": per_query, "order": "desc"}
                if sort != "best-match":
                    params["sort"] = sort
                try:
                    rsp = api.get("/search/repositories", params)
                except GitHubError as exc:
                    record["errors"].append(str(exc))
                    break
                found = rsp.get("items") or []
                record["queries"].append({
                    "q": query, "sort": sort, "page": page,
                    "reported_total": rsp.get("total_count"), "returned": len(found),
                    "incomplete_results": bool(rsp.get("incomplete_results"))
                })
                if rsp.get("incomplete_results") or rsp.get("total_count", 0) > 1000:
                    record["incomplete_queries"].append(query)
                for item in found:
                    name = item.get("full_name")
                    if not name:
                        continue
                    key = name.lower()
                    if key not in rows:
                        rows[key] = summarized(item)
                    rows[key]["discovery_routes"].append(query + " / " + sort)
                if len(found) < per_query:
                    break
    for seed in seeds:
        try:
            name = slug_of(seed)
            item = api.get("/repos/" + name)
            key = item["full_name"].lower()
            if key not in rows:
                rows[key] = summarized(item)
            rows[key]["discovery_routes"].append("direct-seed")
            record["seed_count"] += 1
        except (GitHubError, ValueError, KeyError) as exc:
            record["errors"].append(str(exc))
    result = sorted(rows.values(), key=adoption_key)
    record["found_before_limit"] = len(result)
    record["candidate_limit_reached"] = len(result) > limit
    return result[:limit], record


def filter_required_features(api, rows, required, record, max_readme_checks=100):
    """Mechanical relevance gate BEFORE sorting by human popularity.

    This is NOT an AI judgement of merit. It checks supplied observable terms
    against repository name/description and, when necessary, its public README.
    Unchecked projects are reported explicitly rather than declared irrelevant.
    """
    if not required:
        record["feature_requirements"] = []
        return rows
    if len(required) > 6 or any(len(pattern) > 130 for pattern in required):
        raise ValueError("Use up to 6 short feature requirements")
    terms = [re.compile(pattern, re.I) for pattern in required]
    matched, skipped = [], 0
    readme_count, readme_errors = 0, 0
    for row in rows:
        # A caller-supplied project is an explicit research lead. Never silently
        # discard it because its README does not contain our synonym list;
        # the optional source-code gate will still check actual implementation.
        if "direct-seed" in row.get("discovery_routes", []):
            row["feature_match_source"] = "explicit_seed_pending_source_check"
            matched.append(row)
            continue
        text = row["repo"] + "\n" + row["description"]
        if all(rx.search(text) for rx in terms):
            row["feature_match_source"] = "name_or_description"
            matched.append(row)
            continue
        if readme_count >= max_readme_checks:
            skipped += 1
            continue
        readme_count += 1
        try:
            response = api.get("/repos/" + slug_of(row["repo"]) + "/readme")
            if response.get("encoding") == "base64":
                text += "\n" + base64.b64decode(response["content"]).decode("utf-8", errors="replace")[:150000]
        except (GitHubError, ValueError, KeyError):
            readme_errors += 1
        if all(rx.search(text) for rx in terms):
            row["feature_match_source"] = "public_README"
            matched.append(row)
    record["feature_requirements"] = list(required)
    record["feature_matched"] = len(matched)
    record["feature_excluded_or_unchecked"] = len(rows) - len(matched)
    record["readme_eligibility_checks"] = readme_count
    record["readme_eligibility_errors"] = readme_errors
    record["not_checked_after_readme_budget"] = skipped
    return matched


def adoption_key(row):
    discussion = row.get("discussion_sample") or {}
    count = discussion.get("top_issue_comments_sum") or 0
    return (-row["stars"], -row["forks"], -count, row["repo"].lower())


def sample_issues(api, row, limit=8):
    name = slug_of(row["repo"])
    try:
        result = api.get("/search/issues", {
            "q": f"repo:{name} is:issue", "sort": "comments",
            "order": "desc", "per_page": limit})
        issues = result.get("items") or []
        row["discussion_sample"] = {
            "reported_issue_count": result.get("total_count"),
            "sample_size": len(issues),
            "top_issue_comments_sum": sum(int(i.get("comments") or 0) for i in issues),
            "top_issue_reactions_sum": sum(int((i.get("reactions") or {}).get("total_count") or 0) for i in issues),
            "top_links": [{"url": i.get("html_url"), "comments": i.get("comments", 0),
                            "reactions": (i.get("reactions") or {}).get("total_count", 0)}
                           for i in issues[:5]],
            "notice": "A top-issue sample, not all comments; may include bots, duplicates and negative feedback.",
        }
    except GitHubError as exc:
        row["discussion_sample"] = {"error": str(exc), "sample_size": 0}
    return row


def load_social(path):
    if not path:
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Social observations must be a JSON list")
    grouped = defaultdict(list)
    for item in data:
        name = slug_of(item["repo"]).lower()
        parsed = urlparse(item.get("url", ""))
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https" or not any(host == d or host.endswith("." + d) for d in SOCIAL_DOMAINS):
            raise ValueError("Unrecognized or insecure social URL")
        checked = {"platform": item.get("platform", host), "url": item["url"],
                   "observed_at": item.get("observed_at"),
                   "note": str(item.get("note") or "")[:200],
                   "provenance": "externally_supplied_not_rechecked"}
        for key in ("views", "likes", "comments", "shares"):
            number = item.get(key)
            if number is not None and (type(number) is not int or number < 0):
                raise ValueError(key + " must be a nonnegative integer or null")
            checked[key] = number
        grouped[name].append(checked)
    return grouped


def attach_social(rows, observations):
    for row in rows:
        entries = list(observations.get(row["repo"].lower(), []))
        row["external_social"] = entries
        row["external_social_status"] = "supplied_unverified" if entries else "not_collected"
    return rows


def safe_excerpt(line):
    """Never expose credential-bearing source lines in an agent report."""
    if re.search(r"api[_-]?key|access[_-]?token|client[_-]?secret|password|authorization|bearer", line, re.I):
        return "[credential-bearing line redacted]"
    return line.strip()[:200]


def readme_demo_links(api, row):
    """Discover creator-linked videos; this does NOT fetch playback or engagement."""
    name = slug_of(row["repo"])
    try:
        response = api.get("/repos/" + name + "/readme")
        if response.get("encoding") != "base64":
            row["readme_demo_links"] = []
            return
        content = base64.b64decode(response["content"]).decode("utf-8", errors="replace")
        results, seen = [], set()
        for n, line in enumerate(content.splitlines(), 1):
            for match in re.findall(r'https?://[^\s<>()]+', line):
                url = match.split('"')[0].split("'")[0].rstrip(".,;]")
                host = (urlparse(url).hostname or "").lower()
                if not any(host == d or host.endswith("." + d) for d in SOCIAL_DOMAINS):
                    continue
                if url in seen:
                    continue
                seen.add(url)
                results.append({
                    "url": url, "readme_line": n,
                    "readme_source": response.get("html_url"),
                    "status": "linked_in_readme_not_played_or_counted",
                })
        row["readme_demo_links"] = results[:20]
    except (GitHubError, ValueError, KeyError):
        row["readme_demo_links"] = []


def inspect_source(api, row, file_limit=15, hit_limit=16):
    name = slug_of(row["repo"])
    branch = row.get("default_branch") or "main"
    try:
        tree = api.get("/repos/" + name + "/git/trees/" + quote(branch, safe=""), {"recursive": 1})
        paths = [x for x in tree.get("tree", []) if x.get("type") == "blob"
                 and str(x.get("path", "")).endswith(EXTENSIONS)
                 and 0 < int(x.get("size") or 0) <= 180_000
                 and PATH_RX.search(x.get("path", ""))]
        paths.sort(key=lambda x: (0 if re.search("voice|tts|sovits|cosy|rvc", x["path"], re.I) else 1,
                                  x["path"].count("/"), x["path"]))
        hits = []
        for entry in paths[:file_limit]:
            file_path = entry["path"]
            content = api.get("/repos/" + name + "/contents/" + quote(file_path, safe="/"))
            if content.get("encoding") != "base64":
                continue
            decoded = base64.b64decode(content["content"]).decode("utf-8", errors="replace")
            for line_no, line in enumerate(decoded.splitlines(), 1):
                for kind, rx in SOURCE_RX.items():
                    if rx.search(line):
                        hits.append({"kind": kind, "path": file_path, "line": line_no,
                                     "excerpt": safe_excerpt(line),
                                     "url": f"https://github.com/{name}/blob/{quote(branch, safe='')}/{quote(file_path, safe='/')}#L{line_no}",
                                     "file_sha": content.get("sha")})
                    if len(hits) >= hit_limit:
                        break
                if len(hits) >= hit_limit:
                    break
            if len(hits) >= hit_limit:
                break
        row["implementation_sources"] = hits
        row["inspection"] = {"candidate_files": len(paths),
                              "files_scanned": min(len(paths), file_limit),
                              "truncated": bool(tree.get("truncated")) or len(paths) > file_limit,
                              "executed_third_party_code": False}
    except (GitHubError, ValueError, KeyError) as exc:
        row["inspection"] = {"error": str(exc), "truncated": True}
    readme_demo_links(api, row)
    return row


def adoption_index(row):
    sample = row.get("discussion_sample") or {}
    count = sample.get("top_issue_comments_sum")
    raw = 4 * math.log1p(row["stars"]) + 3 * math.log1p(row["forks"])
    if count is not None:
        raw += 1.5 * math.log1p(count)
    return round(raw, 3)


def write_reports(rows, discovery_record, output):
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    created = datetime.now(timezone.utc).isoformat()
    for index, row in enumerate(rows, 1):
        row["rank"] = index
        row["github_adoption_index"] = adoption_index(row)
    result = {
        "generated_at_utc": created, "ranking": "Stars desc, Forks desc, sampled issue comments desc. No subjective AI code-quality boost.",
        "discovery": discovery_record, "projects": rows,
        "limitations": [
            "GitHub search returns at most 1000 matches per query. Coverage cannot be called exhaustive.",
            "Open issues include PRs. Top issue comments are a sample and may be bots.",
            "External social post counts are not collected automatically. Missing != 0.",
            "Stars/Forks indicate reach or adoption, not proven naturalness, sales or successful deployment.",
            "Inspected code is a selected, partial subset; only source-linked details should be claimed."
        ],
    }
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Human-signal-first GitHub research", "",
             f"Generated UTC: {created}", f"Found before cap: {discovery_record['found_before_limit']}",
             f"Returned: {len(rows)}", "",
             "| # | Repository | Stars | Forks | Top issue comments | Real demo link |",
             "|---:|---|---:|---:|---:|---|"]
    for row in rows:
        sample = row.get("discussion_sample") or {}
        comments = sample.get("top_issue_comments_sum")
        counts = "not sampled" if comments is None else str(comments)
        social = row.get("external_social") or []
        refs = ", ".join("[" + str(x["platform"]) + "](" + x["url"] + ")" for x in social)
        if not refs:
            linked = row.get("readme_demo_links") or []
            refs = (", ".join("[README link](" + x["url"] + ")" for x in linked[:2]) +
                    " (unverified)" if linked else "not collected")
        lines.append(f"| {row['rank']} | [{row['repo']}]({row['url']}) | {row['stars']:,} | {row['forks']:,} | {counts} | {refs} |")
    lines += ["", "## Source code entry points (do not affect popularity rank)", ""]
    for row in rows:
        if row.get("implementation_sources"):
            lines.append("**" + row["repo"] + "**")
            for hit in row["implementation_sources"][:6]:
                lines.append("- " + hit["kind"] + ": [" + hit["path"] + ":" + str(hit["line"]) + "](" + hit["url"] + ")")
    lines += ["", "## Limits", ""]
    lines += ["- " + note for note in result["limitations"]]
    if discovery_record.get("errors"):
        lines += ["", "Partial API errors:"] + ["- " + x for x in discovery_record["errors"][:12]]
    target.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", action="append", help="Repeat for distinct search families")
    parser.add_argument("--seed", action="append", default=[], help="Explicit owner/repo or GitHub URL")
    parser.add_argument("--require", action="append", default=[],
                        help="Mechanical feature regex gate (repeated terms must ALL occur in repo metadata/README)")
    parser.add_argument("--social-file", help="Externally observed social demo URLs and numeric engagement")
    parser.add_argument("--require-code", action="append", choices=sorted(SOURCE_RX),
                        default=[], help="Require source-linked functional marker before ranking (repeatable)")
    parser.add_argument("--code-screen-top", type=int, default=20,
                        help="Maximum popularity-ranked candidates to source-screen, default 20")
    parser.add_argument("--per-query", type=int, default=20)
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--limit", type=int, default=60)
    parser.add_argument("--discussion-top", type=int, default=10)
    parser.add_argument("--inspect-top", type=int, default=5)
    parser.add_argument("--output", default="human-signal-results.json")
    args = parser.parse_args(argv)
    if not (1 <= args.per_query <= 100 and 1 <= args.pages <= 3
            and 1 <= args.limit <= 300 and 0 <= args.discussion_top <= 100
            and 0 <= args.inspect_top <= 100):
        parser.error("Arguments out of bounds")
    queries = args.query or QUERIES
    if len(queries) > 20:
        parser.error("Use at most 20 search queries per run")
    api = GitHubAPI()
    # Scan more than the final output cap so high-star unrelated repos do not
    # crowd out actual implementations before the objective feature gate.
    screening_cap = min(300, max(args.limit * 4, 80)) if args.require else args.limit
    rows, discovery_record = discovery(api, queries, args.seed, per_query=args.per_query,
                                        pages=args.pages, limit=screening_cap)
    rows = filter_required_features(api, rows, args.require, discovery_record)
    rows = sorted(rows, key=adoption_key)[:args.limit]
    if args.require_code:
        if not (1 <= args.code_screen_top <= 80):
            parser.error("--code-screen-top must be 1..80")
        screened = rows[:args.code_screen_top]
        for row in screened:
            inspect_source(api, row, file_limit=20, hit_limit=80)
        survivors = [
            row for row in screened
            if all(kind in {hit["kind"] for hit in row.get("implementation_sources", [])}
                   for kind in args.require_code)
        ]
        discovery_record["code_required"] = args.require_code
        discovery_record["code_screened"] = len(screened)
        discovery_record["code_matched"] = len(survivors)
        discovery_record["code_not_screened_due_budget"] = max(0, len(rows)-len(screened))
        # Functional eligibility is binary. Popularity still determines order.
        rows = sorted(survivors, key=adoption_key)[:args.limit]
    attach_social(rows, load_social(args.social_file))
    for row in rows[:args.discussion_top]:
        sample_issues(api, row)
    for row in rows[:args.inspect_top]:
        if "inspection" not in row:
            inspect_source(api, row)
    rows.sort(key=adoption_key)
    write_reports(rows, discovery_record, args.output)
    print(json.dumps({"projects": len(rows), "github_calls": api.calls,
                      "remaining_rate_limit": api.remaining,
                      "report": args.output, "markdown": str(Path(args.output).with_suffix('.md'))}))
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main())
