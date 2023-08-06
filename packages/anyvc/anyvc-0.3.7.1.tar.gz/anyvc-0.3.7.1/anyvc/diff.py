"""
    anyvc diff tools

    :license: LGPL2 or later
"""
import itertools
import difflib

#XXX: those are a pile of hacks

def diff_for_file(commit, file):
    #XXX: propperly handle add/remove
    try:
        new = commit.file_content(file).splitlines(True)
    except: #XXX: ERRORS?!?!
        new = []

    if commit.parents:
        parent = commit.parents[0]
        try:
            old = parent.file_content(file).splitlines(True)
        except: #XXX: ERRORS?!?!
            old = []

    else:
        old = []

    #XXX: propperly handle lack of tailing \n
    #XXX: binaries ?!
    return difflib.unified_diff(old, new, file, file)

def diff_for_commit(commit):
    changed_files = commit.get_changed_files()

    return ''.join(
                item
                for file in changed_files
                for item in diff_for_file(commit, file)
            )
