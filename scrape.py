#!/usr/bin/python

import os
import sys
import requests

from urlparse import urlparse
from bs4 import BeautifulSoup

ARCHIVE_PATH = os.path.dirname(os.path.realpath(__file__))
ARCHIVE_FILE = os.path.join(ARCHIVE_PATH, 'archive.txt')
ARCHIVE_DIR = os.path.join(ARCHIVE_PATH, 'images')
ARCHIVE_URL_START = 'http://buttsmithy.com/archives/comic/p1'

def uprint(msg, newline=True, quiet=False):
    """
    Unbuffered print.
    """
    if not quiet:
        sys.stdout.write("%s%s" % (msg, "\n" if newline else ''))
        sys.stdout.flush()

def ensure_archive_dir():
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

def fetch_image(s, image_url, filename):
    image_file = os.path.join(ARCHIVE_DIR, filename)

    uprint(image_url)

    if os.path.isfile(image_file):
        uprint('  skipping...')
        return

    with open(image_file, 'wb') as fd:
        uprint('  fetching...', newline=False)
        r = s.get(image_url, stream=True)
        uprint('DONE')

        uprint('  saving...', newline=False)
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
        uprint('DONE')

def fetch_archive():
    ensure_archive_dir()

    with open(ARCHIVE_FILE, 'r') as fd:
        s = requests.Session()

        index = 1
        for line in fd:
            page_url, image_url = line.strip().split(',')

            # Get the path component
            path = urlparse(page_url).path

            # Sanitize URL path for filename
            path_for_filename = path.strip('/').split('/')[-1]

            # Build the image filename
            filename = 'Alfie_{index:04}_{path}.jpg'.format(index=index,
                    path=path_for_filename)
            fetch_image(s, image_url, filename)

            # Increment the index
            index += 1

def map_archive():
    with open(ARCHIVE_FILE, 'w') as fd:
        s = requests.Session()

        next_page_url = ARCHIVE_URL_START
        while next_page_url is not None:
            r = s.get(next_page_url)

            # Parse the response
            soup = BeautifulSoup(r.text, 'html.parser')

            # Find the image URL
            image_url = soup.find(id='comic').img['src']
            uprint(image_url)

            # Write the page and image URLs to the archive file
            fd.write(','.join((next_page_url, image_url)) + '\n')

            # Find the next page URL to fetch
            try:
                next_page_url = soup.find_all('a', class_='comic-nav-next')[0]['href']
                uprint(next_page_url)
            except:
                next_page_url = None

def main():
    if not os.path.isfile(ARCHIVE_FILE):
        map_archive()

    fetch_archive()

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit()
