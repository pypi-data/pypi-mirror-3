from tg import expose
from model import Article, Tagging
from tgext.pluggable import plug_url
from tgext.tagging import TagCloud
from smallpress.lib.forms import SearchForm

search_form = SearchForm()

@expose('genshi:smallpress.templates.articles')
def articles(articles=None, blog=None):
    if articles is None:
        articles=Article.get_published(blog)
    return dict(articles=articles)

@expose('genshi:smallpress.templates.article_preview')
def article_preview(article):
    return dict(article=article, tg_cache=dict(key='%s-%s' % (article.uid,
                                                              article.update_date.strftime('%Y-%m-%d_%H:%M:%S')),
                                               expire=None,
                                               type='memory'))

@expose('genshi:smallpress.templates.tagcloud')
def tagcloud(tags=None):
    tagcloud=TagCloud(tagging_url=plug_url('smallpress', '/tagging'))
    if tags is None:
        tags = Tagging.tag_cloud_for_set(Article).all()
    return dict(tagcloud=tagcloud, tags=tags)

@expose('genshi:smallpress.templates.search')
def search():
    return dict(form=search_form, action=plug_url('smallpress', '/search'),
                tg_cache=dict(key='search', expire=None, type='memory'))
