import os
import re

errors_dict = {"S001": "Too long",
               "S002": "Indentation is not a multiple of four",
               "S003": "Unnecessary semicolon",
               "S004": "At least two spaces required before inline comments",
               "S005": "TODO found",
               "S006": "More than two blank lines preceding a code line"}


class BestAnalyzer:

    def __init__(self, file_name):
        self.file_name = file_name
        self.prev_line = ""
        self.blankline_cnt = 0
        self.errornum = 0
        self.log_data = {}

    def add_error(self, linenum, code):
        if (linenum and code) != "":
            if code in errors_dict.keys():
                self.log_data[self.errornum] = [linenum, code]
        self.errornum += 1

    def checklen(self, line, linenum):
        if len(line) > 79:
            self.add_error(linenum, "S001")  # comment

    def check_comment_spaces(self, line, linenum):
        template = r"\S\s{0,1}#"
        if line.count("#") == 1:
            re_obj = re.search(template, line)
            if re_obj:
                self.add_error(linenum, "S004")

    def check_ident_spaces(self, line, linenum):
        template = r"\w{1}"
        re_obj = re.split(template, line, maxsplit=1)
        if not len(re_obj[0]) % 4 == 0 and re_obj[0] != "\n" and line[0] != "#":
            self.add_error(linenum, "S002")

    def check_semicolor(self, line, linenum):
        template = r"(\);+$|; {1,2}#)"
        re_obj = re.search(template, line)
        if re_obj:
            self.add_error(linenum, "S003")

    def check_todo(self, line, linenum):
        template = "#{1,2}.+todo"
        re_obj = re.search(template, line, flags=re.IGNORECASE)
        if re_obj:
            self.add_error(linenum, "S005")

    def check_blanklines(self, line, linenum):
        if line == "\n":
            self.blankline_cnt += 1
        else:
            if self.blankline_cnt > 2:
                self.add_error(linenum, "S006")
            self.blankline_cnt = 0

    def checkcode(self):
        linenum = 1
        if not os.path.exists(self.file_name):
            raise FileNotFoundError

        with open(self.file_name) as fp:
            for line in fp.readlines():
                self.checklen(line, linenum)
                self.check_comment_spaces(line, linenum)
                self.check_ident_spaces(line, linenum)
                self.check_semicolor(line, linenum)
                self.check_todo(line, linenum)
                self.check_blanklines(line, linenum)
                linenum += 1

    def printallerrors(self):
        self.log_data = list(sorted(self.log_data.items(), key=lambda x: (x[1][0], x[1][1])))
        for elem in self.log_data:
            print(f"Line {elem[1][0]}: {elem[1][1]} {errors_dict[elem[1][1]]}")


user_file = input()
my_analyzer = BestAnalyzer(user_file)
my_analyzer.checkcode()
my_analyzer.printallerrors()
