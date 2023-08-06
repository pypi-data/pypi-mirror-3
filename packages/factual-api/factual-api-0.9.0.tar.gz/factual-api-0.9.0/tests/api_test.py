import unittest

from factual import Factual
from factual.utils import circle
from test_settings import KEY, SECRET

class FactualAPITestSuite(unittest.TestCase):
    def setUp(self):
        self.factual = Factual(KEY, SECRET)
        self.places = self.factual.table('places')

    def test_search(self):
        q = self.places.search('factual')
        row = q.data()[0]
        self.assertRegexpMatches(row['name'], 'Factual')

    # full text search for "Mcdonald's, Santa Monica" (test spaces, commas, and apostrophes)
    def test_search2(self):
        q = self.places.search("McDonald's,Santa Monica").limit(20)
        included_rows = q.included_rows()
        self.assertEqual(20, included_rows)

    def test_limit(self):
        q = self.places.search('sushi').limit(3)
        self.assertEqual(3, len(q.data()))

    def test_select(self):
        q = self.places.select('name,address')
        row = q.data()[0]
        self.assertEqual(2, len(row.keys()))

    def test_sort(self):
        q1 = self.places.sort_asc('name')
        self.assertTrue(q1.data()[0]['name'] < q1.data()[1]['name'])

        q2 = self.places.sort_desc('name')
        self.assertTrue(q2.data()[0]['name'] > q2.data()[1]['name'])

    def test_paging(self):
        q1 = self.places.offset(30)
        r1 = q1.data()[0]

        q2 = self.places.page(3, 15)
        r2 = q2.data()[0]
        self.assertEqual(r1['name'], r2['name'])

    def test_filters(self):
        q = self.places.filters({'region': 'NV'})
        for r in q.data():
            self.assertEqual('NV', r['region'])

    def test_geo(self):
        q = self.places.search('factual').geo(circle(34.06021, -118.41828, 1000))
        row = q.data()[0]
        self.assertEqual('Factual', row['name'])
        self.assertEqual('1801 Avenue Of The Stars', row['address'])

    def test_resolve(self):
        q = self.factual.resolve({'name': 'factual inc', 'locality': 'los angeles'})
        row = q.data()[0]
        self.assertTrue(row['resolved'])
        self.assertEqual('1801 Avenue Of The Stars', row['address'])

    def test_schema(self):
        schema = self.places.schema()
        self.assertEqual(21, len(schema['fields']))
        self.assertTrue('title' in schema)
        self.assertTrue('locality' in set(f['name'] for f in schema['fields']))

    # full text search for things where locality equals 大阪市 (Osaka: test unicode)
    def test_unicode(self):
        q = self.places.filters({'locality': '大阪市'})
        for r in q.data():
            self.assertEqual('大阪市', r['locality'])

    def test_bw_encoding(self):
        q = self.places.filters({'category': {"$bw":"Arts, Entertainment & Nightlife > Bars"}})
        row = q.data()[0]
        self.assertRegexpMatches(row['category'], "Arts, Entertainment & Nightlife > Bars")

    def test_in(self):
        q = self.places.filters({"locality":{"$in":["Santa Monica","Los Angeles","Culver City"]}})
        row = q.data()[0]
        self.assertIn(row['locality'], ["Santa Monica","Los Angeles","Culver City"])

    def test_and(self):
        q = self.places.filters({"$and":[{"country":"US"},{"website":{"$blank":"false"}}]})
        row = q.data()[0]
        self.assertEqual('US', row['country'])
        self.assertRegexpMatches(row['website'], 'http')


if __name__ == '__main__':
    unittest.main()
