from django.test import TestCase
from talgoxe.models import Landskap

class LandskapTestCase(TestCase):
    def setUp(self):
        self.landskap0 = Landskap('Norrb')
        self.landskap1 = Landskap('Östg')

    def test_landskapens_ordning(self):
        sorterade_landskap = sorted([self.landskap0, self.landskap1], key = Landskap.key)
        self.assertEqual(sorterade_landskap[0], self.landskap1)
        self.assertEqual(sorterade_landskap[1], self.landskap0)

    def test_reduce_landskap(self):
        input = [Landskap('Skåne'), Landskap('Blek'), Landskap('Öland'), Landskap('Smål'),
          Landskap('Hall'), Landskap('Västg'), Landskap('Boh'), Landskap('Dalsl')]
        self.assertEqual(Landskap.reduce_landskap(input)[0].abbrev, 'Götal')

    def test_that_reduce_landskap_also_sorts(self):
        bokstavsordningssorterade = [Landskap('Blek'), Landskap('Dalsl'), Landskap('Skåne'), Landskap('Smål'), Landskap('Västg')]
        self.assertEqual(list(map(lambda ls: ls.abbrev, Landskap.reduce_landskap(bokstavsordningssorterade))), ['Skåne', 'Blek', 'Smål', 'Västg', 'Dalsl'])
