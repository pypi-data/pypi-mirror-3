'''
Created on 5.11.2010

@author: Jan Vlcinsky (jan.vlcinsky@gmail.com)
'''
import argparse
import textwrap
import os
import glob
import string
import time, datetime
import actions
from pprint import pprint

# Archiver

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

def get_parameters(argv):
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent("""
    dalimil tool organizes files into time related containers (directories or archives).
    Note: This command never starts anything by itself, it runs only once per call.
    
    So called Dalimil wrote Chronicle of Dalimil, sorting past and current events.
    See http://en.wikipedia.org/wiki/Chronicle_of_Dalimil    
    """),
    epilog=textwrap.dedent("""   
    Files are selected using Unix shell like syntax using *, ?, [seq] and [!seq]
    Finally, files are placed container, which is archive file or end leaf directory.  
    Warning: File selection pattern can select files from multiple directories.
    If final container rejects storing duplicate names, duplicates are skipped.

    Time is detected from file modification or creation time, or decoded from filename.
    
    Resulting containers are defined by time formating pattern.
    
    Time formating patters for target path and container name:
    Defines path and file name, which can be created from related file time.
        %c Locale's appropriate date and time representation.
        %d Day of the month as a decimal number [01,31].
        %f Microsecond as a decimal number [0,999999], zero-padded on the left
        %H Hour (24-hour clock) as a decimal number [00,23].
        %j Day of the year as a decimal number [001,366].
        %m Month as a decimal number [01,12].
        %M Minute as a decimal number [00,59].
        %S Second as a decimal number [00,61].
        %U Week number of the year (Sunday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Sunday are considered to be in week 0.
        %w Weekday as a decimal number [0(Sunday),6].
        %W Week number of the year (Monday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Monday are considered to be in week 0.
        %y Year without century as a decimal number [00,99].
        %Y Year with century as a decimal number.
        %z UTC offset in the form +HHMM or -HHMM (empty string if the the object is naive).
        %Z Time zone name (empty string if the object is naive).
    For more and details see bottom of page http://docs.python.org/library/datetime.html
    Samples: pattern => resulting path + archive name:
        "archive/%Y-%m-%dT%H.zip" => "archive/2010-02-28T13.zip" 
        "archive/%Y/%m/%d.zip" => "archive/2010/02/28.zip" 
        "archive/%Y/week-%W.zip" => "archive/2010/week-10.zip"
    default value is:
        "archive/year-%Y/month-%m/%Y-%m-%d.zip" => "archive/year-2010/month-08/2010-08-28.zip"

    Containers contain flat structure without deeper directory tree.
    Source files can be finally deleted or left as they are.
    Use action list (default) to see expected result without endangering files.

    Existing containers are never touched, if they are found, *_1.* etc. is used.
    
    Reading command line parameters from file: write arguments into text file,
    each prefix and each value on separate lines like 
        ------(quotation of my.cfg start)
        -action
        movetozip
        D:\my files with spaces\\data\\2010-0[789]\\*.xml
        E:/other/location/data\\2010-0[789]\\*.xml
        (quotation of my.cfg end)------    
    Then from command line 
        dalimil -incomplete @my.cfg
    will read it.
    Mixing command line arguments and others from file(s) is possible.
    
    Examples:
    Dry test of archiving *.xml from current folder without touching the files
        dalimil *.xml
    
    Move the *.xml fles into subdir archive/year-2010/month-08/2010-08-28.zip etc.
    Current period are skipped
        dalimil -a move2zip *.xml
        
    Move there all files, including current period
        dalimil -a move2zip -incomplete *.xml
        
    Copy the *.xml files into dir structure without zipping (dirs keep the .zip extension)
        dalimil -a copy2dir *.xml

    Move the *.xml files into dir structure of style archive/year-2010/month-08/2010-08-28
        dalimil -a move2dir -d archive/year-%Y/month-%m/%Y-%m-%d *.xml
        
    Move to archives, detecting time of files from file names
    Expecting file names notes-201010251325_abc.xml
        dalimil -t pattern -p notes-%Y%m%d%H%M -a move2zip *.xml
    """
    ))
    

    parser.add_argument('-action', dest='action', default="list", 
                        choices=["list","move2dir","move2zip","move2targz","copy2dir", "copy2zip", "copy2targz"],
                        help=
        '''Defines action to do with files organized into time related containers. 
          (default: %(default)s)'''
        )
    parser.add_argument('-destination', dest='destination', 
                        default = "archive/year-%Y/month-%m/%Y-%m-%d.zip", help=
       '''Time formated pattern for resulting container 
       (default: %(default)s)'''
       )
    parser.add_argument('-time', dest='time_detection_method', 
                        default="modified", choices=["modified","pattern"],
                        help=
        '''Method, how time of file is detected,
         options: %(choices)s (default: %(default)s)'''
        )
    parser.add_argument('-pattern', dest='time_detection_pattern',
                        default = "%Y-%m-%dT%H_%M_%S", help=
        '''Pattern, detecting time from filename.
        Effective only, if -time_detection_method is "pattern".
        Path is ignored, first part of filename must fit, useless end of filename can be omitted. 
        (default: %(default)s))'''
        )
    parser.add_argument('-incomplete', dest='archive_incomplete_periods', action = "store_true",
                         default = False, help=
       '''Allows creation of containers for periods,
        which are not yet completed (default: %(default)s))'''
       )
    parser.add_argument('source', nargs='+', default="*", help=
       '''Unix shell pattern for selecting files to archive.
       (defaults to all files in current dir)'''
       )

    #parse_args might raise some exception, we let outer function to catch it.
    args = parser.parse_args(argv) if argv else parser.parse_args()
    return args

def main(argv = None):
    args = get_parameters(argv)
    print("{now} - Dalimil started.".format(now = datetime.datetime.now()))
    pprint(args)
    #find all file names
    sfiles = find_files(args.source)
    print("{now} - Files selected.".format(now = datetime.datetime.now()))
    #set proper time detector
    detector = TimeDetector(method = args.time_detection_method, pattern = args.time_detection_pattern)
    #create archive manager
    archmanager = ArchiveManager(destination = args.destination, 
                                 detector = detector,
                                 archive_incomplete_periods = args.archive_incomplete_periods,
                                 ctime = datetime.datetime.now())
    #for each file,
    for sfile in sfiles:
        archmanager.add_file(sfile) 
    print("{now} - Files sorted into time slots.".format(now = datetime.datetime.now()))
    #Now we call action. It is responsibility of action code to call
    # archmanager.check_duplicates(), if needed
    action_handler = actions.actions[args.action]
    action_handler(archmanager)
    print("{now} - Dalimil completed his Chronicle.".format(now = datetime.datetime.now()))

    return

def find_files(masks):
    allfiles = set()
    print(masks)
    for mask in masks:
        #we are not interested in archiving directories, only real files
        newset = set([fname for fname in glob.glob(mask) if os.path.isfile(fname)])        
        allfiles = allfiles.union(newset)
    return allfiles

class TimeDetector:
    __doc__ = '''
    Currently detects time only from filename, ignoring path
    '''
    method = ""
    pattern = ""
    
    def __init__ (self, method, pattern):
        self.method = method
        self.pattern = pattern
        if self.method == "modified":
            self.get_time = self.get_modified_time
        elif self.method == "created":
            self.get_time = self.get_created_time
        elif self.method == "pattern":
            #to make live easier, all slashes unified to forward one
            self.pattern.replace("\\", "/")
            #use only end part without path
            self.pattern = self.pattern.split("/")[-1]
            if (len(self.pattern) < 2) or (self.pattern.find('%') < 0):
                raise ValueError("Unusable value of pattern.")
            self.get_time = self.get_pattern_time
        else:
            raise ValueError("Invalid time detection method supplied.")
        return
    def get_modified_time(self, path):
        return os.path.getmtime(path)
    
    def get_created_time(self, path):
        return os.path.getctime(path)
    
    def get_pattern_time(self, path):
        #datetime.datetime.strptime("2010-11-03T12:25:12", "%Y-%m-%dT%H:%M:%S")
        #datetime.datetime.strptime("20101103122512", "%Y%m%d%H%M%S")
        #'{dateTime:%Y-%m-%d %H:%M:%S}'.format(dateTime=dt)
        #'Cesta JeDlouha {dateTime:%Y-%m-%d %H:%M:%S} a poradi take {ord}'.format(dateTime=dt, ord = 25)

        dateTime = None
        path = os.path.split(path)[1]
        while len(path) > 0:
            try:
                dateTime = datetime.datetime.strptime(path, self.pattern)
                dateTime = time.mktime(dateTime.timetuple())
                break
            except ValueError:
                path = path[:-1]
        return dateTime

class ArchiveManager:
    __doc__ = '''
    Manages all informatin related to planning archives creation.
    Keeps list of archives and all files to be added there.
    If some file doesnot allow time detection, it is ept in notimefiles
    '''
    destinaton = ""
    archives = {}
    archs_with_duplicates = {}
    notimefiles = []
    skippedfiles = []
    incomplete_archive = ""
    ctime = None
    archive_incomplete_periods = False
    def __init__(self, destination, detector, archive_incomplete_periods = False, ctime = None):
        __doc__ = '''
        destination is pattern, describing target archive name. It has form of strftime pattern.
        detector is instance of TimeDetector
        Set ctime to datetime.datetime.now() and files belonging to current time archive and future 
        will be skipped as we expect they will probably get some more data in future 
        '''
        self.destination = destination
        self.detector = detector
        self.archive_incomplete_periods = archive_incomplete_periods
        self.ctime = ctime
        #test, if provided destination pattern is usable to create some string
        try:
            res = self.get_arch_name(datetime.datetime.now())
            if len(res) <= 0:
                raise ValueError("Destination pattern is unusable for creating string.")
        except ValueError:
            print("Unable to create a string from destination pattern.")
            raise
        #if ctime set, we prepare data for skipping current incompleted archive
        if archive_incomplete_periods:
            pass #there is no need to do any tricks with times and archives to skip
        else: 
            #make sure, we have it in seconds
            ctime_type = type(self.ctime).__name__
            if ctime_type == 'datetime':
                self.ctime = time.mktime(self.ctime.timetuple())
            elif ctime_type == 'float':
                pass #this type we expect
            else:
                self.ctime = time.mktime()
            self.incomplete_archive = self.get_arch_name(self.ctime)
        return
        
    def get_arch_name(self, time):
        ttype = type(time).__name__
        if ttype == 'float':
            time = datetime.datetime.fromtimestamp(time)
        elif ttype != 'datetime':
            raise TypeError("Expecting type datetime")
        return time.strftime(self.destination)

    def add_file(self, path):
        __doc__ = '''
        Tries to add the file into archive manager
        If cannot detect time of file, places the path into notimefiles collection
        '''
        #detect related time
        try:
            ftime = self.detector.get_time(path)            
        except:
            # if cannot detect, move to notime collection
            print("Unable to detect time for {0}".format(path))
            self.notimefiles.append(path)
            return
        archname = self.get_arch_name(ftime)
        
        #hadle skipping future files and files for incomplete archive
        if self.archive_incomplete_periods:
            pass
        else:
            if (archname == self.incomplete_archive) or (ftime >= self.ctime):
#               print "File {0} belongs to skipped archive or into future, skipped".format(path)
                self.skippedfiles.append(path)
                return
        
        if archname not in self.archives:
            self.archives[archname] = []
        self.archives[archname].append(path)
        return archname
    def check_duplicates(self):
        __doc__ = '''
        for each archive checks, if there are any filename (no path) duplicates.
        If yes, these files are moved into another dictionary duplicates,
        where they are under key of archive all listed 
        '''
        dupl_count = 0
        for archname, files in self.archives.items():
            names = {}
            for file in files:
                path, name = os.path.split(file)
                if not name in names:
                    names[name] = [file]
                else:
                    names[name].append(file)
            #now in names are all short names with related long names listed
            #we will find short names having multiple long path entries - duplicates
            singles = []
            dupls = []
            dupl_count = dupl_count + len(dupls)
            for name, files in names.items():
                if len(files) == 1:
                    singles.append(files[0])
                else:
                    dupls.extend(files)
            #now remove duplicates from archive and put duplicates into archs_with_duplicates
            if len(dupls) > 0:
                self.archs_with_duplicates[archname] = dupls
            self.archives[archname] = singles
            #TODO: add option keep_empty and we may get emty archives/dirs created
            if len(singles) == 0:
                del self.archives[archname]
        return dupl_count

def test_it():
#    argline = "-a list -d arch/%Y/month-%m/day-%d/hour-%H-pack.tar.gz -t modified D:/var/projects/calrchive/testdata/* D:\var\TICEReports\JSDI data\bezne\2010-09"   
    argline = "@sources.txt"   
#    argline = "-h"   
    main(argline.split())
    return

#main(None)
#test_it()

if __name__ == '__main__':
    main(None)
