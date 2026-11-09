"""Local unit tests; do not require internet or API credentials."""
import importlib.util
import math
from pathlib import Path
import unittest

path=Path(__file__).with_name("scout.py")
spec=importlib.util.spec_from_file_location("scout",path)
scout=importlib.util.module_from_spec(spec)
spec.loader.exec_module(scout)

class TestHumanSignals(unittest.TestCase):
    def test_forks_and_stars(self):
        base={"stars":0,"forks":0,"archived":False,"social":[]}
        popular={**base,"stars":400,"forks":60}
        self.assertGreater(scout.popularity(popular),scout.popularity(base))

    def test_verified_social_only(self):
        base={"stars":0,"forks":0,"archived":False}
        unverified={**base,"social":[{"url":"https://example.com/a","metric":"views","count":100000,"verified":False}]}
        verified={**base,"social":[{"url":"https://example.com/a","metric":"views","count":100000,"verified":True}]}
        self.assertEqual(scout.popularity(unverified),scout.popularity({**base,"social":[]}))
        self.assertGreater(scout.popularity(verified),scout.popularity(unverified))

    def test_no_issues_as_comments(self):
        base={"stars":1,"forks":1,"archived":False,"social":[]}
        self.assertEqual(scout.popularity({**base,"issues_including_prs":10000}),scout.popularity(base))

if __name__=="__main__":unittest.main()
