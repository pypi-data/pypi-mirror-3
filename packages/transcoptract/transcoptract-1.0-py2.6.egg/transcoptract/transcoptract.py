#!/usr/bin/env python

import os
import re
import subprocess
import logging
import logging.handlers
import shutil
import sys
import argparse
import transmissionrpc

import settings


#### Auto remove public torrents?

#handler = logging.handlers.SysLogHandler(address = '/dev/log')

logging.basicConfig()
logger = logging.getLogger("transcoptract")
#logger.addHandler(handler)

class TransCopTract(object):

    def __init__(self, host, port, username, password, folder_ignore, filename_ignore, rar_file_match, main_rar_file_match):

        logger.info("Host: " + host + ", Port: " + port + ", User: " + username + ", Password: " + password)

        self.transmission = transmissionrpc.Client(host, port=port, user=username, password=password)

        self.folder_ignore = folder_ignore
        self.filename_ignore = filename_ignore
        self.rar_file_match = rar_file_match
        self.main_rar_file_match = main_rar_file_match
        

    def log(self):
        return logging.getLogger(__name__)

    def process(self, torrent_ids, dest_root, overwrite):

        if(torrent_ids == None):
            torrent_ids = []

            torrents = self.transmission.list()
            
            for torrent_id in torrents:
                torrent_ids.append(torrent_id)

        logger.info("Processing torrents: " + torrent_ids)

        for current_torrent_id, torrent in self.transmission.info(torrent_ids).items():

            logger.info("Torrent Id: " + current_torrent_id)

            src_root = torrent.downloadDir

            if torrent.percentDone != 1.0:
                logger.debug(torrent.name + " is only " + torrent.perentDone * 100 + "% done - Skipping")
                continue

            logger.info("Torrent Name: " + torrent.name)
            
            for file_id, file in torrent.files().items():
                fullpath = os.path.join(src_root, file['name'])
                filename = os.path.basename(fullpath)
                path = os.path.dirname(fullpath)        
                
                if re.match(self.folder_ignore, os.path.basename(path), flags=re.IGNORECASE):
                    logger.debug(os.path.basename(path) + " matched folder ignore")
                    continue

                if re.match(self.filename_ignore, filename, flags=re.IGNORECASE):
                    logger.debug(filename + " matched filename ignore")
                    continue

                rel = os.path.relpath(path, src_root)

                try:

                    dest = os.path.join(dest_root, rel)

                    if not os.path.exists(dest):
                        os.makedirs(dest)

                    if re.match(self.rar_file_match, filename):
                        logger.debug("Extracting rar archive " + filename + " to " + dest)
                        self.unrar(os.path.join(path, filename), dest, overwrite)
                    else:
                        # the folder always exists so it's always skipped
                        if not os.path.exists(dest) or overwrite:
                            logger.debug("Copying " + filename + " to " + dest)
                            shutil.copy(os.path.join(path, filename), dest)

                except:
                    logger.error("Error processing " + filename + " error: ", sys.exc_info()[1])
                    raise
            
    def unrar(self, filepath, dest, overwrite):

        overwrite_option = "-o-"

        if re.match(self.main_rar_file_match, os.path.basename(filepath), flags=re.IGNORECASE):
            logger.debug(os.path.basename(filepath) + " identified as the main archive file - Extracting")

            if overwrite:
                overwrite_option = "-o+"

            unrar = subprocess.Popen(["unrar", "x", "-kb", overwrite_option, filepath, dest], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            results = unrar.communicate()

        else:
            logger.debug(os.path.basename(filepath) + " is not the main archive file - Ignoring")


def main():

    # make this check for env variables?

    parser = argparse.ArgumentParser(description='Transmission completed download copy and extract')
    parser.add_argument('-s', '--host', default=settings.HOST, dest='host', help='Transmission host')
    parser.add_argument('-x', '--port', default=settings.PORT, dest='port', help='Transmission port')
    parser.add_argument('-u', '--username', dest='username', help='Transmission username')
    parser.add_argument('-p', '--password', dest='password', help='Transmission password')
    parser.add_argument('-t', '--torrent', dest='torrent_id', help='Torrent id to process')
    parser.add_argument('-d', '--dest', dest='dest', help='Destination folder', required=True)
    parser.add_argument('-f', '--folder-ignore', default=settings.FOLDER_IGNORE, dest='folder_ignore', help='Ignore folders that match this regular expression')
    parser.add_argument('-i', '--filename-ignore', default=settings.FILENAME_IGNORE, dest='filename_ignore', help='Ignore filenames that match this regular expression')
    parser.add_argument('-r', '--rar-file-match', default=settings.RAR_FILE_MATCH, dest='rar_file_match', help='Match rar files with this regular expression')
    parser.add_argument('-m', '--main-rar-file-match', default=settings.MAIN_RAR_FILE_MATCH, dest='main_rar_file_match', help='Match the main rar file with this regular expression')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', dest='debug', help='Output debug information')
    parser.add_argument('-o', '--overwrite', default=False, action='store_true', dest='overwrite', help='Overwrite existing files')
    
    args = parser.parse_args()

    if(args.debug):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)  

    tct = TransCopTract(args.host, args.port, args.username, args.password, args.folder_ignore, args.filename_ignore, args.rar_file_match, args.main_rar_file_match)
    
    tct.process(args.torrent_id, args.dest, args.overwrite)

if __name__ == '__main__':
    main()
