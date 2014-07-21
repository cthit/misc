#!/usr/bin/env python

import web #http://webpy.org
import git #https://pypi.python.org/pypi/GitPython/

import logging
import json
import subprocess
import os
import sys

urls = ('/.*', 'Hooks')
app = web.application(urls, globals())

REPO_BASE_PATH = ""
COMPILED_FILES_DIR_PATH = "/var/www/core/wp-content/uploads/styrit/"

class Hooks:

    def POST(self):
        data = web.data()
        run(data)
        return "OK"


def get_files(commits, category):
    files = []
    for commit in commits:
        for file in commit[category]:
            if file.endswith(".tex"):
                files.append(file)

    return files

def compile_files(files):
    compiled_files = []
    print files
    for file in files:
        subprocess.call("pdftex", "-interaction=nonstopmode", file)
        name, ext = os.path.splitext(file)
        compiled_files.append(name + ".pdf")

    return compiled_files

def move_files(src, dest, files):
    for file in files:
        os.rename(src + file, dest + file)

def delete_files(dir, files):
    for file in files:
        os.remove(dir + file)


def pull_repo(path):
    repo = git.Repo(path)
    origin = repo.remotes.origin
    origin.pull()


def run(data):

    parsed_data = json.loads(data)
    repo_name = parsed_data["repository"]["name"]

    print "Name: " + repo_name
    modified_files = get_files(parsed_data["commits"], "modified")
    #print "Modified files: " + modified_files[0]
    added_files = get_files(parsed_data["commits"], "added")

    removed_files = get_files(parsed_data["commits"], "removed")

    pull_repo(REPO_BASE_PATH + repo_name)

   # compiled_files = compile_files(modified_files + added_files)
   
   # move_files(REPO_BASE_PATH + repo_name, COMPILED_FILES_DIR_PATH, compiled_files)




if __name__ == '__main__':
    print sys.argv
    if len(sys.argv) > 1:
        run(sys.argv[1])
    else:
	app.run() #Used for testing.

