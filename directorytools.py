import re
from os import walk, getcwd, path, mkdir, unlink
from shutil import rmtree

default_dir = getcwd()

def file_by_name(file_name, directory=default_dir):
    file_list = files_by_name(file_name, directory)
    if file_list:
        return file_list[0]

def files_by_name(file_name, directory=default_dir):
    return find_files(re.compile(file_name), directory)
	
def file_by_extension(file_extension, directory=default_dir):
    file_list = files_by_extension(file_extension, directory)
    if file_list:
        return file_list[0]

def files_by_extension(file_extension, directory=default_dir):
    if not file_extension.startswith("."):
        file_extension = "." + file_extension
    return find_files(re.compile(".*\\" + file_extension), directory)

def file_by_partial(file_partial, directory=default_dir):
    file_list = files_by_partial(file_partial, directory)
    if file_list:
        return file_list[0]

def files_by_partial(file_partial, directory=default_dir):
    return find_files(re.compile(".*" + file_partial + ".*"), directory)

def find_files(regex, directory=default_dir):
    file_list = []

    for root, dirs, dirfiles in walk(directory):
        if root.find("/.") > 0: #hidden folders
            continue
        for name in dirfiles:
            if regex.match(name) and not name.startswith("."):
                file_list.append(root + name)
    if len(file_list) > 0:
        return file_list

def file_list(directory=default_dir):
    return find_files(re.compile(".*"), directory)

def folder_by_name(folder_name, directory=default_dir):
    folder_list = folders_by_name(folder_name, directory)
    if folder_list:
        return folder_list[0]

def folders_by_name(folder_name, directory=default_dir):
    return find_folders(re.compile(folder_name), directory)

def folder_by_partial(folder_partial, directory=default_dir):
    folder_list = folders_by_partial(folder_partial, directory)
    if folder_list:
        return folder_list[0]

def folders_by_partial(folder_partial, directory=default_dir):
    return find_folders(re.compile(".*" + folder_partial + ".*"), directory)

def find_folders(regex, directory=default_dir):
    folder_list = []
    for root, dirs, dirfiles in walk(directory):
        if root.find("/.") > 0: #hidden folders
            continue
        for dir_name in dirs:
            if regex.match(dir_name) and not dir_name.startswith("."):
                folder_list.append(root + "/" + dir_name)
    if len(folder_list) > 0:
        return folder_list

def folder_list(directory=default_dir):
    return find_folders(re.compile(".*"), directory)

def create_directory(directory):
    if not path.exists(directory):
        mkdir(directory)

def clear_directory(directory):
    if not path.exists(directory):
        return
    for root, dirs, files in walk(directory):
        for f in files:
            unlink(path.join(root, f))
        for d in dirs:
            rmtree(path.join(root, d))

def clear_or_create(directory):
    create_directory(directory)
    clear_directory(directory)

#add other directory name cleaning operations as they come up
def clean_dir_name(directory):
    if not directory.endswith("/"):
        return directory + "/"
