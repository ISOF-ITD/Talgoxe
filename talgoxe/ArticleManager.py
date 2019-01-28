from talgoxe.common_functions import *
from talgoxe.models import Artikel, Spole, Typ


class ArticleSearchCriteria:
    def __init__(self):
        self.compare_type = "StartsWith"
        self.search_string = ""
        self.search_type = "Lemma"


class ArticleManager:

    @staticmethod
    def create_article(article_information):
        article = Artikel.create(article_information)
        article.collect()
        return article

    @staticmethod
    def delete_article(article_id):
        Spole.objects.filter(artikel_id = article_id).delete()
        Artikel.objects.get(id = article_id).delete()

    @staticmethod
    def get_article(article_id, load_article_items=True):
        article = Artikel.objects.get(id = article_id)
        if (load_article_items):
            article.collect()
        return article

    @staticmethod
    def get_article_item_types(search_criteria_list):
        articleItemTypeIds = []
        has_article_item_search_criteria = False
        has_article_item_type_search_criteria = False
        for search_criteria in search_criteria_list:
            if ((search_criteria.search_type == 'ArticleItemType') and
                (not (is_empty_string(search_criteria.search_string)))):
                has_article_item_type_search_criteria = True
            if (search_criteria.search_type == 'ArticleItem'):
                has_article_item_search_criteria = True

        if (has_article_item_search_criteria and
            has_article_item_type_search_criteria):
            for search_criteria in search_criteria_list:
                if ((search_criteria.search_type == 'ArticleItemType') and
                    (not (is_empty_string(search_criteria.search_string)))):
                    if (search_criteria.compare_type == 'Contains'):
                        articleItemTypes = Typ.objects.filter(kod__icontains=search_criteria.search_string)
                    elif (search_criteria.compare_type == 'EndWith'):
                        articleItemTypes = Typ.objects.filter(kod__iendswith=search_criteria.search_string)
                    elif (search_criteria.compare_type == 'EqualTo'):
                        articleItemTypes = Typ.objects.filter(kod__iexact=search_criteria.search_string)
                    elif (search_criteria.compare_type == 'StartsWith'):
                        articleItemTypes = Typ.objects.filter(kod__istartswith=search_criteria.search_string)
                    for articleItemType in articleItemTypes:
                        articleItemTypeIds.append(articleItemType.id)
        else:
            articleItemTypeIds = None
        return articleItemTypeIds

    @staticmethod
    def get_articles(load_article_items = True):
        articles = []
        articles_database = Artikel.objects.all()
        articles += articles_database

        if (load_article_items and (len(articles) >= 1)):
            # Get article items and add that information to article.
            article_ids = []
            for article in articles:
                article_ids.append(article.id)
            article_item_array = []
            article_items = Spole.objects.filter(artikel_id__in = article_ids)
            article_item_array += article_items
            article_item_dictionary = {}
            for article_id in article_ids:
                article_item_dictionary[int(article_id)] = []
            for article_item in article_item_array:
                article_item_dictionary[article_item.artikel_id].append(article_item)
            for article in articles:
                article.collect2(article_item_dictionary[article.id])

        return articles

    @staticmethod
    def get_articles_by_ids(article_ids, load_article_items = True):
        articles = []
        articles_database = Artikel.objects.filter(id__in=article_ids)
        articles += articles_database

        if (load_article_items and (len(articles) >= 1)):
            # Get article items and add that information to article.
            article_item_array = []
            article_items = Spole.objects.filter(artikel_id__in = article_ids)
            article_item_array += article_items
            article_item_dictionary = {}
            for article_id in article_ids:
                article_item_dictionary[int(article_id)] = []
            for article_item in article_item_array:
                article_item_dictionary[article_item.artikel_id].append(article_item)
            for article in articles:
                article.collect2(article_item_dictionary[article.id])

        return articles

    @staticmethod
    def get_articles_by_letter(letter, load_article_items = True):
        articles = []
        articles_database = Artikel.objects.filter(lemma_sortable__istartswith = letter)
        articles += articles_database

        if (load_article_items and (len(articles) >= 1)):
            # Get article items and add that information to article.
            article_ids = []
            for article in articles:
                article_ids.append(article.id)
            article_item_array = []
            article_items = Spole.objects.filter(artikel_id__in = article_ids)
            article_item_array += article_items
            article_item_dictionary = {}
            for article_id in article_ids:
                article_item_dictionary[int(article_id)] = []
            for article_item in article_item_array:
                article_item_dictionary[article_item.artikel_id].append(article_item)
            for article in articles:
                article.collect2(article_item_dictionary[article.id])

        return articles

    @staticmethod
    def get_articles_by_search_criteria(search_criteria_list):
        if (ArticleManager.is_empty_search_criteria(search_criteria_list)):
            return []

        article_search_result = None
        article_item_types = ArticleManager.get_article_item_types(search_criteria_list)
        for search_criteria in search_criteria_list:
            if ((not (is_empty_string(search_criteria.search_string))) and
                (not ((search_criteria.search_type == 'ArticleItemType') and
                      (not (article_item_types is None))))):
                articles = ArticleManager.get_articles_by_one_search_criteria(search_criteria, article_item_types)
                if (article_search_result is None):
                    article_search_result = articles
                else:
                    article_search_result = ArticleManager.get_subset(article_search_result, articles)

        if (article_search_result is None):
            article_search_result = []
        return article_search_result

    @staticmethod
    def get_articles_by_lemma(lemma):
        articles = []
        search_articles = Artikel.objects.filter(lemma = lemma)
        articles += search_articles
        return articles

    @staticmethod
    def get_articles_by_one_search_criteria(search_criteria, article_item_types):
        articles = []
        search_articles = None
        if (not (is_empty_string(search_criteria.search_string))):
            if ((search_criteria.search_type == 'Lemma') or
                (search_criteria.search_type == 'All')):
                if (search_criteria.compare_type == 'Contains'):
                    search_articles = Artikel.objects.filter(lemma_sortable__icontains = search_criteria.search_string)
                elif (search_criteria.compare_type == 'EndWith'):
                    search_articles = Artikel.objects.filter(lemma_sortable__iendswith=search_criteria.search_string)
                elif (search_criteria.compare_type == 'EqualTo'):
                    search_articles = Artikel.objects.filter(lemma_sortable__iexact=search_criteria.search_string)
                elif (search_criteria.compare_type == 'StartsWith'):
                    search_articles = Artikel.objects.filter(lemma_sortable__istartswith=search_criteria.search_string)
                articles += search_articles

            if ((search_criteria.search_type == 'ArticleItem') or
                (search_criteria.search_type == 'All')):
                if (search_criteria.compare_type == 'Contains'):
                    if (article_item_types is None):
                        articleItems = Spole.objects.filter(text__icontains=search_criteria.search_string).select_related('artikel')
                    else:
                        articleItems = Spole.objects.filter(text__icontains=search_criteria.search_string, typ_id__in=article_item_types).select_related('artikel')
                elif (search_criteria.compare_type == 'EndWith'):
                    if (article_item_types is None):
                        articleItems = Spole.objects.filter(text__iendswith=search_criteria.search_string).select_related('artikel')
                    else:
                        articleItems = Spole.objects.filter(text__iendswith=search_criteria.search_string, typ_id__in=article_item_types).select_related('artikel')
                elif (search_criteria.compare_type == 'EqualTo'):
                    if (article_item_types is None):
                        articleItems = Spole.objects.filter(text__iexact=search_criteria.search_string).select_related('artikel')
                    else:
                        articleItems = Spole.objects.filter(text__iexact=search_criteria.search_string, typ_id__in=article_item_types).select_related('artikel')
                elif (search_criteria.compare_type == 'StartsWith'):
                    if (article_item_types is None):
                        articleItems = Spole.objects.filter(text__istartswith=search_criteria.search_string).select_related('artikel')
                    else:
                        articleItems = Spole.objects.filter(text__istartswith=search_criteria.search_string, typ_id__in=article_item_types).select_related('artikel')

                search_articles = [articleItem.artikel for articleItem in articleItems]
                articles += search_articles

            if (((search_criteria.search_type == 'ArticleItemType') or
                 (search_criteria.search_type == 'All')) and
                (article_item_types is None)):
                if (search_criteria.compare_type == 'Contains'):
                    articleItemTypes = Typ.objects.filter(kod__icontains=search_criteria.search_string)
                elif (search_criteria.compare_type == 'EndWith'):
                    articleItemTypes = Typ.objects.filter(kod__iendswith=search_criteria.search_string)
                elif (search_criteria.compare_type == 'EqualTo'):
                    articleItemTypes = Typ.objects.filter(kod__iexact=search_criteria.search_string)
                elif (search_criteria.compare_type == 'StartsWith'):
                    articleItemTypes = Typ.objects.filter(kod__istartswith=search_criteria.search_string)
                articleItemTypeIds = []
                for articleItemType in articleItemTypes:
                    articleItemTypeIds.append(articleItemType.id)
                articleItems = Spole.objects.filter(typ_id__in=articleItemTypeIds).select_related('artikel')
                search_articles = [articleItem.artikel for articleItem in articleItems]
                articles += search_articles

        if (len(articles) > 1):
            # Get distinct articles.
            articlesDictionary = {}
            for article in articles:
                if (not (article.id in articlesDictionary)):
                    articlesDictionary[article.id] = article

            # Sorted articles from database.
            search_articles = Artikel.objects.filter(id__in=articlesDictionary.keys())
            articles = []
            articles += search_articles

        return articles

    @staticmethod
    def get_subset(articles1, articles2):
        if (len(articles1) < 1) or (articles1[0] is None):
            return []
        if (len(articles2) < 1) or (articles2[0] is None):
            return []

        article_dictionary = {}
        for article in articles2:
            article_dictionary[article.id] = article

        index = len(articles1) - 1
        while (index >= 0):
            if (not (articles1[index].id in article_dictionary)):
                articles1.remove(articles1[index])
            index -= 1

        return articles1

    @staticmethod
    def is_empty_search_criteria(search_criteria_list):
        if (search_criteria_list is None):
            return True;
        if (len(search_criteria_list) < 1):
            return True;
        is_search_string_found = False
        for search_criteria in search_criteria_list:
            if (is_not_empty_string(search_criteria.search_string)):
                is_search_string_found = True
        return not is_search_string_found

    @staticmethod
    def update_article(article_id, article_information):
        article = Artikel.objects.get(id = article_id)
        article.update(article_information)
        article.collect()
        return article

    @staticmethod
    def update_article_order(article_ids):
        ordning = []
        for article_id in article_ids:
            ordning.append(Artikel.objects.get(id = article_id))
        föreArtikel = ordning[0]
        föreRang = 1
        for artikel in ordning[1:]:
            if artikel.lemma != föreArtikel.lemma and föreRang == 1:
                föreRang = 0
            if föreArtikel.rang != föreRang:
                föreArtikel.rang = föreRang
                föreArtikel.save()
            if artikel.lemma == föreArtikel.lemma:
                föreRang += 1
            else:
                föreRang = 1
            föreArtikel = artikel


