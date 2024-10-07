import tarfile
import unittest
from Task_1.main import BashFake


class TastBashFake(unittest.TestCase):
    def setUp(self):
        self.not_bash = BashFake()

    def test_ls_normal(self):
        result = self.not_bash._ls()
        self.assertIn("home", result)
        self.assertIn("etc", result)

    def test_ls_empty(self):
        self.not_bash._cd("empty")
        result = self.not_bash._ls()
        self.assertEqual("", result)

    def test_ls_with_path(self):
        result = self.not_bash._ls("home/user")
        self.assertIn("file.txt", result)
        self.assertIn("file2.txt", result)

    def test_cd_valid(self):
        self.not_bash._cd("empty")
        self.assertEqual(self.not_bash.path, "./file_system/empty/")

    def test_cd_invalid(self):
        result = self.not_bash._cd("invalid_dir")
        self.assertEqual(result, "No such directory")

    def test_cd_to_root(self):
        self.not_bash.path = "./file_system/home/user/"
        self.not_bash._cd("/")
        self.assertEqual(self.not_bash.path, "./file_system/")

    def test_touch_create_file(self):
        self.not_bash.path = "./file_system/"
        self.not_bash._touch("new_file.txt")
        with tarfile.open(self.not_bash.config["file_system"], "r") as tar:
            self.assertTrue("new_file.txt" in [member.name for member in tar.getmembers()])

    def test_touch_no_args(self):
        self.not_bash.path = "./file_system/"
        self.assertEqual(self.not_bash._touch(""), "No file name")


if __name__ == "__main__":
    unittest.main()
