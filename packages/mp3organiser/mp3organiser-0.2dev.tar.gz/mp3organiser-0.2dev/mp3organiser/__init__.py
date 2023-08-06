import argparse
import sys

from mp3organiser import *

VERSION = '0.2dev'


def get_args(sysargs):
    parser = argparse.ArgumentParser(description=("""
    Shows and updates info about mp3 files.

    Tags your mp3 files either automatically by guessing the artist and title
    from the file name and location, or manually by interactively querying user
    input. If no option is given then show the info about the files.
    """))
    parser.add_argument('locations', nargs='*', default=['./'],
                help='The mp3 file(s) or folder(s) of mp3 files to organise')
    tag_group = parser.add_mutually_exclusive_group()
    tag_group.add_argument('--tag', '-t', action='store_true',
                help='Tags mp3 files that don\'t already have tag info')
    tag_group.add_argument('--force-tag', '-f', action='store_true',
                help='Tag mp3s even if they already have tag info')
    tag_group.add_argument('--interactive-tag', '-i', action='store_true',
                help='Don\'t guess tags; ask the user to input each tag')
    tag_group.add_argument('--info', action='store_true',
                help='Show metadata info for mp3s')
    tag_group.add_argument('--noop', action='store_true',
                help='Don\'t tag the files; print what would have happened')
    tag_group.add_argument('--normalise', action='store_true',
                help='Set the files ID3v1 to the same as the ID3v2 tags')
    parser.add_argument('--version', action='store_true',
                help='Print the version')
    return parser.parse_args(sysargs)


def main(sysargs=None):
    sysargs = sysargs or sys.argv[1:]
    args = get_args(sysargs)

    if args.version:
        print VERSION
    else:
        for location in args.locations:
            for (filename, dirname) in get_mp3_list(location):
                if dirname and os.path.isdir(location):
                    full_target = os.path.join(location, dirname, filename)
                else:
                    full_target = location

                # If info is set or no other arg is explicitly set to True
                if args.info or\
                   not [i for i,v in args.__dict__.iteritems() if v is True]:
                    print get_tags(full_target)
                elif args.normalise:
                    filepath = os.path.join(location, dirname, filename)
                    print 'Normalising %s' % filepath
                    normalise_tags(filepath)
                else:
                    tags = not args.force_tag and get_tags(full_target)
                    if args.interactive_tag or (not tags or\
                       'title' not in tags or 'artist' not in tags):
                        if args.interactive_tag:
                            certain, info = False, []
                        else:
                            certain, info = \
                                    guess_artist_and_title(filename, dirname)

                        if not certain and not args.noop:
                            print 'Not sure of info for %s' % full_target
                            confirmed_info = ask_user_for_info(info)
                        else:
                            confirmed_info = info[0]

                        if args.noop:
                            print 'Would have set %s to %s' \
                                    % (full_target, confirmed_info)
                        else:
                            print 'Setting MP3 tag info on %s to %s' \
                                % (filename, confirmed_info)
                            add_tags(full_target, confirmed_info)
                    else:
                        print '%s already has a title and artist' % full_target
