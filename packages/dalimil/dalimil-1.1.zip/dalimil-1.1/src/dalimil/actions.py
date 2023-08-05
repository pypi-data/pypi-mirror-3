'''
Created on 5.11.2010

@author: javl
'''
from pprint import pprint
import tarfile
import zipfile
import shutil

import os


def do_list(archmanager):
    #Check for file name duplicates in archives
    list(archmanager, check_duplicates = True)
    return

def list_notimefiles(archmanager):
    print("==Files without detected time==")
    if len(archmanager.notimefiles) == 0:
        print("None found")
    else:
        pprint(archmanager.notimefiles)
    return

def list_duplicates(archmanager):
    print("==Files with duplicated names per archive")
    if len(archmanager.archs_with_duplicates) == 0:
        print("None found")
    else:
        pprint(archmanager.archs_with_duplicates)
    return

def list_skippedfiles(archmanager):
    #print files skipped due to skipping current and future archives
    print("==Files skipped as they belong to current and future archives==")
    if len(archmanager.skippedfiles) == 0:
        print("None found")
    else:
        pprint(archmanager.skippedfiles)
    return
    
def list(archmanager, check_duplicates = True):
    __doc__ = '''
    Lists files, gives option if check_duplicates is called on archmanager 
    '''
    if check_duplicates:           
        #Check for file name duplicates in archives
        archmanager.check_duplicates()
    
    #list files, which had no time detected
    list_notimefiles(archmanager)
    #print duplicates, if we care about it
    if check_duplicates:
        list_duplicates(archmanager)
            
    #print files skipped due to skipping current and future archives
    list_skippedfiles(archmanager)
    #print files per archive
    print("==Files to be archived per archive")
    if len(archmanager.archives) == 0:
        print("None found")
    else:
        pprint(archmanager.archives)
    return

def do_copy2dir(archmanager, delete = False):
    mode = "move" if delete else "copy"
    #Check for file name duplicates in archives
    archmanager.check_duplicates()
    ##TODO: list files which are notime or duplicates
    print("Files duplicated in container and files without detected time are always skipped:")
    list_duplicates(archmanager)
    list_notimefiles(archmanager)
    if len(archmanager.skippedfiles) > 0:
        list_skippedfiles(archmanager)
    print("==Moving/copying files==")
    for archname, files in archmanager.archives.items():
        try:
            if os.path.exists(archname):
                orgpath = archname
                archname = unique_filename(archname)
                print("Directory {orgpath} already exists, using modified name {newpath}".format(orgpath = orgpath, newpath = archname))
            os.makedirs(archname)
        except:
            print("Unable to create directory {0}".format(archname))
            continue
        for file in files:
            try:
                destfile = archname + "/" + os.path.split(file)[1]
                shutil.copy2(file, destfile)
                if delete:
                    os.remove(file)
                print("{stat}: {mode} {file} => {destfile}".format(stat = "OK", file = file, destfile = destfile, mode = mode))                
            except:
                print("{stat}: {mode} {file} => {destfile}".format(stat = "ERR", file = file, destfile = destfile, mode = mode))                
                continue
    return

def do_move2dir(archmanager):
    return do_copy2dir(archmanager, delete=True)

def do_move2zip(archmanager):
    return do_copy2zip(archmanager, delete=True)

def do_copy2zip(archmanager, delete = False):
    #Check for file name duplicates in archives
    archmanager.check_duplicates()
    ##TODO: list files which are notime or duplicates
    print("Files duplicated in container and files without detected time are always skipped:")
    list_duplicates(archmanager)
    list_notimefiles(archmanager)
    if len(archmanager.skippedfiles) > 0:
        list_skippedfiles(archmanager)
    print("==Copying files==")
    for archname, files in archmanager.archives.items():
        success = False
        if os.path.exists(archname):
            orgpath = archname
            archname = unique_filename(archname)
            print("Archive {orgpath} already exists, using modified name {newpath}".format(orgpath = orgpath, newpath = archname))
        try:
            archdir = os.path.split(archname)[0]
            if os.path.exists(archdir):
                pass
            else:
                os.makedirs(archdir)
        except:
            print("Unable to create directory {0}".format(archdir))
            continue
        try:
            zip = zipfile.ZipFile(archname, 'w')
            for file in files:
                zip.write(file, arcname = os.path.split(file)[1], compress_type = zipfile.ZIP_DEFLATED)
            print("OK: Archive created: {archive}".format(archive = archname))
            print("Following files were archived:")
            pprint(files)
            success = True
        except:
            print("ERROR: Unable to create archive {archive}".format(archive = archname))
            print("Hint: zlib module is told to be required for effective compression, if missing, we can fail.")
            print("Following files were skipped:")
            pprint(files)
        finally:
            zip.close()
        if delete and success:
            print("Deleting source files:")
            success = False
            for file in files:
                try:
                    os.remove(file)
                    success = True #Checking, if at least one file was succesfully deleted.
                except:
                    print("{stat}: Unable to delete file {file}".format(stat = "ERR", file = file))                
                    continue
            if success:
                print("..deleted.")                    
    return

def unique_filename(file_name):
    counter = 1
    file_name_parts = os.path.splitext(file_name)
    while os.path.exists(file_name): 
        file_name = file_name_parts[0] + '_' + str(counter) + file_name_parts[1]
        counter += 1
    return file_name


names = ['D:/var/projects/calrchive/testdata\\JSDI_NDIC_20100903_00000044.xml',
         'D:/var/projects/calrchive/testdata\\JSDI_NDIC_20100903_00000043.xml']
tar_archive = r"D:\var\projects\calrchive\testarchive\arch.tar.gz"
zip_archive = r"D:\var\projects\calrchive\testarchive\today/ttt/arch.zip"

def testTarGz(names, archive):
    try:
        tar = tarfile.open(archive, "w|gz")
        for name in names:
            tar.add(name, arcname = os.path.split(name)[1], recursive = True)
    finally:
        tar.close()
    return

if __name__ == '__main__':
    pass

# testZip(zip_archive, names, create_dirs = False, onExisting = "newName")

##Here we define dictionary of actions
def do_not_implemented_yet(archmanager):
    print "Action not implemented yet."
    return

do_move2targz = do_not_implemented_yet 
do_copy2targz = do_not_implemented_yet

actions = {"list": do_list,"move2dir": do_move2dir,"move2zip":do_move2zip,
           "move2targz":do_move2targz,"copy2dir":do_copy2dir, 
           "copy2zip":do_copy2zip, "copy2targz":do_copy2targz}
