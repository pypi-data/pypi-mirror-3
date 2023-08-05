#!/usr/bin/env python

import os
import re
import subprocess
import logging
import logging.handlers
import shutil
import sys
import argparse
import cPickle as pickle
import atexit

import settings

logger = logging.getLogger("AutoExtractor")
logger.setLevel(logging.INFO)

class AutoExtractor(object):

    def __init__(self, folder_ignore, filename_ignore, rar_file_match, main_rar_file_match, start_fresh, debug):
        self.folder_ignore = folder_ignore
        self.filename_ignore = filename_ignore
        self.rar_file_match = rar_file_match
        self.main_rar_file_match = main_rar_file_match
        self.start_fresh = start_fresh
        self.home_path = os.path.expanduser("~/.AutoExtractor")
        self.lock_file = os.path.join(self.home_path, "running.pid")
        self.processed_file = os.path.join(self.home_path, "processed.p")
        self.log_file = os.path.join(self.home_path, "process.log")

        if not os.path.exists(self.home_path):
            os.makedirs(self.home_path)

        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        if(debug):
            logger.setLevel(logging.DEBUG)
            ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

    def process(self, src_root, dest_root, overwrite):

        self.acquire_lock()
        
        processed = set()
        
        errors = []
              
        try:
          
            if os.path.exists(self.processed_file) and not self.start_fresh:
                logger.info("Loading previously processed file list")
                processed = pickle.load(open(self.processed_file, "rb"))

            elif self.start_fresh:
                logger.info("Starting fresh - Processing all files")
            
            else:
                logger.info("Processed file doesn't exists - Processing all files")

            logger.info("Processing files in: {0}".format(src_root))

            for path, dirs, files in os.walk(os.path.abspath(src_root)):
            
                for file_name in files:
                
                    src_file = os.path.join(path, file_name)
                    src_relative_path = os.path.relpath(path, src_root)
                    src_relative_file = os.path.join(src_relative_path, file_name)
                    parent_folder = os.path.basename(path)
                    dest_path = os.path.join(dest_root, src_relative_path)
                    dest_file = os.path.join(dest_path, file_name)
                    
                    if src_relative_file in processed:
                        logger.info("Skipping previously processed file: {0}".format(src_relative_file))
                        continue
                    
                    if re.match(self.folder_ignore, parent_folder, flags=re.IGNORECASE):
                        logger.debug("{0} matched folder ignore".format(src_relative_path))
                        continue

                    if re.match(self.filename_ignore, file_name, flags=re.IGNORECASE):
                        logger.debug("{0} matched filename ignore".format(file_name))
                        continue
                        
                    try:

                        if re.match(self.rar_file_match, file_name):
                            if self.unrar(src_file, dest_path, overwrite):
                                processed.add(src_relative_file)
                                
                        else:
                            if not os.path.isfile(dest_file) or overwrite:
                                logger.info("Copying {0} to {1}".format(file_name, dest_path))

                                if not os.path.exists(dest_path):
                                    os.makedirs(dest_path)

                                shutil.copy(src_file, dest_path)
                            else:
                                logger.info("Skipping {0} - File already exists and not overwriting".format(src_file))

                            processed.add(src_relative_file)

                    except Exception, e:
                        errors.append((src_file, e))
                    
        except Exception, e:
                logger.info("Error {0}".format(e))
                
        finally:
            if len(processed) > 0:
                logger.info("Saving processed file list")
                pickle.dump(processed, open(self.processed_file, "wb" ) )
                
            if len(errors) > 0:
                logger.error("{0} errors".format(len(errors)))

                for error in errors:
                    logger.error("Error processing {0}".format(error[0]))


    def unrar(self, src_file, dest_path, overwrite):

        overwrite_option = "-o-"

        file_name = os.path.basename(src_file)

        if re.match(self.main_rar_file_match, file_name, flags=re.IGNORECASE):
            logger.debug("Extracting rar archive {0} to {1}".format(file_name, dest_path))

            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

            if overwrite:
                overwrite_option = "-o+"

            unrar = subprocess.Popen(["unrar", "x", "-kb", overwrite_option, src_file, dest_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            results = unrar.communicate()

            if unrar.returncode != 0 and (unrar.returncode != 1 or overwrite == True):
                raise Exception("Error running unrar for: {0} {1}".format(src_file, results[0], results[1], unrar.returncode))

            if unrar.returncode == 1 and overwrite != True:
                logger.info("Skipping {0} - File already exists and not overwriting".format(src_file))

        else:
            logger.debug("{0} is not the main archive file - Ignoring".format(file_name))
            return False
            
        return True

    def check_lock(self):
        if os.path.exists(self.lock_file):
            return True
        return False

    def acquire_lock(self):
        logger.debug('AutoExtractor started (PID: %s)' % os.getpid())

        if self.check_lock():
            logger.warning("Another instance is running or a stale lock file exists at {0}".format(self.lock_file))
            sys.exit(1)

        f = file(self.lock_file, 'w')
        f.write('PID: %s\n' % os.getpid())
        f.close()
        atexit.register(self.release_lock)

    def release_lock(self):
        logger.info('AutoExtractor stopped (PID: %s)' % os.getpid())

        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)
            logger.debug('Removed %s' % self.lock_file)
        else:
            logger.debug('Lock file %s not found' % self.lock_file)        


def main():

    # unrar command location?
    # settings file

    parser = argparse.ArgumentParser(description='File copy and extract')
    parser.add_argument('-s', '--source', dest='source_path', help='Source folder')
    parser.add_argument('-d', '--dest', dest='dest_path', help='Destination folder', required=True)
    parser.add_argument('-f', '--folder-ignore', default=settings.FOLDER_IGNORE, dest='folder_ignore', help='Ignore folders that match this regular expression')
    parser.add_argument('-i', '--filename-ignore', default=settings.FILENAME_IGNORE, dest='filename_ignore', help='Ignore filenames that match this regular expression')
    parser.add_argument('-r', '--rar-file-match', default=settings.RAR_FILE_MATCH, dest='rar_file_match', help='Match rar files with this regular expression')
    parser.add_argument('-m', '--main-rar-file-match', default=settings.MAIN_RAR_FILE_MATCH, dest='main_rar_file_match', help='Match the main rar file with this regular expression')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', dest='debug', help='Output debug information')
    parser.add_argument('-o', '--overwrite', default=False, action='store_true', dest='overwrite', help='Overwrite existing files')
    parser.add_argument('-c', '--reset', default=False, action='store_true', dest='start_fresh', help='Forgets everything that has been processed')
    
    args = parser.parse_args()

    extractor = AutoExtractor(args.folder_ignore, args.filename_ignore, args.rar_file_match, args.main_rar_file_match, args.start_fresh, args.debug)
    
    extractor.process(args.source_path, args.dest_path, args.overwrite)

if __name__ == '__main__':
    main()
