# -*- coding: utf-8 -*-

from talgoxe.models import ArticleSearchCriteria

userSettings = {}


class UserSettings:

    @staticmethod
    def get_articles_html(request):
        settings = UserSettings.get_settings(request)
        if 'articlesHtml' in settings:
            articles = settings['articlesHtml']
        else:
            articles = []
        return articles

    @staticmethod
    def get_clipboard(request):
        settings = UserSettings.get_settings(request)
        if 'clipboard' in settings:
            clipboard = settings['clipboard']
        else:
            clipboard = ''
        return clipboard

    @staticmethod
    def get_edit_article(request):
        settings = UserSettings.get_settings(request)
        if 'editArticle' in settings:
            edit_article = settings['editArticle']
        else:
            edit_article = None
        return edit_article

    @staticmethod
    def get_search_articles(request):
        settings = UserSettings.get_settings(request)
        if 'searchArticles' in settings:
            articles = settings['searchArticles']
        else:
            articles = []
        return articles

    @staticmethod
    def get_search_criteria(request):
        settings = UserSettings.get_settings(request)
        if 'searchCriteria' in settings:
            search_criteria = settings['searchCriteria']
        else:
            search_criteria = [ArticleSearchCriteria(),
                               ArticleSearchCriteria(),
                               ArticleSearchCriteria()]
        return search_criteria

    @staticmethod
    def get_settings(request):
        user_name = request.user.username
        if user_name in userSettings:
            settings = userSettings[user_name]
        else:
            settings = {}
            userSettings[user_name] = settings
        return settings

    @staticmethod
    def has_articles_html(request):
        articles_html = UserSettings.get_articles_html(request)
        return (len(articles_html) > 0) and not (articles_html[0] is None)

    @staticmethod
    def has_edit_article(request):
        article = UserSettings.get_edit_article(request)
        return not (article is None)

    @staticmethod
    def update_clipboard(request, clipboard):
        settings = UserSettings.get_settings(request)
        settings['clipboard'] = clipboard

    @staticmethod
    def update_article_html(request, article):
        articles = []
        articles.append(article)
        UserSettings.update_articles_html(request, articles)

    @staticmethod
    def update_articles_html(request, articles):
        settings = UserSettings.get_settings(request)
        settings['articlesHtml'] = articles

    @staticmethod
    def update_edit_article(request, article):
        settings = UserSettings.get_settings(request)
        settings['editArticle'] = article

    @staticmethod
    def update_search_articles(request, articles):
        settings = UserSettings.get_settings(request)
        settings['searchArticles'] = articles
        for article in articles:
            article.checked = False

    @staticmethod
    def update_search_criteria(request, search_criteria):
        settings = UserSettings.get_settings(request)
        settings['searchCriteria'] = search_criteria
