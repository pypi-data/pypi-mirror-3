# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from tgext.pluggable import PluggableSession, app_model
import tgext.tagging

DBSession = PluggableSession()
DeclarativeBase = declarative_base()

def init_model(app_session):
    DBSession.configure(app_session)

Tag, Tagging = tgext.tagging.setup_model({'DBSession':DBSession,
                                          'DeclarativeBase':DeclarativeBase,
                                          'User':app_model.User,
                                          'metadata':DeclarativeBase.metadata})

from models import Article, Attachment

