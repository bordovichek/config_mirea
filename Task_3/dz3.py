import json
import re
import sys


class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse(self, text):
        lines = iter(text.splitlines())
        parsed = {}
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line and not line.startswith("dict("):
                name, value = map(str.strip, line.split("=", 1))
                self.constants[name] = self._parse_value(value)
                continue
            if line.startswith("dict("):
                dict_lines = [line]
                open_brackets = 1
                while open_brackets > 0:
                    line = next(lines, "").strip()
                    if line.startswith("dict("):
                        open_brackets += 1
                    elif line.endswith(")"):
                        open_brackets -= 1
                    dict_lines.append(line)
                _, value = self._parse_dict(dict_lines)
                parsed.update(value)
                continue

            # Обработка массива
            if line.startswith("{"):
                value = self._parse_array([line])
                parsed.update(value)
                continue

            raise SyntaxError(f"Некорректный синтаксис: {line}")

        return parsed

    def _parse_dict(self, dict_lines):
        dict_content = "".join(dict_lines).strip()[5:-1].strip()
        entries = self._split_dict_entries(dict_content)
        result = {}
        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue
            if "=" not in entry:
                raise SyntaxError(f"Некорректная запись в словаре: {entry}")
            key, value = map(str.strip, entry.split("=", 1))
            if not re.match(r"[a-zA-Z]+", key):
                raise SyntaxError(f"Некорректное имя ключа словаря: {key}")
            result[key] = self._parse_value(value)
        return None, result

    def _split_dict_entries(self, dict_content):
        entries = []
        depth = 0
        current_entry = []
        for char in dict_content:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1

            if char == "," and depth == 0:
                entries.append("".join(current_entry).strip())
                current_entry = []
            else:
                current_entry.append(char)
        if current_entry:
            entries.append("".join(current_entry).strip())
        return entries

    def _parse_value(self, value):
        value = value.strip()
        if value.startswith("|") and value.endswith("|"):
            return self.constants.get(value[1:-1], value)
        if value.isdigit():
            return int(value)
        if value.startswith("[[") and value.endswith("]]"):
            return value[2:-2]
        if value.startswith("dict(") and value.endswith(")"):
            _, dict_value = self._parse_dict([value])
            return dict_value
        if value.startswith("{") and value.endswith("}"):
            return self._parse_array([value])
        return value

    def _parse_array(self, array_lines):
        array_content = "".join(array_lines).strip()[1:-1].strip()
        elements = array_content.split(".")
        return [self._parse_value(el.strip()) for el in elements if el.strip()]


def main():
    input_file = 'test_correct.conf'
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            config_text = file.read()

        parser = ConfigParser()
        parsed_data = parser.parse(config_text)
        print(json.dumps(parsed_data, ensure_ascii=False, indent=4))

    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file}' не найден.")
        sys.exit(1)
    except SyntaxError as e:
        print(f"Ошибка синтаксиса: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
