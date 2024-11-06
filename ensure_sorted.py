#!/bin/python3
import re

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Category:
    def __init__(self, name):
        self.name = name
        # a list of apps
        self.apps = []

    def add_app(self, app_str: str):
        matches = re.findall("(?<=\\[\\*\\*).*(?=\\*\\*\\])", app_str)
        if len(matches) != 1:
            raise "These should be only one match"
        app_name = matches[0]
        # make it lower case and append it
        self.apps.append(app_name.lower())

    def is_sorted(self):
        # I know not effiencent
        return sorted(self.apps) == self.apps

    def __str__(self):
        return str(self.apps)
    
    def __repr__(self):
        return self.__str__()

def main():
    readme_file = open('README.md', 'r')
    # start of the Apps section
    APPS_LINE_START = '## – Apps –\n'
    lines = readme_file.readlines()

    index: int
    try:
        index = lines.index(APPS_LINE_START)
    except ValueError:
        print(f'String "{APPS_LINE_START}" was not found in README.md it\'s needed to determine the start of the app categories')
        exit(1)

    categories = []
    for i in range(index+1, len(lines)):
        # This is a category
        if lines[i].startswith("### •"):
            category = Category(lines[i][6:-1])
            categories.append(category)
        # This is an app
        elif lines[i].startswith("*"):
            # The last category in the categories list is the one we're working on
            category = categories[-1]
            category.add_app(lines[i])

    all_sorted = True
    for i in categories:
        if not i.is_sorted():
            print(f'Category {bcolors.OKBLUE}{i.name}{bcolors.ENDC} is not sorted')
            all_sorted = False

    if not all_sorted:
        exit(2)
            

if __name__ == "__main__":
    main()