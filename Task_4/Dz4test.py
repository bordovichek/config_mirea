import unittest
import csv
from Dz4 import assemble, interpret


class TestAssembler(unittest.TestCase):

    def test_load_const(self):
        with open("test_program.txt", "w") as f:
            f.write("LOAD_CONST 0 10\n")
        assemble("test_program.txt", "test_output.bin", "test_log.csv")
        with open("test_output.bin", "rb") as f:
            instruction = int.from_bytes(f.read(7), byteorder="big")
        self.assertEqual(instruction, (2 << 49) | (0 << 38) | (10 << 12))

    def test_shift_right(self):
        with open("test_program.txt", "w") as f:
            f.write("SHIFT_RIGHT 0 0 1\n")
        assemble("test_program.txt", "test_output.bin", "test_log.csv")
        with open("test_output.bin", "rb") as f:
            instruction = int.from_bytes(f.read(7), byteorder="big")
        self.assertEqual(instruction, (15 << 49) | (0 << 38) | (0 << 12) | 1)

    def test_load_memory(self):
        with open("test_program.txt", "w") as f:
            f.write("LOAD_MEMORY 0 1\n")
        assemble("test_program.txt", "test_output.bin", "test_log.csv")
        with open("test_output.bin", "rb") as f:
            instruction = int.from_bytes(f.read(7), byteorder="big")
        self.assertEqual(instruction, (14 << 49) | (0 << 38) | (1 << 12))

    def test_store_memory(self):
        with open("test_program.txt", "w") as f:
            f.write("STORE_MEMORY 0 1 2\n")
        assemble("test_program.txt", "test_output.bin", "test_log.csv")
        with open("test_output.bin", "rb") as f:
            instruction = int.from_bytes(f.read(7), byteorder="big")
        self.assertEqual(instruction, (10 << 49) | (0 << 38) | (1 << 12) | 2)

    def test_shift_left(self):
        with open("test_program.txt", "w") as f:
            f.write("SHIFT_LEFT 0 1 1\n")
        assemble("test_program.txt", "test_output.bin", "test_log.csv")
        with open("test_output.bin", "rb") as f:
            instruction = int.from_bytes(f.read(7), byteorder="big")
        self.assertEqual(instruction, (16 << 49) | (0 << 38) | (1 << 12) | 1)

    def test_interpret(self):
        with open("test_program.txt", "w") as f:
            f.write("LOAD_CONST 0 10\n")
            f.write("LOAD_MEMORY 1 0\n")
            f.write("SHIFT_RIGHT 1 0 1\n")
            f.write("SHIFT_LEFT 1 0 1\n")
        assemble("test_program.txt", "test_output.bin", "test_log.csv")
        interpret("test_output.bin", "test_result.csv", 0, 14)
        with open("test_result.csv", "r") as result_file:
            reader = csv.reader(result_file)
            result = list(reader)

        self.assertEqual(result[1], ['0', '10'])


if __name__ == "__main__":
    unittest.main()
