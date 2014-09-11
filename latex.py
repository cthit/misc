#!/usr/bin/env python2
#
# Script that pulls changes from a gitrepo and compiles
# the latex files into PDF-files
#

import git  # https://pypi.python.org/pypi/GitPython/

import json
import os
import sys
import shutil
from optparse import OptionParser

REPO_BASE_PATH = ""
OUTPUT_DIRECTORY = ""


# Get all files from a series of commits in a category
# Categories are 'Added', 'Modified' and 'removed'
def get_files(commits, category):
    files = []
    for commit in commits:
        for file in commit[category]:
            files.append(file)

    return files


# Run the makefile in a list of directories.
def run_makefiles(directories):
    for directory in directories:
        if os.path.exists(directory + "/Makefile"):
            print "Running makefile in: " + directory
            os.system("make -C " + directory)


# Go through a list of directories and collect all pdf files in them.
def collect_compiled_files(directories):
    compiled_files = []
    for directory in directories:
        for file in os.listdir(directory):
            if file.endswith(".pdf"):
                print "File: " + file
                path = os.path.relpath(os.path.join(directory, file))
                compiled_files.append(path)

    return compiled_files


def pull_repo(path):
    repo = git.Repo(path)
    origin = repo.remotes.origin
    origin.pull()


# Returns a list with all directories that has a changed file in it.
def get_changed_directories(data):

    parsed_data = json.loads(data)
    repo_name = parsed_data["repository"]["name"]
    pull_repo(REPO_BASE_PATH + repo_name)

    commits = parsed_data["commits"]

    modified_files = get_files(commits, "modified")
    added_files = get_files(commits, "added")
    removed_files = get_files(commits, "removed")

    changed_files = added_files + modified_files + removed_files
    unique_directories = []

    for file in changed_files:
        #files = os.path.dirname(file)
        found = False
        for unique_directory in unique_directories:
            if unique_directory == os.path.dirname(file):
                found = True
                break
        if found:
            found = False
        else:
            unique_directories.append(os.path.dirname(file))

    #Append the repo path to all directory paths
    unique_directories = [os.path.join(REPO_BASE_PATH, repo_name, directory)
                          for directory in unique_directories]

    return unique_directories


# Go through all directories, run its makefile collect the compiled PDF-files
# and copy them to their destination.
def execute(directories):
    run_makefiles(directories)

    compiled_files = collect_compiled_files(directories)

    for file in compiled_files:
        file_destination = os.path.join(OUTPUT_DIRECTORY, file)
        if not os.path.exists(os.path.dirname(file_destination)):
            os.makedirs(os.path.dirname(file_destination))

        shutil.copy(file, file_destination)


# Run only when --first-run is an argument and it runs all makefiles in
# every directory no matter if any file has changed or not.
def handleFirstRun(repo_folder):
    os.chdir(REPO_BASE_PATH)
    pull_repo(os.path.join(REPO_BASE_PATH, repo_folder))

    directories = []
    for root, sub_folders, files in os.walk(repo_folder):
        for folder in sub_folders:
            folder = os.path.join(os.path.relpath(root), folder)
            directories.append(folder)

    execute(directories)


# Executes the normal flow of the script.
def run(data):
    directories = get_changed_directories(data)
    execute(directories)


if __name__ == '__main__':
    parser = OptionParser(description="Compile LaTeX files to PDF-files")
    parser.add_option('-f', '--first-run', dest="firstrun", metavar="REPO_FOLDER",
                      help='use when this script is run for the first time. Argument: repo folder')
    parser.add_option('-r', '--repo-path', dest="repo_base_path",
                      default="/home/kerp/Desktop/",
                      help='the path to the GIT-repo to read from')
    parser.add_option('-o', '--output', dest="output",
                      default="/var/www/core/wp-content/uploads/styrit/",
                      help='where to put the compiled files')
    options, args = parser.parse_args(sys.argv[1:])

    REPO_BASE_PATH = options.repo_base_path
    OUTPUT_DIRECTORY = options.output

    os.chdir(REPO_BASE_PATH)
    if options.firstrun:
        handleFirstRun(options.firstrun)
    else:
        if len(args) != 1:
            print "Invalid amount of arguments supplied. Expected 1 JSON argument"
        else:
            run(args[0])
