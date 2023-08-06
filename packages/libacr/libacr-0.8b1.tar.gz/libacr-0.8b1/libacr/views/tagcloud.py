import ConfigParser
from tg import tmpl_context
import StringIO
from libacr.lib import url as acr_url
from libacr.lib import language
from genshi.template import MarkupTemplate

from libacr.model.core import DBSession
from libacr.model.content import Slice, Content, ContentData
import tw.forms as twf

class SearchRenderer(object):
    def __init__(self):
        self.name = 'search'
        self.exposed = True
        self.form_fields = [twf.TextField('expose', label_text="Filter Tag:", default='', validator=twf.validators.String(strip=True))]

    def to_dict(self, data):
        config = ConfigParser.ConfigParser({'expose':''})
        config.readfp(StringIO.StringIO(data))
        return {'expose' : config.get('search', 'expose')}

    def from_dict(self, dic):
        config = ConfigParser.ConfigParser()
        config.add_section('search')
        config.set('search', 'expose', dic.get('expose', ''))

        s = StringIO.StringIO()
        config.write(s)
        return s.getvalue()
    
    def render(self, page, slice, data):
        result = u'''
<div class="acr_search">
  <form action=%s>
    <input type="hidden" name="searchid" value="%s"/>
    <input type="text" name="what" class="acr_search_text" value="search..." 
           onfocus="if (this.value=='search...') {this.value='';}"
           onblur="if (this.value=='') {this.value = 'search...';}"/>
    <input type="submit" value="GO" class="acr_search_btn"/>
  </form>
</div>''' % (acr_url('/search'), unicode(slice.uid))

        return result

    def preview(self, page, slice, data):
        return 'Preview not Implemented'
        
    @staticmethod
    def perform(slice, what):
        search_def = slice.content.data
        config = ConfigParser.ConfigParser({'expose':''})
        config.readfp(StringIO.StringIO(search_def))
        
        expose_tag = config.get('search', 'expose')

        res = DBSession.query(Slice).join(Content).join(ContentData)
        if expose_tag.strip():
            res = res.filter(Slice.tags.any(name=expose_tag.strip()))
        res = res.filter(ContentData.value.like('%' + what + '%'))
       
        return res
        
