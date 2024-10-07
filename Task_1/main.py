from src.console import Console
import csv
import threading
import tarfile


class BashFake:
    path = "/"
    config = {
        "file_system": "",
        "start_script": "",
    }

    def __init__(self):
        self.console = Console(self.cmd_processing)
        with open(r'C:\Users\slava\PycharmProjects\Configuration_management\Task_1\config.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                self.config[row[0]] = row[1]
        self.path = self.config["file_system"].replace(".tar", "") + "/"


    def _ls(self, append_path=""):
        path = self.get_path(append_path)
        elems = set()
        with tarfile.open(self.config["file_system"], "r") as tar:
            for member in tar.getmembers():
                if not member.name.startswith(path):
                    continue
                elems.add(member.name.split("/")[path.count("/")])
        return "\n".join(elems)

    def _cd(self, path):
        self.path = self.path.replace("//", "/")
        if type(path) != list:
            path = path.split("/")
        if path[0] == "" and len(path) > 1:
            self.path = "/".join(self.path.split("/")[:2]) + "/"
            return self._cd(path[1:])
        if path[0] == "" or path[0] == "-":
            self.path = self.config["file_system"].replace(".tar", "") + "/"
            return
        if path[0] == "..":
            if self.path == "./file_system/":
                return self._cd(path[1:])
            self.path = "/".join(self.path.split("/")[:-2]) + "/"
            return self._cd(path[1:])
        elif path[0] == ".":
            return self._cd(path[1:])
        else:
            with tarfile.open(self.config["file_system"], "r") as tar:
                for member in tar.getmembers():
                    if member.name == self.path + "/".join(path) and member.isdir():
                        break
                else:
                    return "No such directory"

            self.path += "/".join(path) + "/"
            self.path = self.path.replace("//", "/")

    def _touch(self, path):
        with tarfile.open(self.config["file_system"], "a") as tar:
            try:
                tar.addfile(tarfile.TarInfo(self.get_path(path)))
            except:
                return "Can't create file"

    def get_path(self, path):
        path = path.split("/")
        result_path = self.path
        if path[0] == "" and len(path) > 1:
            result_path = "./file_system/"
            path = path[1:]
        for elem in path:
            if elem == "..":
                result_path = "/".join(result_path.split("/")[:-2]) + "/"
            elif elem == ".":
                continue
            else:
                result_path += elem + "/"
            result_path = result_path.replace("//", "/")
        return result_path

    def cmd_processing(self, command):
        command = command.split(" ")
        match command[0]:
            case "ls":
                self.console.print(self._ls(command[1] if len(command) > 1 else ""))
            case "cd":
                try:
                    error = self._cd(command[1])
                except IndexError as IE:
                    error = self._cd("-")
                if error:
                    self.console.print(error)

                new_path = self.path.replace(
                    self.config["file_system"].replace(".tar", ""), "")
                self.console.set_path(new_path)
            case "touch":
                try:
                    error = self._touch(command[1])
                    if error:
                        self.console.print(error)
                except IndexError as IE:
                    self.console.print("No file name")
            case _:
                self.console.print("Unknown command")

        self.console.insert_prompt()

    def run_start_script(self):
        if self.config["start_script"]:
            script = open(self.config["start_script"], "r")
            self.console.insert_prompt()
            for line in script:
                line = line.strip()
                self.console.print(line)
                self.cmd_processing(line)
            script.close()

    def run(self):
        start_cmds = threading.Thread(target=self.run_start_script)
        start_cmds.start()
        self.console.run()


def main():
    not_bash = BashFake()
    not_bash.run()


if __name__ == "__main__":
    main()
