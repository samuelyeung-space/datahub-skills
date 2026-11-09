"""Offline tests for the public GitHub research CLI. No live API or QQ access."""
import base64
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import socialscan as scan


def item(name="human/voice", stars=3608, forks=226):
    return {
        "full_name": name, "html_url": "https://github.com/" + name,
        "stargazers_count": stars, "forks_count": forks,
        "default_branch": "main", "description": "real QQ voice TTS",
    }


class FakeGitHub:
    def __init__(self):
        self.requests = []

    def get(self, path, params=None):
        self.requests.append((path, params or {}))
        if path == "/search/repositories":
            return {"total_count": 2, "incomplete_results": False,
                    "items": [item(), item("tiny/pretty-readme", 1, 0)]}
        if path == "/repos/human/voice":
            return item()
        if path == "/search/issues":
            return {"total_count": 2, "items": [
                {"html_url": "https://github.com/human/voice/issues/1",
                 "comments": 11, "reactions": {"total_count": 7}},
                {"html_url": "https://github.com/human/voice/issues/2",
                 "comments": 5, "reactions": {"total_count": 2}},
            ]}
        if path == "/repos/human/voice/git/trees/main":
            return {"tree": [
                {"type": "blob", "path": "src/voice.py", "size": 200},
                {"type": "blob", "path": "secrets.env", "size": 50},
            ]}
        if path == "/repos/human/voice/contents/src/voice.py":
            code = "model = 'GPT-SoVITS'\nref_audio_path = 'file.wav'\nqq_send_voice(text)\n"
            return {"encoding": "base64",
                    "content": base64.b64encode(code.encode()).decode(),
                    "sha": "a123"}
        raise AssertionError("Unexpected API path: " + path)


class SocialProofTests(unittest.TestCase):
    def test_search_is_deduplicated_and_adoption_first(self):
        rows, meta = scan.discovery(FakeGitHub(),
                                    ['"QQ" "TTS"', '"OneBot" "voice"'],
                                    [], per_query=25, limit=30)
        self.assertEqual(meta["found_before_limit"], 2)
        self.assertEqual(rows[0]["repo"], "human/voice")
        self.assertEqual(rows[0]["stars"], 3608)
        self.assertGreaterEqual(len(rows[0]["discovery_routes"]), 2)

    def test_seeding_known_project_works(self):
        rows, meta = scan.discovery(FakeGitHub(), [], ["human/voice"])
        self.assertEqual(rows[0]["forks"], 226)
        self.assertEqual(meta["seed_count"], 1)

    def test_code_evidence_never_changes_adoption_rank(self):
        top = scan.summarized(item())
        tiny = scan.summarized(item("tiny/readme", 1, 0))
        tiny["implementation_sources"] = [{}] * 50
        self.assertLess(scan.adoption_key(top), scan.adoption_key(tiny))
        self.assertGreater(scan.adoption_index(top), scan.adoption_index(tiny))

    def test_discussion_is_comments_not_open_issues(self):
        row = scan.summarized(item())
        scan.sample_issues(FakeGitHub(), row)
        self.assertEqual(row["discussion_sample"]["top_issue_comments_sum"], 16)
        self.assertEqual(row["discussion_sample"]["top_issue_reactions_sum"], 9)
        self.assertEqual(row["open_issues_including_prs"], 0)

    def test_social_absence_is_not_zero(self):
        row = scan.summarized(item())
        scan.attach_social([row], {})
        self.assertEqual(row["external_social_status"], "not_collected")
        self.assertEqual(row["external_social"], [])

    def test_social_observations_need_real_host_and_numeric_values(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "social.json"
            file.write_text(json.dumps([
                {"repo": "human/voice", "url": "https://www.bilibili.com/video/BV12345678/",
                 "views": 5000, "likes": 100, "comments": 19}
            ]))
            social = scan.load_social(str(file))
            row = scan.summarized(item())
            scan.attach_social([row], social)
            self.assertEqual(row["external_social"][0]["views"], 5000)
            self.assertEqual(row["external_social_status"], "supplied_unverified")
            file.write_text(json.dumps([
                {"repo": "human/voice", "url": "https://bilibili.com.evil.com/watch",
                 "views": 99}
            ]))
            with self.assertRaises(ValueError):
                scan.load_social(str(file))

    def test_code_inspection_returns_real_file_line(self):
        row = scan.summarized(item())
        scan.inspect_source(FakeGitHub(), row)
        found = row["implementation_sources"]
        self.assertTrue(any(x["kind"] == "tts_model" for x in found))
        self.assertTrue(any(x["kind"] == "qq_delivery" for x in found))
        self.assertTrue(any(x["url"].endswith("#L3") for x in found))
        self.assertTrue(all("secrets.env" not in x["path"] for x in found))

    def test_repo_url_input_not_arbitrary_hosts(self):
        self.assertEqual(scan.slug_of("https://github.com/owner/repo/blob/main/README.md"),
                         "owner/repo")
        for value in ("../../file", "https://evil.invalid/owner/repo"):
            with self.assertRaises(ValueError):
                scan.slug_of(value)

    def test_report_is_generated_with_unknown_external_status(self):
        row = scan.summarized(item())
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "test.json"
            result = scan.write_reports([row], {"found_before_limit": 1, "errors": []}, str(output))
            self.assertEqual(result["projects"][0]["rank"], 1)
            self.assertIn("not collected", output.with_suffix(".md").read_text())
            self.assertEqual(json.loads(output.read_text())["projects"][0]["stars"], 3608)


if __name__ == "__main__":
    unittest.main()
