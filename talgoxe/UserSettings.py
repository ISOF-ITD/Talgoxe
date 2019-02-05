# -*- coding: utf-8 -*-

from talgoxe.ArticleManager import ArticleManager, ArticleSearchCriteria

userSettings = {}


class UserSettings:

    @staticmethod
    def delete_article(article_id):
        for settings in userSettings.values():
            if 'articlesHtml' in settings:
                articles = settings['articlesHtml']
                if (len(articles) > 0) and not (articles[0] is None):
                    index = len(articles)
                    while (index > 0):
                        index -= 1
                        if (articles[index].id == article_id):
                            settings['articlesHtml'].pop(index)

            if 'editArticle' in settings:
                article = settings['editArticle']
                if (article.id == article_id):
                    settings['editArticle'] = None

            if 'searchArticles' in settings:
                articles = settings['searchArticles']
                if (len(articles) > 0) and not (articles[0] is None):
                    index = len(articles)
                    while (index > 0):
                        index -= 1
                        if (articles[index].id == article_id):
                            settings['searchArticles'].pop(index)

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
    def update_articles_cache(request):
        # Refresh cached information.
        if (UserSettings.has_edit_article(request)):
            edit_article = UserSettings.get_edit_article(request)
            edit_article = ArticleManager.get_article(edit_article.id)
            UserSettings.update_edit_article(request, edit_article)

        if (UserSettings.has_articles_html(request)):
            article_ids = []
            for article in UserSettings.get_articles_html(request):
                article_ids.append(article.id)
            articles_html = ArticleManager.get_articles_by_ids(article_ids)
            UserSettings.update_articles_html(request, articles_html)

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
        if (search_criteria is None):
            search_criteria = [ArticleSearchCriteria(),
                               ArticleSearchCriteria(),
                               ArticleSearchCriteria()]

        settings = UserSettings.get_settings(request)
        settings['searchCriteria'] = search_criteria
