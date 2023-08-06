# -*- coding: utf-8 -*-

import os
import unittest
from omgeo import Geocoder
from omgeo.places import Viewbox, PlaceQuery, Candidate
from omgeo.processors.preprocessors import CountryPreProcessor, RequireCountry, ParseSingleLine, ReplaceRangeWithNumber
from omgeo.processors.postprocessors import AttrFilter, AttrExclude, AttrRename, AttrSorter, AttrReverseSorter, UseHighScoreIfAtLeast, GroupBy, ScoreSorter

# Required to run the tests for BING
BING_MAPS_API_KEY = os.getenv("BING_MAPS_API_KEY")
ESRI_MAPS_API_KEY = os.getenv("ESRI_MAPS_API_KEY")

class OmgeoTestCase(unittest.TestCase):
    def assertEqual_(self, output, expected):
        """assertEqual with built-in error message"""
        self.assertEqual(output, expected, 'Expected "%s". Got "%s".' % (expected, output))

    def assertEqualCI_(self, output, expected, strip_commas=False):
        """Case-insensitive assertEqual with built-in error message"""
        self.assertEqual_(str(output).upper(), str(expected).upper())

class GeocoderTest(OmgeoTestCase):
    g = None # not set until set up
    def setUp(self):
        # Viewbox objects
        vb = {}
        vb['callowhill'] = Viewbox(-75.162628, 39.962769, -75.150963, 39.956322)
        # PlaceQuery objects
        self.pq = {}
        # North American Addresses:
        self.pq['azavea'] = PlaceQuery('340 N 12th St Ste 402 Philadelphia PA')
        self.pq['ambiguous_azavea'] = PlaceQuery('340 12th St Ste 402 Philadelphia PA')
        self.pq['wolf'] = PlaceQuery('Wolf Building')
        self.pq['wolf_philly'] = PlaceQuery('Wolf Building, Philadelphia PA')
        self.pq['wolf_bounded'] = PlaceQuery('Wolf Building', viewbox=vb['callowhill'])
        self.pq['alpha_774R_W_Central_Ave'] = PlaceQuery('774R W Central Ave Alpha NJ')
        self.pq['alpha_774_W_Central_Ave_Rear'] = PlaceQuery('774 W Central Ave Rear Alpha NJ')
        self.pq['pine_needles_dr'] = PlaceQuery('11761 pine needles providence forge')
        self.pq['pine_needles_ct'] = PlaceQuery('5328 pine needles providence forge')
        self.pq['pine_needles_terr'] = PlaceQuery('5359 pine needles providence forge')
        self.pq['moorestown_hyphenated'] = PlaceQuery('111-113 W Main St Moorestown NJ')
        self.pq['willow_street'] = PlaceQuery('2819F Willow Street Pike Willow Street PA')
        self.pq['quebec'] = PlaceQuery('756 Rue Berri Montreal QC', country='CA')
        self.pq['quebec_bang'] = PlaceQuery('177 Rue Commerciale, Saint-Louis-du-Ha! Ha! QC')
        self.pq['quebec_accent'] = PlaceQuery('527 Ch. Beauséjour, Saint-Elzéar-de-Témiscouata QC')
        self.pq['quebec_hyphenated'] = PlaceQuery('227-227A Rue Commerciale, Saint-Louis-du-Ha! Ha! QC')
        # European Addresses:
        self.pq['london_pieces'] = PlaceQuery(address='31 Maiden Lane', city='London', country='UK')
        self.pq['london_one_line'] = PlaceQuery('31 Maiden Lane, London WC2E', country='UK')
        self.pq['london_pieces_hyphenated'] = PlaceQuery(address='31-32 Maiden Lane', city='London', country='UK')
        self.pq['london_one_line_hyphenated'] = PlaceQuery('31-32 Maiden Lane London WC2E', country='UK')
        # Oceanic Addresses:
        self.pq['karori'] = PlaceQuery('102 Karori Road Karori Wellington', country='NZ')

        # Geocoder objects
        self.g = Geocoder()
        if ESRI_MAPS_API_KEY is not None:
            self.g_esri_na = Geocoder([['omgeo.services.EsriNA',
                    {'settings':{'api_key':ESRI_MAPS_API_KEY}}]])
            self.g_esri_eu = Geocoder([['omgeo.services.EsriEU',
                    {'settings':{'api_key':ESRI_MAPS_API_KEY}}]])
        else:
            self.g_esri_na = Geocoder([['omgeo.services.EsriNA', {}]])
            self.g_esri_eu = Geocoder([['omgeo.services.EsriEU', {}]])

        self.g_bing = Geocoder([['omgeo.services.Bing', {'settings':{'api_key':BING_MAPS_API_KEY}}]])
        self.g_nom = Geocoder([['omgeo.services.Nominatim',{}]])
        self.g_dc = Geocoder([['omgeo.services.CitizenAtlas', {}]])

    def tearDown(self):
        pass

    def test_geocode_azavea(self):
        candidates = self.g.geocode(self.pq['azavea'])
        self.assertEqual(len(candidates) > 0, True, 'No candidates returned.')
        self.assertEqual(len(candidates) > 1, False, 'More than one candidate returned.')

    def test_geocode_esri_na_us(self):
        candidates = self.g_esri_na.geocode(self.pq['alpha_774_W_Central_Ave_Rear'])
        self.assertEqual(len(candidates) > 0, True, 'No candidates returned.')

    def test_geocode_esri_na_nz(self):
        candidates = self.g_esri_na.geocode(self.pq['karori'])
        self.assertEqual(len(candidates) > 0, False, 'Found New Zealand address when this should only be using the North American ESRI geocoder.')

    def test_nom_bounded(self):
        candidates = self.g.geocode(PlaceQuery('8 Kirkbride Rd'))
        self.assertEqual(len(candidates) > 0, True, 'No candidates returned.')

    @unittest.skipIf(BING_MAPS_API_KEY is None, 'Enter a Bing Maps API key to run the bing tests')
    def test_geocode_bing(self):
        candidates = self.g_bing.geocode(self.pq['azavea'])
        self.assertEqual(len(candidates) > 0, True, 'No candidates returned.')

    def test_geocode_dc_address(self):
        candidates = self.g_dc.geocode(PlaceQuery('1600 pennsylvania'))
        self.assertTrue(len(candidates) > 0, 'No candidates returned.')
        self.assertTrue(candidates[0].locator == 'DC Address', 'Expected 1600 pennsylvania to be an address match')

    def test_geocode_dc_intersection(self):
        candidates = self.g_dc.geocode(PlaceQuery('h and 15th'))
        self.assertTrue(len(candidates) > 0, 'No candidates returned.')
        self.assertTrue(candidates[0].locator == 'DC Intersection', 'h and 15th to be an intersection match')

    def test_geocode_dupepicker(self):
        candidates = self.g.geocode(self.pq['ambiguous_azavea'])
        self.assertEqual(len(candidates) > 0, True, 'No candidates returned.')

    def _test_geocode_results_all(self, verbosity=0, geocoder=Geocoder()):
        queries_with_results = 0
        for place in self.pq:
            if verbosity > 1: print '\n%s' % place
            if verbosity > 1: print len(place) * '-'
            candidates = geocoder.geocode(self.pq[place])
            if len(candidates) == 0:
                if verbosity > 1: print 'Input:  %s\n(no results)' % self.pq[place].query
            else:
                queries_with_results += 1
                if verbosity > 1: print 'Input:  %s' % self.pq[place].query
                for x in ['Output: %r (%s %s)' % (c.match_addr, c.geoservice, [c.locator, c.score, c.confidence, c.entity]) for c in candidates]:
                    if verbosity > 1: print x
        self.assertEqual(len(self.pq), queries_with_results, 'Got results for %d of %d queries.' % (queries_with_results, len(self.pq)))

    def test_geocode_results_all(self):
        if BING_MAPS_API_KEY is not None:
            self.g.add_source(['omgeo.services.Bing',
                     {'settings':{'api_key':BING_MAPS_API_KEY}}])
        self._test_geocode_results_all(geocoder=self.g)

class GeocoderProcessorTest(OmgeoTestCase):
    def setUp(self):
        # places
        self.pq_us = PlaceQuery('1200 Callowhill St, Philadelphia, PA 19107')
        self.pq_uk = PlaceQuery('32 Bond Road, Ste A, Surbiton, Surrey KT6')
        self.pq_uk_with_country_UK = PlaceQuery('32 Bond Road, Ste A, Surbiton, Surrey KT6', country='UK')
        self.pq_uk_with_country_GB = PlaceQuery('32 Bond Road, Ste A, Surbiton, Surrey KT6', country='GB')

        # candidates
        self.good = Candidate(match_addr='123 Any St', locator='address', score=85.3)
        self.better = Candidate(match_addr='123 Any St', locator='parcel', score=92)
        self.best = Candidate(match_addr='123 Any St', locator='rooftop', score=100)
        self.wolf_good = Candidate(match_addr='1200 Callowhill St', locator='address', score=76)
        self.wolf_better = Candidate(match_addr='1200 Callowhill St', locator='parcel', score=90)
        self.wolf_best = Candidate(match_addr='1200 Callowhill St', locator='rooftop', score=99.9)

        self.locators_worse_to_better = ['address', 'parcel', 'rooftop']

    def tearDown(self):
        pass


    def test_pro_country_CountryPreProcessor(self):
        acceptable_countries = ['US', 'UK']
        country_map = {'GB':'UK'} # 'from':'to'
        place_in = self.pq_uk_with_country_GB
        place_out = CountryPreProcessor(acceptable_countries, country_map).process(place_in)
        country_exp = 'UK'
        self.assertEqual_(place_out.country, country_exp)

    def test_pro_country_RequireCountry(self):
        place_in = self.pq_us
        place_out = RequireCountry().process(place_in)
        place_exp = False
        self.assertEqual_(place_out, place_exp)

    def test_pro_filter_AttrFilter_exact(self):
        good_values = ['roof', 'parcel']
        candidates_in = [self.best, self.good, self.better]
        candidates_exp = [self.better] # just the one with the parcel locator
        candidates_out = AttrFilter(good_values, 'locator', exact_match=True).process(candidates_in)
        self.assertEqual_(candidates_out, candidates_exp)

    def test_pro_filter_AttrFilter_inexact(self):
        good_values = ['roof', 'parcel']
        candidates_in = [self.best, self.good, self.better]
        candidates_exp = [self.best, self.better] # roof is a substr of rooftop
        candidates_out = AttrFilter(good_values, 'locator', exact_match=False).process(candidates_in)
        self.assertEqual_(candidates_out, candidates_exp)

    def test_pro_filter_AttrExclude_exact(self):
        bad_values = ['address', 'parc']
        candidates_in = [self.best, self.good, self.better]
        candidates_exp = [self.best, self.better]
        # The candidate with the 'parcel' locator stays because 'parcel' is not in bad values
        # and the processor by default only looks for exact matches against bad_values.
        candidates_out = AttrExclude(bad_values, 'locator', exact_match=True).process(candidates_in)
        self.assertEqual_(candidates_out, candidates_exp)

    def test_pro_filter_AttrExclude_inexact(self):
        bad_values = ['address', 'parc']
        candidates_in = [self.best, self.good, self.better]
        candidates_exp = [self.best]
        # This can be confusing. There is only one because the match does NOT have to be exact, but
        # we are using this processor to EXCLUDE values, so an inexact match will result in fewer candidates
        candidates_out = AttrExclude(bad_values, 'locator', exact_match=False).process(candidates_in)
        self.assertEqual_(candidates_out, candidates_exp)

    def test_pro_group_GroupBy(self):
        candidates_in = [self.best, self.good, self.better, self.wolf_best, self.wolf_good]
        candidates_exp = [self.best, self.wolf_best]
        candidates_out = GroupBy('match_addr').process(candidates_in)
        self.assertEqual_(candidates_out, candidates_exp)

    def test_pro_parsing_ParseSingleLine(self):
        place_in = PlaceQuery('32 Bond Road, Surbiton, Surrey KT6 7SH')
        place_out = ParseSingleLine().process(place_in)
        self.assertEqual_(place_out.address, '32 Bond Road')
        self.assertEqual_(place_out.city, 'Surbiton, Surrey')
        self.assertEqual_(place_out.postal, 'KT6 7SH')

    def test_pro_rename_AttrRename_inexact(self):
        candidates_in = [self.best]
        locator_exp = 'el_techo'
        candidates_out = AttrRename('locator', {'oofto': 'el_techo'}).process(candidates_in)
        self.assertEqual_(candidates_out[0].locator, locator_exp)

    def test_pro_rename_AttrRename_exact(self):
        candidates_in = [self.best]
        locator_exp = 'el_techo'
        candidates_out = AttrRename('locator', {'rooftop': 'el_techo'}).process(candidates_in)
        self.assertEqual_(candidates_out[0].locator, locator_exp)

    def test_pro_scoring_UseHighScoreIfAtLeast(self):
        candidates_in = [self.best, self.good, self.better]
        candidates_exp = [self.best, self.better]
        candidates_out = UseHighScoreIfAtLeast(90).process(candidates_in)
        self.assertEqual_(candidates_out, candidates_exp)

    def test_pro_scoring_ScoreSorter(self):
        candidates_in = [self.best, self.good, self.better]
        candidates_exp = [self.best, self.better, self.good]
        candidates_out = ScoreSorter().process(candidates_in)
        self.assertEqual_(candidates_out, candidates_exp)

    def test_pro_scoring_ScoreSorter_asc(self):
        candidates_in = [self.best, self.good, self.better]
        candidates_exp = [self.good, self.better, self.best]
        candidates_out = ScoreSorter(reverse=False).process(candidates_in)
        self.assertEqual_(candidates_out, candidates_exp)

    def test_pro_sort_AttrSorter(self):
        candidates_in = [self.better, self.best, self.good]
        candidates_exp = [self.good, self.better, self.best]
        candidates_out = AttrSorter(self.locators_worse_to_better).process(candidates_in)
        self.assertEqual_(candidates_out, candidates_exp)

    def test_pro_sort_AttrReverseSorter(self):
        candidates_in = [self.better, self.best, self.good]
        candidates_exp = [self.best, self.better, self.good] # reverse order of self.locators_worse_to_better
        candidates_out = AttrReverseSorter(self.locators_worse_to_better).process(candidates_in)
        self.assertEqual_(candidates_out, candidates_exp)

    def test_pro_streetnumber_ReplaceRangeWithNumber(self):
        place_in = PlaceQuery('4452-54 Main Street, Philadelphia') #Mom's Pizza in Manayunk
        place_out = ReplaceRangeWithNumber().process(place_in)
        query_exp = '4452 Main Street, Philadelphia'
        self.assertEqual_(place_out.query, query_exp)


if __name__ == '__main__':
    unittest.main()
