#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Antti Kurittu
#
# Install:
# pip install requests ssdeep bs4
#
# Usage:
# Add URL: python3 flinch.py -a http://url
# Help: python3 flinch.py -h

import os
import sys
import requests
from bs4 import BeautifulSoup
import ssdeep
import time
import argparse
import json
from collections import OrderedDict

class c:
    HDR = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    G = '\033[92m'
    R = '\033[91m'
    D = '\033[90m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UL = '\033[4m'

def get_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        page_object = requests.get(url, headers=headers)
        status_code = str(page_object.status_code)
        if str(status_code)[0] == "2":
            status_code = c.G + status_code + c.END
        elif str(status_code)[0] == "4":
            status_code = c.Y + status_code + c.END
        elif str(status_code)[0] == "5":
            status_code = c.R + status_code + c.END
        data = [page_object.text.encode('utf8'), status_code, page_object.headers]
        return data
    except:
        #print("Error requesting page:", sys.exc_info()[0])
        return False

parser = argparse.ArgumentParser(description="Flinch.py watches URLs for changes using a fuzzy hashing algorithm (ssdeep). To reset an URL's baseline, add it again with -a. (C) Antti Kurittu 2017.")
parser.add_argument("-a",
                    "--add",
                    metavar='url',
                    type=str,
                    help="add an URL to watch, include http(s)://")

parser.add_argument("-r",
                    "--remove",
                    metavar='N',
                    type=int,
                    help="Remove an url from watchlist and quit, see reference numbers with --list.")

parser.add_argument("-l",
                    "--list",
                    help="List watched urls and quit",
                    action="store_true")

parser.add_argument("-u",
                    "--url",
                    metavar="reference",
                    type=int,
                    help="Check individual URL")

parser.add_argument("-c",
                    "--check",
                    help="Run watchlist and quit",
                    action="store_true")

parser.add_argument("-d",
                    "--headers",
                    help="Print HTTP response headers",
                    action="store_true")

parser.add_argument("-e",
                    "--head",
                    metavar="N",
                    type=int,
                    help="Show first n lines of HTML content")

arg = parser.parse_args()

if not len(sys.argv) > 1:
    arg.list = True

def main():
    if arg.url:
        arg.check = True

    print(c.BOLD + "Flinch.py - see -h for help and command line options\n" + c.END)

    # Read watchlist, create an empty list if file does not exist
    if os.path.exists('urls.txt'):
        f = open('urls.txt', 'r')
        urls = f.read()
        f.close()
    else:
        urls = "{}"

    urls = json.loads(urls, object_pairs_hook=OrderedDict)

    #Order items
    i = 0
    for url, entries in urls.items():
        i = i + 1
        urls[url]['reference'] = i

    # Add a new url to watch
    if arg.add:
        epoch_time = int(time.time())
        urls[arg.add] = {"reference": (len(urls) + 1), "added": str(epoch_time), "size": 0, "checked": str(epoch_time)}
        page = get_page(arg.add)
        if page is False:
            print("{0}Connection error: {1}{2}".format(c.R, arg.add, c.END))
            exit()
        soup = BeautifulSoup(page[0], "html.parser")
        page[0] = ''.join(soup.findAll(text=True))
        page_title = soup.title.string
        page_size = len(page[0])
        current_hash = ssdeep.hash(page[0])
        urls[arg.add]['hash'] = current_hash
        urls[arg.add]['size'] = page_size
        print(c.G + " + New url added: " + c.END + arg.add + " (" + current_hash + ")")

    #List or remove an url from the watchlist
    if arg.list or arg.remove:
        if arg.remove:
            for key, entries in urls.items():
                if int(entries['reference']) == int(arg.remove):
                    url_to_drop = key
                    print("[" + c.R + "X" + c.END + "]: " + key)
                    confirm = input("\nRemoving URL from watchlist. Are you sure? [Y/n] ")

                    if confirm[0].lower() == "n":
                        print("Aborting.")
                        exit()
            try:
                del urls[url_to_drop]
                i = 0
                for url, entries in urls.items():
                    i = i + 1
                    urls[url]['reference'] = i
            except NameError:
                print("Referenced url not found, see watchlist with --list")
                exit()

        print("Ref.\t{0}\t\t{1}\t{2}".format("URL".ljust(32), "Added".ljust(20), "Checked".ljust(20)))
        for key, entries in urls.items():
            print("[{0}{1}{2}]:\t{3}\t\t{4}\t{5}".format(c.G, entries['reference'], c.END, key[0:32].ljust(32),
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(entries['added']))),
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(entries['checked'])))))
    #Run checks
    if arg.check is True:
        for url, entries in urls.items():
            if arg.url and arg.url != entries['reference']:
                continue
            urls[url]['checked'] = int(time.time())
            page = get_page(url)
            if page is False:
                print(c.R + "Connection error. %s " + c.END) % url
                continue
            headlines = page[0].decode("utf-8").splitlines()
            soup = BeautifulSoup(page[0], "html.parser")
            page[0] = ''.join(soup.findAll(text=True))
            page_title = str(soup.title.string).replace('\r', '').replace('\n', '')
            ' '.join(page_title.split())
            page_size = len(page[0])
            size_difference = page_size - entries['size']
            if size_difference == 0:
                size_difference = ""
            elif size_difference > 0:
                size_difference = c.G + "(+" + str(size_difference) + ") " + c.END
            else:
                size_difference = c.R + "(" + str(size_difference) + ") " + c.END
            current_hash = ssdeep.hash(page[0])
            print(c.G + str(entries['reference']) + c.END + ": [HTTP " + str(page[1]) + "] " + url + ": " + c.BOLD + page_title + c.END + "")
            comparison_score = ssdeep.compare(entries['hash'], current_hash)
            if comparison_score == 100:
                print(c.G + "  ➤ Content identical [" + str(comparison_score) + "%]" + c.END + "\t\t[size " + str(page_size) + " " + str(size_difference) + "bytes]")
            elif 75 <= comparison_score <= 99:
                print(c.G + "  ➤ Content similar [" + str(comparison_score) + "%]" + c.END + "\t\t[size " + str(page_size) + " " + str(size_difference) + "bytes]")
            elif 50 <= comparison_score <= 74:
                print(c.Y + "  ➤ Content different [" + str(comparison_score) + "%]" + c.END + "\t\t[size " + str(page_size) + " " + str(size_difference) + "bytes]")
            elif 25 <= comparison_score <= 49:
                print(c.Y + "  ➤ Content very different [" + str(comparison_score) + "%]" + c.END + "\t\t[size " + str(page_size) + " " + str(size_difference) + "bytes]")
            elif 0 <= comparison_score <= 24:
                print(c.R + "  ➤ Content completely different [" + str(comparison_score) + "%]\t\t" + c.END + "[size " + str(page_size) + " " + str(size_difference) + "bytes]")
            if arg.headers is True:
                print(c.BOLD + "  HTTP RESPONSE HEADERS:" + c.END)
                for header, value in page[2].items():
                    print("    " + c.Y + header + c.END + ": " + value)
            if arg.head:
                print(c.BOLD + "  DOCUMENT HEAD (truncated to 80 characters):" + c.END)
                print("    ------------------------------------------------------------")
                i = 1
                while i <= arg.head:
                    print(c.D + "    " + headlines[i][0:80] + c.END)
                    i = i + 1
                print("    ------------------------------------------------------------")
    f = open('urls.txt', 'w')
    f.write(json.dumps(urls, sort_keys=True, indent=4, separators=(',', ': ')))
    f.close()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("Error: %s" % e)
