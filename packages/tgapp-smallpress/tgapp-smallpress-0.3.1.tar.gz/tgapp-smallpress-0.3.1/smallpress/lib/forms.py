import sys
import tg
from tw.forms import ListForm, TextField, TextArea, HiddenField, FileField
from tw.core import WidgetsList
from tw.forms.validators import UnicodeString, FieldStorageUploadConverter
from tg.i18n import lazy_ugettext as l_
from tgext.ajaxforms import ajaxloaded
from tgext.pluggable import plug_url

class ArticleForm(ListForm):
    class fields(WidgetsList):
        uid = HiddenField()
        title = TextField(label_text='Title', validator=UnicodeString(not_empty=True))
        description = TextField(label_text='Description', validator=UnicodeString(),
                                attrs=dict(placeholder=l_('If empty will be extracted from the content')))
        tags = TextField(label_text='Tags', validator=UnicodeString(),
                         attrs=dict(placeholder=l_('tags, comma separated')))
        content = TextArea(suppress_label=True, validator=UnicodeString(not_empty=True),
                           attrs=dict(id='article_content'))
        publish_date = TextField(label_text='Publish Date')

@ajaxloaded
class UploadForm(ListForm):
    class fields(WidgetsList):
        article = HiddenField()
        name = TextField(label_text='Name', validator=UnicodeString(not_empty=True))
        file = FileField(label_text='File', validator=FieldStorageUploadConverter(not_empty=True))

    action = plug_url('smallpress', '/attach', lazy=True)
    ajaxurl = plug_url('smallpress', '/upload_form_show', lazy=True)
    submit_text = 'Attach'

class SearchForm(ListForm):
    class fields(WidgetsList):
        text = TextField(suppress_label=True, validator=UnicodeString(not_empty=True),
                         attrs=dict(placeholder=l_('Search...')))

    submit_text = 'Search'

def get_article_form():
    config = tg.config['_smallpress']

    article_form = config.get('form_instance')
    if not article_form:
        form_path = config.get('form', 'smallpress.lib.forms.ArticleForm')
        root_module, path = form_path.split('.', 1)
        form_class = reduce(getattr, path.split('.'), sys.modules[root_module])
        article_form = config['form_instance'] = form_class()

    return article_form