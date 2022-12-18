import os
import re
import argparse


errors_dict = {"S001": "Too long",
               "S002": "Indentation is not a multiple of four",
               "S003": "Unnecessary semicolon",
               "S004": "At least two spaces required before inline comments",
               "S005": "TODO found",
               "S006": "More than two blank lines preceding a code line",
               "S007": "Too many spaces after 'class'",
               "S008": "Class name 'user' should use CamelCase",
               "S009": "Function name 'Print2' should use snake_case"}

exclude_list = ["__init__.py", "tests.py"]


class BestAnalyzer:

    def __init__(self, file_name):
        self.file_name = file_name
        self.curr_file = ""
        self.prev_line = ""
        self.blankline_cnt = 0
        self.errornum = 0
        self.filescount = 0
        self.log_data = {}

    def add_error(self, fname, linenum, code):
        if (linenum and code) != "":
            if code in errors_dict.keys():
                self.log_data[self.errornum] = [fname, linenum, code]
        self.errornum += 1

    def checklen(self, line, linenum):
        if len(line) > 79:
            self.add_error(self.curr_file, linenum, "S001")  # comment

    def check_comment_spaces(self, line, linenum):
        template = r"\S\s{0,1}#"
        if line.count("#") == 1:
            re_obj = re.search(template, line)
            if re_obj:
                self.add_error(self.curr_file, linenum, "S004")

    def check_ident_spaces(self, line, linenum):
        template = r"\S{1}"
        re_obj = re.split(template, line, maxsplit=1)
        if not len(re_obj[0]) % 4 == 0 and re_obj[0] != "\n" and line[0] != "#":
            self.add_error(self.curr_file, linenum, "S002")

    def check_semicolor(self, line, linenum):
        template = r"(\);+$|; {1,2}#)"
        re_obj = re.search(template, line)
        if re_obj:
            self.add_error(self.curr_file, linenum, "S003")

    def check_todo(self, line, linenum):
        template = "#{1,2}.+todo"
        re_obj = re.search(template, line, flags=re.IGNORECASE)
        if re_obj:
            self.add_error(self.curr_file, linenum, "S005")

    def check_blanklines(self, line, linenum):
        if line == "\n":
            self.blankline_cnt += 1
        else:
            if self.blankline_cnt > 2:
                self.add_error(self.curr_file, linenum, "S006")
            self.blankline_cnt = 0

    def check_classspaces(self, line, linenum):
        template = r"^class\s{2,}\w"
        re_obj = re.search(template, line)
        if re_obj:
            self.add_error(self.curr_file, linenum, "S007")

    def check_defspaces(self, line, linenum):
        template = r"def\s{2,}\w"
        re_obj = re.search(template, line)
        if re_obj:
            self.add_error(self.curr_file, linenum, "S007")

    def check_classcamels(self, line, linenum):
        template = r"^class\s{1,}[^A-Z][a-z]+([A-Z]|)"
        re_obj = re.search(template, line)
        if re_obj:
            self.add_error(self.curr_file, linenum, "S008")

    def check_functsnake(self, line, linenum):
        template = r"def ([A-Z]|[a-z]+[A-Z])"
        re_obj = re.search(template, line)
        if re_obj:
            self.add_error(self.curr_file, linenum, "S009")

    def checkcode(self):
        temp_list = []
        if not os.path.exists(self.file_name):
            raise FileNotFoundError

        if os.path.isdir(self.file_name):
            temp_list = [self.file_name+'\\'+fname for fname in os.listdir(self.file_name)
                         if fname.find(".py") > 1 and fname not in exclude_list]

        elif os.path.isfile(self.file_name):
            temp_list = [self.file_name]

        for one_file in temp_list:
            if os.path.getsize(one_file) > 0:
                self.curr_file = one_file.lower()
                self.filescount += 1
                linenum = 1
                with open(one_file) as fp:
                    for line in fp.readlines():
                        self.checklen(line, linenum)
                        self.check_comment_spaces(line, linenum)
                        self.check_ident_spaces(line, linenum)
                        self.check_semicolor(line, linenum)
                        self.check_todo(line, linenum)
                        self.check_blanklines(line, linenum)
                        self.check_classspaces(line, linenum)
                        self.check_defspaces(line, linenum)
                        self.check_classcamels(line, linenum)
                        self.check_functsnake(line, linenum)
                        linenum += 1

    def printallerrors(self):
        self.log_data = list(sorted(self.log_data.items(), key=lambda x: (x[1][0], x[1][1], x[1][2])))
        for elem in self.log_data:
            print(f"{elem[1][0]}: Line {elem[1][1]}: {elem[1][2]} {errors_dict[elem[1][2]]}")

    def print_statistics(self):
        print("Total error count:", len(self.log_data), "in", self.filescount, "file(s)")


arg_pars = argparse.ArgumentParser("The simplest Python code analyzer ever")
arg_pars.add_argument('file_directory', help='File or directory name to check')
user_argums = arg_pars.parse_args()

my_analyzer = BestAnalyzer(user_argums.file_directory)
my_analyzer.checkcode()
my_analyzer.printallerrors()
