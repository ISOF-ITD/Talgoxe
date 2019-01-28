class Province():
    province_order = [
        u'Skåne', u'Blek', u'Öland', u'Smål', u'Hall', u'Västg', u'Boh', u'Dalsl', u'Gotl', u'Östg', # 0-9
        u'Götal', # 10
        u'Sörml', u'Närke', u'Värml', u'Uppl', u'Västm', u'Dal', # 11 - 16
        u'Sveal', # 17
        u'Gästr', u'Häls', u'Härj', u'Med', u'Jämtl', u'Ång', u'Västb', u'Lappl', u'Norrb', # 18 - 26
        u'Norrl', # 27
    ]

    province_abbreviation = {
      u'Sk' : u'Skåne',
      u'Bl' : u'Blek',
      u'Öl' : u'Öland',
      u'Sm' : u'Smål',
      u'Ha' : u'Hall',
      u'Vg' : u'Västg',
      u'Bo' : u'Boh',
      u'Dsl': u'Dalsl',
      u'Gl' : u'Gotl',
      u'Ög' : u'Östg',
      u'Götal' : u'Götal',
      u'Sdm': u'Sörml',
      u'Nk' : u'Närke',
      u'Vrm': u'Värml',
      u'Ul' : u'Uppl',
      u'Vstm' : u'Västm',
      u'Dal': u'Dal',
      u'Sveal' : u'Sveal',
      u'Gst': u'Gästr',
      u'Hsl': u'Häls',
      u'Hrj': u'Härj',
      u'Mp' : u'Med',
      u'Jl' : u'Jämtl',
      u'Åm' : u'Ång',
      u'Vb' : u'Västb',
      u'Lpl': u'Lappl',
      u'Nb' : u'Norrb',
      u'Norrl' : u'Norrl',
    }

    def cmp(self, other):
        if self.abbreviation in self.province_order and other.abbreviation in self.province_order:
            return self.cmp(self.province_order.index(self.abbreviation), self.province_order.index(other.abbreviation))
        else:
            return 0

    @staticmethod
    def key(self):
        if self.abbreviation in self.province_order:
            return self.province_order.index(self.abbreviation)
        else:
            return -1 # Så det är lättare att se dem

    def __init__(self, abbreviation):
        self.abbreviation = abbreviation.capitalize()

    def __str__(self):
        return self.abbreviation

    @staticmethod
    def reduce_provinces(provinces):
        province_count_in_country_part = { 'Götal' : 7, 'Sveal' : 4, 'Norrl' : 6 }
        provinces_in_country_part = { 'Götal' : [], 'Sveal' : [], 'Norrl' : [] }
        for province in provinces:
            if Province.province_order.index(province.abbreviation) < Province.province_order.index('Götal'):
                provinces_in_country_part['Götal'].append(province)
            elif Province.province_order.index(province.abbreviation) < Province.province_order.index('Sveal'):
                provinces_in_country_part['Sveal'].append(province)
            else:
                provinces_in_country_part['Norrl'].append(province)

        provinces_as_string = []
        for country_part, provinces_in_one_country_part in provinces_in_country_part.items():
            if len(provinces_in_one_country_part) >= province_count_in_country_part[country_part]:
                provinces_as_string.append(Province(country_part))
            else:
                provinces_as_string += sorted(provinces_in_one_country_part, key = Province.key)

        return provinces_as_string
