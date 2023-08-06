#!/usr/bin/python
#
# A module to help organise mp3 files. Automatically or manually tag mp3 files
#
# NOTE: I take no responsibility for this module making a mess of your files.
#       Use at your own risk!!

import mutagen
import re
import os
import sys

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3


def add_tags(filename, tags):
    """Add tags to a mp3 file"""
    m = MP3(filename, ID3=EasyID3)
    try:
        m.add_tags(ID3=EasyID3)
    except mutagen.id3.error:
        # Already had tags
        pass

    m.update(tags)
    # Save with v1=2 so ID3v1 tags will be create and/or updated
    m.save(v1=2)


def get_tags(filename):
    """Get a dict of tags from a mp3 file"""
    m = MP3(filename, ID3=EasyID3)
    return dict(m.items())


def normalise_tags(filename):
    """Gets the existing tags off a file and resaves with both ID3v1 & ID3v2"""
    tags = get_tags(filename)
    add_tags(filename, tags)


def guess_artist_and_title(title, parent_dir=''):
    """
    Guess the artist and title. Usually "Artist - Song title"

    The returned info will have the best match first and so on

    :return (certain, [{'artist': <artist>, 'title': <title>},..]
    """
    title = re.sub(r'.mp3', '', title)
    parent_dir = os.path.normpath(parent_dir)
    guesses = []
    certain = True

    dirs = parent_dir.split(os.path.sep)
    if len(dirs) and dirs[0] != os.path.curdir:
        split_title = title.split('-')
        split_title.reverse()
        if len(dirs) > 1:
            guess = {'artist': dirs[-2], 'album': dirs[-1],
                            'title': split_title[0].strip()}
        else:
            guess = {'artist': dirs[0], 'title': split_title[0].strip()}

        guesses.append(guess)

        # If - is in the title then add it as the second most likely guess
        if '-' in title:
            guess = dict(guess)
            guess['title'] = title
            guesses.append(guess)

    match = re.search(r'([^-]*)-(.*)', title)
    if not match and not guesses:
        # We're not too sure; let's just take the first word as the artist and
        # return False to indicate we're uncertain
        certain = False
        match = re.search(r'([^ ]*) (.*)', title)

    if match:
        artist, song_title = match.groups()
        guesses.append({'artist': artist.strip(), 'title': song_title.strip()})

    # If there's not exactly one guess then we're not certain!
    return (certain and len(guesses) == 1, guesses)


def get_mp3_list(target, strip_target=True):
    """Get the specified mp3 file or a list of mp3s in a folder"""
    mp3_files = []
    if target.endswith('.mp3') and os.path.exists(target):
        mp3_files = [(os.path.basename(target), os.path.dirname(target))]
    else:
        for (parent_dir, dirs, files) in os.walk(target):
            if strip_target:
                parent_dir = re.sub(
                    '^%s%s' % (os.path.normpath(target), os.path.sep), '',
                    os.path.normpath(parent_dir))
            mp3_files.extend(
                    [(f, os.path.normpath(parent_dir))
                     for f in files if f.endswith('.mp3')])
    return mp3_files


def ask_user_for_info(info):
    """
    Interactively ask the user to pick one of a list of infos or input the file
    details themselves
    """
    confirmed_info = None
    for i in info:
        print 'Is this the correct song info?\n%s' % i
        if 'y' in sys.stdin.readline():
            confirmed_info = i
            break

    if not confirmed_info:
        confirmed_info = {}
        print 'Artist? ',
        confirmed_info['artist'] = \
                sys.stdin.readline().strip('\n')
        print 'Title? ',
        confirmed_info['title'] = \
                sys.stdin.readline().strip('\n')

    return confirmed_info
