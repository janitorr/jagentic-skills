import unittest

from src.text import slugify, trim


class TestText(unittest.TestCase):
    def test_trim_removes_outer_whitespace(self):
        self.assertEqual(trim("  hello  "), "hello")


class TestSlugify(unittest.TestCase):
    def test_lowercases_text(self):
        self.assertEqual(slugify("Hello"), "hello")

    def test_trims_outer_whitespace(self):
        self.assertEqual(slugify("  Hello  "), "hello")

    def test_collapses_whitespace_runs_to_one_hyphen(self):
        self.assertEqual(slugify("A  B"), "a-b")

    def test_removes_punctuation(self):
        self.assertEqual(slugify(" Hello, World! "), "hello-world")

    def test_removes_underscore(self):
        self.assertEqual(slugify("snake_case"), "snakecase")

    def test_strips_boundary_hyphens(self):
        self.assertEqual(slugify("Hello !"), "hello")
        self.assertEqual(slugify("! Hello"), "hello")
