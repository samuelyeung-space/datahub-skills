import importlib.util
import unittest
from pathlib import Path

source = Path(__file__).parents[1] / "scripts" / "read_bank.py"
spec = importlib.util.spec_from_file_location("read_bank", source)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)

class ReaderTests(unittest.TestCase):
    def test_url_validation(self):
        bad = ["http://raw.githubusercontent.com/a",
               "https://raw.githubusercontent.com.evil.example/x",
               "file:///etc/passwd", "https://raw.githubusercontent.com/other/repo/main/thing"]
        for url in bad:
            with self.assertRaises(ValueError):
                reader.validate_url(url)
        reader.validate_url(reader.INDEX)

    def test_course(self):
        self.assertEqual(reader.find_course({"courses":[{"course_id":"AMC10"}]},"amc10")["course_id"],"AMC10")

    def test_papers(self):
        data = {"papers":[{"year":2023,"group":"amc-2023a"},{"year":2023,"group":"amc-2023b"}]}
        self.assertEqual(len(reader.select_papers(data,2023,"2023a",5)),1)

    def test_question_keyword(self):
        data = {"questions":[{"id":"a","search_text":"similar triangles"},{"id":"b","problem_type":"ratio"}]}
        self.assertEqual(reader.select_questions(data,"triangles",1)[0]["id"],"a")

if __name__ == "__main__":
    unittest.main()
