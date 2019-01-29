from django.test import TestCase
from talgoxe.models import Province

class LandskapTestCase(TestCase):
    def setUp(self):
        self.landskap0 = Province('Norrb')
        self.landskap1 = Province('Östg')

    def test_landskapens_ordning(self):
        sorterade_landskap = sorted([self.landskap0, self.landskap1], key = Province.key)
        self.assertEqual(sorterade_landskap[0], self.landskap1)
        self.assertEqual(sorterade_landskap[1], self.landskap0)

    def test_reduce_landskap(self):
        input = [Province('Skåne'), Province('Blek'), Province('Öland'), Province('Smål'),
                 Province('Hall'), Province('Västg'), Province('Boh'), Province('Dalsl')]
        self.assertEqual(Province.reduce_landskap(input)[0].abbrev, 'Götal')

    def test_that_reduce_landskap_also_sorts(self):
        bokstavsordningssorterade = [Province('Blek'), Province('Dalsl'), Province('Skåne'), Province('Smål'), Province('Västg')]
        self.assertEqual(list(map(lambda ls: ls.abbrev, Province.reduce_landskap(bokstavsordningssorterade))), ['Skåne', 'Blek', 'Smål', 'Västg', 'Dalsl'])
