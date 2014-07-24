#!/usr/bin/env python

import web #http://webpy.org
import git #https://pypi.python.org/pypi/GitPython/

import logging
import json
import subprocess
import os
import sys
import shutil

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
            files.append(file)

    return files

def run_makefiles(directories):
    for directory in directories:
        if os.path.exists(directory + "/Makefile"):
            print "Running makefile in: " + directory
            os.system("make -C " + directory)
            
def collect_compiled_files(directories):
    compiled_files = []
    for directory in directories:
        for file in os.listdir(directory):
            if file.endswith(".pdf"):
                print "File: " + file
                compiled_files.append(directory + "/" + file)
                
    return compiled_files

def pull_repo(path):
    repo = git.Repo(path)
    origin = repo.remotes.origin
    origin.pull()


def run(data):

    parsed_data = json.loads(data)
    repo_name = parsed_data["repository"]["name"]
    pull_repo(REPO_BASE_PATH + repo_name)
    modified_files = get_files(parsed_data["commits"], "modified")
    added_files = get_files(parsed_data["commits"], "added")
    removed_files = get_files(parsed_data["commits"], "removed")
    
    changed_files = added_files + modified_files + removed_files
    unique_directories = []

    for file in changed_files:
        directory = os.path.dirname(file)
        found = False
        for unique_directory in unique_directories:
            if unique_directory == os.path.dirname(file):
                found = True
                break
        if found:
            found = False
        else:
            unique_directories.append(directory)
    
    #Append the repo path to all directory paths
    unique_directories = [REPO_BASE_PATH + repo_name + "/" + directory for directory in unique_directories]
    
    run_makefiles(unique_directories)
    
    compiled_files = collect_compiled_files(unique_directories)
       
    for file in files:
        if not os.path.exists(os.path.dirname(dest + file)):
            os.makedirs(os.path.dirname(dest + file))
            
        shutil.move(file, dest + file)

if __name__ == '__main__':
    print sys.argv
    if len(sys.argv) > 1:
        run(sys.argv[1])
    else:
	    app.run() #Used for testing.

