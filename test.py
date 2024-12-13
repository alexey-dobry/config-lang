import unittest
from translator import parse_config, generate_xml, ConfigError

class TestTranslator(unittest.TestCase):
    def test_constant_parsing(self):
        config = "var pi := 3.14159"
        parsed = parse_config(config)
        self.assertEqual(parsed, [
            {"type": "constant", "name": "pi", "value": 3.14159}
        ])

    def test_array_parsing(self):
        config = "var numbers := <<1, 2, 3>>"
        parsed = parse_config(config)
        self.assertEqual(parsed, [
            {"type": "constant", "name": "numbers", "value": [1, 2, 3]}
        ])

    def test_evaluation(self):
        config = """
        var g := 9.81
        ![g]
        """
        parsed = parse_config(config)
        self.assertEqual(parsed, [
            {"type": "constant", "name": "g", "value": 9.81},
            {"type": "evaluation", "name": "g", "value": 9.81}
        ])

    def test_invalid_syntax(self):
        config = "var pi = 3.14159"
        with self.assertRaises(ConfigError):
            parse_config(config)

    def test_undefined_constant(self):
        config = "![undefined]"
        with self.assertRaises(ConfigError):
            parse_config(config)

if __name__ == "__main__":
    unittest.main()
