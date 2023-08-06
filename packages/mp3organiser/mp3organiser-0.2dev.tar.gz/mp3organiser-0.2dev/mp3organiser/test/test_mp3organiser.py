import unittest

import mp3organiser


class TestSession(unittest.TestCase):
    def setUp(self):
        pass

    def test_guess_artist_and_title(self):
        (certain, info) = mp3organiser.guess_artist_and_title('Artist - Title')
        self.assertTrue(certain)
        self.assertEqual(info, [{'artist': 'Artist', 'title': 'Title'}])

    def test_guess_artist_and_title_with_folder(self):
        (certain, info) = mp3organiser.guess_artist_and_title('Title',
                                                              'Artist/Album')
        self.assertTrue(certain)
        self.assertEqual(info,
                [{'artist': 'Artist', 'album': 'Album', 'title': 'Title'}])

    def test_guess_artist_and_title_folder_with_one_level(self):
        (certain, info) = mp3organiser.guess_artist_and_title('Title',
                                                              'Artist/')
        self.assertTrue(certain)
        self.assertEqual(info,
                [{'artist': 'Artist', 'title': 'Title'}])

    def test_guess_artist_and_title_with_unnormalised_folder(self):
        (certain, info) = mp3organiser.guess_artist_and_title('Title',
                                                             './Artist/Album/')
        self.assertTrue(certain)
        self.assertEqual(info,
                [{'artist': 'Artist', 'album': 'Album', 'title': 'Title'}])

    def test_guess_artist_and_title_folder_and_hypen(self):
        (certain, info) = mp3organiser.guess_artist_and_title('A - Title',
                                                              'Artist/Album')
        self.assertFalse(certain)
        self.assertEqual(info,
                [{'artist': 'Artist', 'album': 'Album', 'title': 'Title'},
                 {'artist': 'Artist', 'album': 'Album', 'title': 'A - Title'},
                 {'artist': 'A', 'title': 'Title'}])

    def test_guess_artist_and_title_with_no_hypen(self):
        (certain, info) = mp3organiser.guess_artist_and_title('Artist Title I')
        self.assertFalse(certain)
        self.assertEqual(info, [{'artist': 'Artist', 'title': 'Title I'}])

    def test_get_args(self):
        args = mp3organiser.get_args(['abc', 'def'])
        self.assertEqual(['abc', 'def'], args.locations)

    def test_get_args_tag_and_force_tag(self):
        try:
            mp3organiser.get_args(['--tag', '--force-tag', 'abc'])
            self.assertTrue(False, 'Shouldn\'t have got past the arg parse')
        except:
            self.assertTrue(True, 'argparse threw an exception')
