import os


class BestAnalyzer:

    def __init__(self, file_name):
        self.file_name = file_name

    def printerror(self, linenum, code):
        msg = ""
        if (linenum and code) != "":

            if code == "S001":
                msg = "Too long"

            print(f"Line {linenum}: {code} {msg}")

    def checklen(self, line, linenum):
        if len(line) > 79:
            self.printerror(linenum, "S001")

    def checkcode(self):
        linenum = 1
        if not os.path.exists(self.file_name):
            raise FileNotFoundError

        with open(self.file_name) as fp:
            for line in fp.readlines():
                self.checklen(line, linenum)
                linenum += 1


user_file = input()
my_analyzer = BestAnalyzer(user_file)
my_analyzer.checkcode()
