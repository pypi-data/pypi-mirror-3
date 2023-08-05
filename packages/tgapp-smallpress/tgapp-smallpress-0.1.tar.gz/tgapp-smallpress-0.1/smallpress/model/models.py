from tg import request, config

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import backref, relation
from sqlalchemy import event

import os
from datetime import datetime
from smallpress.model import DeclarativeBase, DBSession
from tgext.pluggable import app_model, primary_key
from tgext.datahelpers.fields import Attachment as DataHelpersAttachment
from tgext.pluggable import call_partial

import whoosh
import whoosh.index
import whoosh.fields
WHOOSH_SCHEMA = whoosh.fields.Schema(uid=whoosh.fields.ID(stored=True),
                                     title=whoosh.fields.TEXT(stored=True),
                                     description=whoosh.fields.TEXT,
                                     content=whoosh.fields.TEXT)

class Article(DeclarativeBase):
    __tablename__ = 'smallpress_articles'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(Unicode(150), nullable=False, default=u"Untitled", index=True)
    published = Column(Integer, nullable=False, default=0)
    private = Column(Integer, nullable=False, default=0)

    author_id = Column(Integer, ForeignKey(primary_key(app_model.User)))
    author = relation(app_model.User, backref=backref('articles'))

    publish_date = Column(DateTime, nullable=False, default=datetime.now)
    description = Column(Unicode(150), nullable=False, default=u'Empty article, edit or delete this')
    content = Column(Unicode(32000), nullable=False, default=u'')

    def refresh_whoosh(self, action=0):
        index_path = config.get('smallpress_whoosh_index', '/tmp/smallpress_whoosh')
        ix = whoosh.index.open_dir(index_path)
        writer = ix.writer()

        if action == 1:
            writer.add_document(uid=unicode(self.uid), title=self.title,
                                content=self.content,
                                description=self.description)
        elif action == -1:
            writer.delete_by_term('uid', unicode(self.uid))
        else:
            writer.update_document(uid=unicode(self.uid), title=self.title,
                                   content=self.content,
                                   description=self.description)
        writer.commit()

    @staticmethod
    def after_update(mapper, connection, obj):
        obj.refresh_whoosh(0)

    @staticmethod
    def after_insert(mapper, connection, obj):
        obj.refresh_whoosh(1)

    @staticmethod
    def before_delete(mapper, connection, obj):
        obj.refresh_whoosh(-1)

        from smallpress.model import Tagging
        DBSession.query(Tagging).filter(Tagging.taggable_type == 'Article')\
                                .filter(Tagging.taggable_id == obj.uid).delete()

    @staticmethod
    def get_published():
        now = datetime.now()
        articles = DBSession.query(Article).filter_by(published=True)\
                                           .filter(Article.publish_date<=now)\
                                           .order_by(Article.publish_date.desc())
        return articles

    def tagging_display(self):
        return call_partial('smallpress.partials:article_preview', article=self)

    def is_owner(self, identity):
        if not identity:
            return False

        return identity['user'] == self.author

event.listen(Article, 'after_update', Article.after_update)
event.listen(Article, 'after_insert', Article.after_insert)
event.listen(Article, 'before_delete', Article.before_delete)

class Attachment(DeclarativeBase):
    __tablename__ = 'smallpress_attachments'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(16), nullable=False)
    content = Column(DataHelpersAttachment)

    article_id = Column(Integer, ForeignKey(Article.uid))
    article = relation(Article, backref=backref('attachments', cascade='all, delete-orphan'))

    @staticmethod
    def delete_file(mapper, connection, obj):
        try:
            os.unlink(obj.content.local_path)
        except:
            pass

    @property
    def url(self):
        return self.content.url

event.listen(Attachment, 'before_delete', Attachment.delete_file)