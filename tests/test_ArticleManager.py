from django.test import TestCase
from talgoxe.models import ArticleManager
from talgoxe.models import ArticleSearchCriteria

class ArticleManagerTest(TestCase):
    #def setUp(self):
        # settings.configure()

    def get_articles_by_search_criteria(self):
        search_criteria = ArticleSearchCriteria()
        search_criteria.compare_type = "StartsWith"
        search_criteria.search_type = "Lemma"
        search_criteria.search_string = "g"
        articles = ArticleManager.get_articles_by_search_criteria(search_criteria)
        self.assertIsNotNone(articles)

