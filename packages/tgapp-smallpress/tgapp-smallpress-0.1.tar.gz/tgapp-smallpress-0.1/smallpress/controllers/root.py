# -*- coding: utf-8 -*-
"""Main Controller"""
import os
from tg import TGController
from tg import expose, flash, require, url, lurl, request, redirect, validate, tmpl_context, config
from tg.decorators import before_render
from tg.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from smallpress.model import DBSession, Article, Attachment, Tagging
from smallpress.helpers import *
from smallpress.lib.forms import ArticleForm, UploadForm
from tgext.datahelpers.validators import SQLAEntityConverter
from tgext.datahelpers.fields import AttachedFile
from tgext.pluggable import plug_url
from webhelpers.html.builder import HTML
from tw.api import CSSLink
from tw.forms import DataGrid
from tw.forms.validators import UnicodeString
from datetime import datetime
from tgext.ajaxforms.ajaxform import formexpose, spinner_icon
from tgext.tagging import TaggingController
import whoosh
from whoosh.query import *

article_form = ArticleForm()
upload_form = UploadForm()
articles_table = DataGrid(fields=[(l_('Actions'), lambda row:link_buttons(row, 'edit', 'delete', 'hide', 'publish')),
                                  (l_('Title'), lambda row:HTML.a(row.title,
                                                                  href=plug_url('smallpress', '/view/%s'%row.uid,
                                                                                lazy=True))),
                                  (l_('Tags'), comma_separated_tags),
                                  (l_('Author'), 'author'),
                                  (l_('Publishing'), lambda row:format_published(row) + ', ' + format_date(row))])
attachments_table = DataGrid(fields=[(l_('Actions'), lambda row:link_buttons(row, 'rmattachment')),
                                     (l_('Name'), 'name'),
                                     (l_('Url'), lambda row:format_link(row.url))])

def inject_css(*args, **kw):
    CSSLink(link='/_pluggable/smallpress/css/style.css').inject()

class RootController(TGController):
    tagging = TaggingController(model=Article, session=DBSession, allow_edit=None)
    tagging.search = before_render(inject_css)(tagging.search)

    @expose('genshi:smallpress.templates.index')
    def index(self, *args, **kw):
        articles = Article.get_published().all()
        tags = Tagging.tag_cloud_for_set(Article, articles).all()
        return dict(articles=articles, tags=tags)

    @expose('genshi:smallpress.templates.article')
    @validate(dict(article=SQLAEntityConverter(Article)), error_handler=index)
    def view(self, article):
        visible = False

        if article.published and article.publish_date <= datetime.now():
            visible = True
        elif request.identity and article.author == request.identity['user']:
            visible = True
        elif request.identity and 'smallpress' in request.identity['groups']:
            visible = True

        if not visible:
            return redirect(plug_url('smallpress', '/'))

        return dict(article=article)

    @require(predicates.in_group('smallpress'))
    @expose('genshi:smallpress.templates.manage')
    def manage(self, *args, **kw):
        articles = DBSession.query(Article).order_by(Article.publish_date.desc())
        return dict(table=articles_table, articles=articles,
                    create_action=self.mount_point+'/new')

    @require(predicates.in_group('smallpress'))
    @expose('genshi:smallpress.templates.edit')
    def new(self, **kw):
        attachments_table.register_resources()

        if 'uid' not in kw:
            article = Article(author=request.identity['user'])
            DBSession.add(article)
            DBSession.flush()

            kw['title'] = article.title
            kw['publish_date'] = format_date(article)
        else:
            article = DBSession.query(Article).get(kw['uid'])

        value = {
            'uid':article.uid,
            'title':kw['title'],
            'publish_date':kw['publish_date'],
            'tags':kw.get('tags', ''),
            'description':kw.get('description', ''),
            'content':kw.get('content', '')
        }

        return dict(article=article, value=value,
                    form=article_form, action=url(self.mount_point+'/save'),
                    upload_form=upload_form, upload_action=url(self.mount_point+'/attach'))

    @require(predicates.in_group('smallpress'))
    @expose('genshi:smallpress.templates.edit')
    def edit(self, uid, *args, **kw):
        attachments_table.register_resources()

        article = DBSession.query(Article).get(uid)
        value = {
            'uid':article.uid,
            'title':article.title,
            'description':article.description,
            'tags':comma_separated_tags(article),
            'publish_date':format_date(article),
            'content':article.content
        }

        return dict(article=article, value=value,
                    form=article_form, action=url(self.mount_point+'/save'),
                    upload_form=upload_form, upload_action=url(self.mount_point+'/attach'))

    @require(predicates.in_group('smallpress'))
    @validate(article_form, error_handler=edit)
    @expose()
    def save(self, *args, **kw):
        article = DBSession.query(Article).get(kw['uid'])
        article.title = kw['title']
        article.description = kw['description']
        article.content = kw['content']
        article.publish_date = datetime.strptime(kw['publish_date'], '%Y-%m-%d %H:%M')
        Tagging.set_tags(article, kw['tags'])

        flash(_('Articles successfully saved'))
        return redirect(self.mount_point+'/manage')

    @require(predicates.in_group('smallpress'))
    @formexpose(upload_form, 'smallpress.templates.attachments')
    def upload_form_show(self, **kw):
        article = DBSession.query(Article).get(kw['article'])
        return dict(value=kw, table=attachments_table, attachments=article.attachments)

    @require(predicates.in_group('smallpress'))
    @validate(upload_form, error_handler=upload_form_show)
    @expose('genshi:smallpress.templates.attachments')
    def attach(self, **kw):
        article = DBSession.query(Article).get(kw['article'])
        attachment = Attachment(name=kw['name'], article=article,
                                content=AttachedFile(kw['file'].file, kw['file'].filename))
        DBSession.add(attachment)
        DBSession.flush()

        return dict(value=dict(article=article.uid),
                    ajaxform=upload_form,
                    ajaxform_id='attachments_form',
                    ajaxform_action=upload_form.action,
                    ajaxform_spinner=spinner_icon,
                    table=attachments_table,
                    attachments=article.attachments)

    @require(predicates.in_group('smallpress'))
    @validate(dict(attachment=SQLAEntityConverter(Attachment)))
    @expose()
    def rmattachment(self, attachment):
        article = attachment.article
        DBSession.delete(attachment)
        flash(_('Attachment successfully removed'))
        return redirect(self.mount_point+'/edit/%s'%article.uid)

    @require(predicates.in_group('smallpress'))
    @validate(dict(article=SQLAEntityConverter(Article)), error_handler=manage)
    @expose()
    def publish(self, article):
        article.published=True
        flash(_('Article published'))
        return redirect(self.mount_point+'/manage')

    @require(predicates.in_group('smallpress'))
    @validate(dict(article=SQLAEntityConverter(Article)), error_handler=manage)
    @expose()
    def hide(self, article):
        article.published=False
        flash(_('Article hidden'))
        return redirect(self.mount_point+'/manage')

    @require(predicates.in_group('smallpress'))
    @validate(dict(article=SQLAEntityConverter(Article)), error_handler=manage)
    @expose()
    def delete(self, article):
        DBSession.delete(article)
        flash(_('Article successfully removed'))
        return redirect(self.mount_point+'/manage')

    @expose('genshi:smallpress.templates.index')
    @validate(dict(text=UnicodeString(not_empty=True)), error_handler=index)
    def search(self, text=None):
        articles = []

        index_path = config.get('smallpress_whoosh_index', '/tmp/smallpress_whoosh')
        ix = whoosh.index.open_dir(index_path)
        with ix.searcher() as searcher:
            query = Or([Term("content", text),
                        Term("title", text),
                        Term("description", text)])
            found = searcher.search(query)
            if len(found):
                articles = Article.get_published().filter(Article.uid.in_([e['uid'] for e in found])).all()

        tags = Tagging.tag_cloud_for_set(Article).all()
        return dict(articles=articles, tags=tags)
