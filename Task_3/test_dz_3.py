import unittest
import os
from dz3 import ConfigParser


class TestConfigParser(unittest.TestCase):
    def setUp(self):
        # Создаем корректный файл .conf
        self.correct_file = "correct_input.conf"
        self.correct_content = """const = 42
dict(
    key1 = 100,
    key2 = |const|,
    key3 = dict(
        nested_key1 = 200,
        nested_key2 = [[Вложенный тест]]
    ),
    key4 = [[Тест]]
)
"""
        with open(self.correct_file, "w", encoding="utf-8") as f:
            f.write(self.correct_content)
        self.error_file = "error_input.conf"
        self.error_content = """const1 = 42
dict(
    key1 = 100
    key2 = |const1|
    key3 = dict(
        nested_key1 = 200,
        nested_key2 = [[Вложенный тест]]
    )
)
"""
        with open(self.error_file, "w", encoding="utf-8") as f:
            f.write(self.error_content)

    def tearDown(self):
        os.remove(self.correct_file)
        os.remove(self.error_file)

    def test_parse_correct_file(self):
        parser = ConfigParser()
        with open(self.correct_file, "r", encoding="utf-8") as f:
            config_text = f.read()

        parsed_data = parser.parse(config_text)

        expected_result = {
            "key1": 100,
            "key2": 42,
            "key3": {
                "nested_key1": 200,
                "nested_key2": "Вложенный тест"
            },
            "key4": "Тест"
        }
        self.assertEqual(parsed_data, expected_result)

    def test_parse_error_file(self):
        parser = ConfigParser()
        with open(self.error_file, "r", encoding="utf-8") as f:
            config_text = f.read()

        with self.assertRaises(SyntaxError):
            parser.parse(config_text)


if __name__ == "__main__":
    unittest.main()
