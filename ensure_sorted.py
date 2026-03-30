#!/bin/python3
import re

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Category:
    """Represents a category of apps in the README.md file."""
    def __init__(self, name):
        """
        Initializes a Category object.

        Args:
            name (str): The name of the category.
        """
        self.name = name
        # a list of apps
        self.apps = []

    def add_app(self, app_str: str):
        """
        Extracts the app name from a markdown string and adds it to the category's app list.

        Args:
            app_str (str): The markdown string representing an app (e.g., "* [**App Name**](link)").
        """
        matches = re.findall("(?<=\[\\*\\*).*(?=\\*\\*\])", app_str)
        if len(matches) != 1:
            raise RuntimeError("These should be only one match")
        app_name = matches[0]
        # make it lower case and append it
        self.apps.append(app_name.lower())

    def is_sorted(self):
        """
        Checks if the apps within the category are sorted alphabetically.

        Returns:
            bool: True if apps are sorted, False otherwise.
        """
        # I know not effiencent
        return sorted(self.apps) == self.apps

    def where_unsorted(self):
        """
        Identifies and returns a message indicating the first app that is out of order.

        Returns:
            str: A formatted string showing the unsorted app, or None if sorted.
        """
        for i in range(1, len(self.apps)):
            if self.apps[i] < self.apps[i-1]:
                return f'App {bcolors.RED}{self.apps[i-1]}{bcolors.ENDC} is not in the correct order'

    def how_to_sort(self):
        """
        Compares the current app list with its sorted version to show differences.

        Returns:
            tuple: A tuple containing two lists: (sorted_apps, unsorted_apps).
                   Elements in these lists are formatted to highlight differences.
        """
        sorted_apps = sorted(self.apps)
        unsorted_apps = self.apps.copy()
        for i in range(len(sorted_apps)):
            if sorted_apps[i] != unsorted_apps[i]:
                # Color it
                sorted_apps[i] = f'{sorted_apps[i]}'
                unsorted_apps[i] = f'{unsorted_apps[i]}'

        return sorted_apps, unsorted_apps

    def __str__(self):
        return str(self.apps)

    def __repr__(self):
        return self.__str__()

def main():
    """
    Main function to read README.md, parse app categories, and check if apps are sorted.
    Prints unsorted categories and exits with a non-zero code if any are found.
    """
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
        # This is also a category
        elif lines[i].startswith("## –"):
            category_name = re.findall("(?<=##\\s–\\s).*?(?=\\s–)", lines[i])[0]
            category = Category(category_name)
            categories.append(category)
        # This is an app
        elif lines[i].startswith("*"):
            # The last category in the categories list is the one we're working on
            category = categories[-1]
            category.add_app(lines[i])

    all_sorted = True
    for i in categories:
        if not i.is_sorted():
            print(f'Category {bcolors.BLUE}{i.name}{bcolors.ENDC} is not sorted')
            print('    ' + i.where_unsorted())
            print('    Should be sorted as follows:')
            sorted, unsorted = i.how_to_sort()
            longest_str = len(max(unsorted, key=len))
            for j in range(len(sorted)):
                color = sorted[j] != unsorted[j]
                print(f'        {bcolors.RED if color else ""}{unsorted[j]}{bcolors.ENDC if color else ""}{((longest_str-len(unsorted[j]))+2) * " "}{bcolors.GREEN if color else ""}{sorted[j]}{bcolors.ENDC if color else ""}')
            all_sorted = False

    if not all_sorted:
        exit(2)

if __name__ == "__main__":
    main()