from StringIO import StringIO
from testtools import TestCase

from txpkgme.scoreboard import (
    _clean_up_staging_data,
    _convert_internal_data,
    SubunitReporter,
    )


class TestSubunitReporter(TestCase):

    def test_extended_character_name(self):
        name = u'\u2603'
        app = {'name': name, 'myapps_id': 15}
        test = SubunitReporter(StringIO())._to_test(app)
        self.assertEqual('%s:15' % (name.encode('utf8'),), test.id())


class TestStagingRewrite(TestCase):

    def test_modified_arb(self):
        # Before a certain point (myapps ID 581 in actual staging data), we
        # want to rewrite all URLs to point to production, as that's where the
        # data comes from.
        data = {
            'package_url': (
                "http://developer.staging.ubuntu.com/site_media/arb/packages/"
                "2012/01/lonote_1.3.3_all.deb"),
            'myapps_id': 581,
            'arbitrary': 'fooey',
            }
        new_data = _clean_up_staging_data(data)
        data['package_url'] = (
            "http://myapps.developer.ubuntu.com/site_media/arb/packages/"
            "2012/01/lonote_1.3.3_all.deb")
        self.assertEqual(data, new_data)

    def test_modified_arb_icon(self):
        icons =  {
            '48x48': ('https://sc.staging.ubuntu.com/site_media/icons/'
                      '2012/01/lonote-128.png'),
            }
        data = {
            'package_url': (
                'https://developer.staging.ubuntu.com/internal_packages/2011/'
                '05/example_1.1.0_with_valid_control.tar_.gz'),
            'myapps_id': 581,
            'arbitrary': 'fooey',
            'icons': icons,
            }
        new_data = _clean_up_staging_data(data)
        expected_icons = {
            '48x48': (
                'https://myapps.developer.ubuntu.com/site_media/icons/'
                '2012/01/lonote-128.png'),
            }
        self.assertEqual(expected_icons, new_data['icons'])

    def test_modified_internal_icon(self):
        icons =  {
            '48x48': ('https://sc.staging.ubuntu.com/site_media/icons/'
                      '2011/05/fluendo-dvd.png'),
            }
        data = {
            'package_url': (
                'https://developer.staging.ubuntu.com/internal_packages/2011/'
                '05/example_1.1.0_with_valid_control.tar_.gz'),
            'myapps_id': 581,
            'arbitrary': 'fooey',
            'icons': icons,
            }
        new_data = _clean_up_staging_data(data)
        expected_icons = {
            '48x48': (
                'https://myapps.developer.ubuntu.com/site_media/icons/'
                '2011/05/fluendo-dvd.png'),
            }
        self.assertEqual(expected_icons, new_data['icons'])

    def test_unmodified(self):
        # After that point, we just want to use whatever is on staging, as
        # they'll be uploads directly to staging.
        data = {
            'package_url': (
                "http://developer.staging.ubuntu.com/site_media/arb/packages/"
                "2012/04/apache-openid_2.0.1.dev1.tar.gz"),
            'myapps_id': 595,
            'arbitrary': 'fooey',
            }
        new_data = _clean_up_staging_data(data)
        self.assertEqual(data, new_data)


class TestExternalRewrite(TestCase):

    def test_modified_internal(self):
        # When running externally from the data centre, we want to use
        # external URLs.
        data = {
            'package_url': (
                'https://myapps.developer.ubuntu.com/internal_packages/2011/'
                '05/example_1.1.0_with_valid_control.tar_.gz'),
            'arbitrary': 'fooey',
            }
        new_data = _convert_internal_data(data)
        data['package_url'] = (
            "https://myapps.developer.ubuntu.com/site_media/packages/"
            "2011/05/example_1.1.0_with_valid_control.tar_.gz")
        self.assertEqual(data, new_data)

    def test_unmodified_icon(self):
        # Icons have public URLs always.
        icons =  {
            '48x48': ('https://software-center.ubuntu.com/site_media/icons/'
                      '2011/05/fluendo-dvd.png'),
            }
        data = {
            'package_url': (
                'https://myapps.developer.ubuntu.com/internal_packages/2011/'
                '05/example_1.1.0_with_valid_control.tar_.gz'),
            'arbitrary': 'fooey',
            'icons': icons,
            }
        new_data = _clean_up_staging_data(data)
        expected_icons = {
            '48x48': (
                'https://software-center.ubuntu.com/site_media/icons/'
                '2011/05/fluendo-dvd.png'),
            }
        self.assertEqual(expected_icons, new_data['icons'])
