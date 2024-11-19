from unittest import TestCase
import src.utils.fitfile as fitf


class testFitfile(TestCase):

    def setUp(self):
        self.fit_file = 'daten/2024-11-18-12-10-49.fit'

    def test_list_of_frame_names(self):
        self.assertLess(1, len(fitf.list_of_frame_names(self.fit_file)))
        self.assertIn('record', fitf.list_of_frame_names(self.fit_file))

    def test_get_alle_frames_mit_namen(self):
        self.assertLess(1, len(fitf.get_alle_frames_mit_namen(self.fit_file, 'record')))

    def test_get_alle_fieldnames_of_frames(self):
        self.assertLess(1, len(fitf.get_alle_fieldnames_of_frames(self.fit_file, 'record')))
        self.assertIn('heart_rate', fitf.get_alle_fieldnames_of_frames(self.fit_file, 'record'))
        self.assertIn('temperature', fitf.get_alle_fieldnames_of_frames(self.fit_file, 'record'))
        self.assertIn('timestamp', fitf.get_alle_fieldnames_of_frames(self.fit_file, 'record'))
