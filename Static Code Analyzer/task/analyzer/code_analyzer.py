import os
import re
import argparse
import ast


errors_dict = {"S001": "Too long",
               "S002": "Indentation is not a multiple of four",
               "S003": "Unnecessary semicolon",
               "S004": "At least two spaces required before inline comments",
               "S005": "TODO found",
               "S006": "More than two blank lines preceding a code line",
               "S007": "Too many spaces after 'class' or 'func'",
               "S008": "Class name 'X===X' should use CamelCase",
               "S009": "Function name 'X===X' should use snake_case",
               "S010": "Argument name 'X===X' should be written in snake_case",
               "S011": "Variable 'X===X' should be written in snake_case",
               "S012": "The default argument value is mutable"}


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

    def add_error(self, fname, linenum, code, wrongplacename=""):
        if (linenum and code) != "":
            if code in errors_dict.keys():
                self.log_data[self.errornum] = [fname, linenum, code, wrongplacename]
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

    def ast_funsnake(self, tree):
        """ S009 : Check if function snake_case """
        # print(ast.dump(tree))
        for item in ast.walk(tree):
            if isinstance(item, ast.FunctionDef) and item.name[0:2] != "__":
                template = r"_?[a-z]{1,}(_?[a-z]{1,}){0,}"
                re_obj = re.match(template, item.name)
                if not re_obj:
                    self.add_error(self.curr_file, item.lineno, "S009", item.name)

    def ast_argsnakecase(self, tree):
        """ S010 : Check if func arg is snake_case """
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for elem in node.args.args:
                    if not elem.arg.islower():
                        self.add_error(self.curr_file, elem.lineno, "S010", elem.arg)


    def ast_varsnakecase(self, tree):
        """ S011 : Check if var is snake_case """
        names_list = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.id not in names_list:
                    names_list.append(node.id)
                    if not node.id.islower():
                        self.add_error(self.curr_file, node.lineno, "S011", node.id)

    def ast_argmutable(self, tree):
        """ S012: Check default argument value is mutable """
        var_list = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for elem in node.args.args:
                    if elem.arg != "self":
                        var_list.append(elem.arg)
                for cnt, elem in enumerate(node.args.defaults):
                    if isinstance(elem, (ast.List, ast.Dict, ast.Set)):
                        self.add_error(self.curr_file, elem.lineno, "S012", var_list[cnt])
                var_list.clear()

    def check_code_classic(self, fp):  # check via RegExp
        linenum = 1
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
            linenum += 1

    def check_code_ast(self, tree):  # check via AST lib
        self.ast_funsnake(tree)
        self.ast_argsnakecase(tree)
        self.ast_argmutable(tree)
        self.ast_varsnakecase(tree)


    def checkcode(self):
        temp_flist = []
        if not os.path.exists(self.file_name):
            raise FileNotFoundError

        if os.path.isdir(self.file_name):
            temp_flist = [self.file_name + '\\' + fname for fname in os.listdir(self.file_name)
                          if fname.find(".py") > 1 and fname not in exclude_list]

        elif os.path.isfile(self.file_name):
            temp_flist = [self.file_name]

        for one_file in temp_flist:
            if os.path.getsize(one_file) > 0:
                self.curr_file = one_file.lower()
                self.filescount += 1
                # classic RegExp check
                with open(one_file) as fp:
                    self.check_code_classic(fp)

                # advanced AST check
                with open(one_file) as fp:
                    tree = ast.parse(fp.read())
                    self.check_code_ast(tree)


    def printallerrors(self):
        self.log_data = list(sorted(self.log_data.items(), key=lambda x: (x[1][0], x[1][1], x[1][2])))
        for elem in self.log_data:
            log_string = f"{elem[1][0]}: Line {elem[1][1]}: {elem[1][2]} {errors_dict[elem[1][2]]}"
            print(log_string.replace("X===X", elem[1][3]))

    def print_statistics(self):
        """Print statistic, error count and files count"""
        print("Total error count:", len(self.log_data), "in", self.filescount, "file(s)")



arg_pars = argparse.ArgumentParser("The simplest Python code analyzer ever")
arg_pars.add_argument('file_directory', help='File or directory name to check')
user_argums = arg_pars.parse_args()

my_analyzer = BestAnalyzer(user_argums.file_directory)
my_analyzer.checkcode()
my_analyzer.printallerrors()
