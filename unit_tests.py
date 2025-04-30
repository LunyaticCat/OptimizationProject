import unittest
import json
import os

class TestAllJsonOutputs(unittest.TestCase):

    def compare_json(self, expected, actual, path="root"):
        if isinstance(expected, dict):
            for key in expected:
                self.assertIn(key, actual, f"Missing key '{path}.{key}'")
                self.compare_json(expected[key], actual[key], f"{path}.{key}")
            for key in actual:
                self.assertIn(key, expected, f"Unexpected key '{path}.{key}'")
        elif isinstance(expected, list):
            self.assertEqual(len(expected), len(actual), f"List length mismatch at '{path}': expected {len(expected)}, got {len(actual)}")
            for i, (e, a) in enumerate(zip(expected, actual)):
                self.compare_json(e, a, f"{path}[{i}]")
        elif isinstance(expected, float):
            self.assertAlmostEqual(expected, actual, places=6, msg=f"Float mismatch at '{path}': expected {expected}, got {actual}")
        else:
            self.assertEqual(expected, actual, f"Value mismatch at '{path}': expected {expected}, got {actual}")

    def test_all_json_files(self):
        reference_dir = "references"
        result_dir = "results"

        for filename in os.listdir(reference_dir):
            if filename.endswith(".json"):
                with self.subTest(file=filename):
                    ref_path = os.path.join(reference_dir, filename)
                    res_path = os.path.join(result_dir, filename)
                    self.assertTrue(os.path.exists(res_path), f"Missing result file for {filename}")

                    with open(ref_path, "r") as f:
                        expected = json.load(f)
                    with open(res_path, "r") as f:
                        actual = json.load(f)

                    self.compare_json(expected, actual, path=filename)