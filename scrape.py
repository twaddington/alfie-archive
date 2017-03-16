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

def last_page_in_archive():
    last_page_url = None

    with open(ARCHIVE_FILE, 'r') as fd:
        for line in fd:
            last_page_url, _ = line.strip().split(',')
    return last_page_url

def fetch_image(s, image_url, filename):
    image_file = os.path.join(ARCHIVE_DIR, filename)

    if os.path.isfile(image_file):
        return

    # Write to stdout
    uprint(image_url)
    uprint('  writing to {file}...'.format(filename))

    with open(image_file, 'wb') as fd:
        r = s.get(image_url, stream=True)

        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

def download_images_from_archive():
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
            # todo better filename?
            filename = 'Alfie_{index:04}_{path}.jpg'.format(index=index,
                    path=path_for_filename)
            fetch_image(s, image_url, filename)

            # Increment the index
            index += 1

def get_image_url_from_soup(soup):
    """
    """
    return soup.find(id='comic').img['src']

def get_next_page_from_soup(soup):
    """
    """
    try:
        next_page_url = soup.find_all('a',
                class_='comic-nav-next')[0]['href']
    except:
        next_page_url = None

    return next_page_url

def map_archive(page_url, skip_first=False):
    with open(ARCHIVE_FILE, 'a') as fd:
        s = requests.Session()

        while page_url is not None:
            r = s.get(page_url)

            # Parse the response
            soup = BeautifulSoup(r.text, 'html.parser')

            # Find the image URL
            image_url = get_image_url_from_soup(soup)

            # Find the next page URL
            next_page_url = get_next_page_from_soup(soup)

            if skip_first:
                skip_first = False
            else:
                # Append the URLs to the archive file
                fd.write(','.join((page_url, image_url)) + '\n')

                # Write to stdout
                uprint(page_url)
                uprint('  ' + image_url)

                # Append the page and image URLs to the archive file
                fd.write(','.join((page_url, image_url)) + '\n')

            # Increment to the next page and continue
            page_url = next_page_url

def main():
    if os.path.isfile(ARCHIVE_FILE):
        uprint('Adding new pages to archive...')
        map_archive(last_page_in_archive(), skip_first=True)
    else:
        uprint('Building site archive...')
        map_archive(ARCHIVE_URL_START)

    uprint('Fetching images...')
    download_images_from_archive()

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit()
