#!/usr/bin/env python3
"""Public-only question reader. Does not download releases, run remote code or require credentials."""
import argparse
import json
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse

INDEX = "https://raw.githubusercontent.com/samuel-resource-members/international-stem-members/main/catalog/index.json"
HOST = "raw.githubusercontent.com"
PREFIX = "/samuel-resource-members/international-stem-members/main/"

def validate_url(url):
    p = urlparse(url)
    if p.scheme != "https" or p.netloc != HOST or not p.path.startswith(PREFIX):
        raise ValueError("URL is outside the public question-bank copy")

class RestrictRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(request, fp, code, msg, headers, newurl)

OPENER = urllib.request.build_opener(RestrictRedirect)

def fetch_text(url, max_bytes=4000000):
    validate_url(url)
    request = urllib.request.Request(url, headers={"User-Agent":"AIHandoutSkill/1.0"})
    with OPENER.open(request, timeout=18) as response:
        content = response.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise ValueError("Resource exceeds the small-file limit")
    return content.decode("utf-8-sig")

def fetch_json(url):
    return json.loads(fetch_text(url))

def find_course(index, course):
    return next((c for c in index.get("courses", [])
                 if str(c.get("course_id", "")).casefold() == course.casefold()), None)

def select_papers(course_data, year, group, limit):
    items = course_data.get("papers", [])
    if year is not None:
        items = [p for p in items if str(p.get("year")) == str(year)]
    if group:
        items = [p for p in items if group.casefold() in str(p.get("group", "")).casefold()]
    return items[:limit]

def select_questions(paper_data, keyword, limit):
    items = paper_data.get("questions", [])
    if keyword:
        needle = keyword.casefold()
        fields = ("problem_type", "search_text", "knowledge_point", "chapter", "display")
        items = [q for q in items if needle in
                 " ".join(str(q.get(k) or "") for k in fields).casefold()
                 or any(needle in str(tag).casefold() for tag in (q.get("topic_tags") or []))]
    return items[:limit]

def run(args):
    if args.check:
        args.course, args.year, args.group, args.keyword = "AMC10", 2023, "2023a", None
        args.limit, args.max_papers = 1, 1
    index = fetch_json(INDEX)
    course = find_course(index, args.course)
    if not course:
        return {"status":"COURSE_NOT_FOUND", "course":args.course}
    papers = select_papers(fetch_json(course["file"]), args.year, args.group, args.max_papers)
    out = []
    for paper in papers:
        for q in select_questions(fetch_json(paper["file"]), args.keyword, args.limit):
            md_url = q.get("question_file") or ""
            text = fetch_text(md_url, max_bytes=1000000) if md_url else ""
            ocr = q.get("search_text") or ""
            out.append({
                "id":q.get("id"), "question_file":md_url,
                "year":q.get("year"), "paper":q.get("paper"), "number":q.get("question_number"),
                "problem_type":q.get("problem_type"), "ocr_text":ocr[:4000],
                "text_file_read":bool(text), "QUESTION_TEXT_OK":bool(ocr),
                "original_files":[x.get("url") for x in q.get("files") or []],
                "answer_candidates":q.get("answer_candidates") or [],
                "ORIGINAL_CHECKED":False, "ANSWER_CHECKED":False
            })
    return {"status":"TEXT_FOUND_SOURCE_UNVERIFIED" if out else "NO_MATCHES",
            "INDEX_OK":True, "course":args.course, "papers_read":len(papers), "questions":out}

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--course", default="AMC10")
    parser.add_argument("--year", type=int)
    parser.add_argument("--group")
    parser.add_argument("--keyword")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--max-papers", type=int, default=4)
    args = parser.parse_args(argv)
    if not (1 <= args.limit <= 20 and 1 <= args.max_papers <= 20):
        parser.error("limits must be 1–20")
    try:
        result = run(args)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError,
            ValueError, RuntimeError, KeyError) as error:
        print(json.dumps({"status":"ERROR", "reason":str(error)},ensure_ascii=False),file=sys.stderr)
        return 3
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["status"] == "TEXT_FOUND_SOURCE_UNVERIFIED" else 1

if __name__ == "__main__":
    raise SystemExit(main())
