import tw.forms as twf
import genshi
from genshi.template import MarkupTemplate
from libacr.model.core import DBSession
from libacr.model.content import View
import ConfigParser, StringIO, cgi, base64, mimetypes
from tw.tinymce import TinyMCE, MarkupConverter

from libacr.lib import get_slices_with_tag, get_page_from_urllist
import libacr.helpers as h
from libacr.form_fields import AdvancedFileField

class UserDefinedViewRendererTemplate(object):
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.exposed = True
        self.acr_dict = {'slices_with_tag':get_slices_with_tag,
                         'page_from_urllist':get_page_from_urllist,
                         'preview_slice':h.preview_slice,
                         'render_slice':h.render_slice,
                         'acr_url':h.acr_url,
                         'markup':genshi.Markup}

    @property
    def fields_names(self):
        fields_declaration_name = '%s_fields' % self.name
        fields = DBSession.query(View).filter_by(name=fields_declaration_name).first()
        fields = fields.properties.items('fields')
        return [field[0] for field in fields]

    @property
    def form_fields(self):
        fields_declaration_name = '%s_fields' % self.name
        fields = DBSession.query(View).filter_by(name=fields_declaration_name).first()
        fields = fields.properties.items('fields')

        tw_fields = []
        for name, field_type in fields:
            required = False
            if name.startswith('*'):
                name = name[1:]
                required = True

            if field_type.lower() == 'text':
                validator = required and twf.validators.String(not_empty=True) or twf.core.DefaultValidator()
                tw_fields.append(twf.TextField(name, label_text="%s:" % name.capitalize(),
                                            validator=validator))
            elif field_type.lower() == 'textarea':
                validator = required and twf.validators.String(not_empty=True) or twf.core.DefaultValidator()
                tw_fields.append(twf.TextArea(name, label_text="%s:" % name.capitalize(),
                                                    validator=validator))
            elif field_type.lower() == 'html':
                tw_fields.append(TinyMCE(name, label_text="%s:" % name.capitalize(), validator=MarkupConverter(),
                                         rows=20, attrs={'style':'width:100%;height:400px;'},
                                         mce_options=dict(theme_advanced_buttons1= """bold,italic,underline,
strikethrough,separator,justifyleft,justifycenter,justifyright,justifyfull,separator,
fontselect,fontsizeselect,separator,forecolor,backcolor""")))
            elif field_type.lower().startswith('select'):
                choices = field_type[len('select'):].split(',')
                tw_fields.append(twf.SingleSelectField('show_title', label_text="%s:" % name.capitalize(),
                                                       options=choices))
            elif field_type.lower() == 'file':
                validator = required and twf.validators.FieldStorageUploadConverter(not_empty=True) or\
                                         twf.validators.FieldStorageUploadConverter(not_empty=False)
                tw_fields.append(AdvancedFileField(name, label_text="%s:" % name.capitalize(),
                                                        validator=validator))

        return tw_fields

    def from_dict(self, dic):
        config = ConfigParser.ConfigParser()
        config.add_section(self.name.encode('ascii'))

        for name in self.fields_names:
            if name.startswith('*'):
                name = name[1:]

            if isinstance(dic[name], cgi.FieldStorage):
                value = "data:%s;base64," % (mimetypes.guess_type(dic[name].filename)[0] or "application/octet-stream")
                value += base64.b64encode(dic[name].file.read())
                config.set(self.name.encode('ascii'), name.encode('ascii'), value)
            else:
                if isinstance(dic[name], unicode):
                    dic[name] = dic[name].encode('utf-8')
                config.set(self.name.encode('ascii'), name.encode('ascii'), dic[name] and dic[name] or '')

        s = StringIO.StringIO()
        config.write(s)
        return s.getvalue().decode('utf-8')

    def to_dict(self, data):
        config = ConfigParser.ConfigParser()
        config.readfp(StringIO.StringIO(data))

        d = {}
        for name, value in config.items(self.name):
            d[str(name)] = value
        return d

    def render(self, page, slice, data):
        from libacr.lib import language
        data_as_dict = self.to_dict(data)

        try:
            t = MarkupTemplate(u'<html xmlns:py="http://genshi.edgewall.org/" py:strip="">%s</html>' % self.code)
            t = t.generate(acr=self.acr_dict, slice_uid=slice.uid, slice=slice, lang=language()[0], **data_as_dict)
            return t.render('xhtml').decode('utf-8')
        except Exception, e:
            return str(e)

    def preview(self, page, slice, data):
        preview_template_name = '%s_preview' % self.name
        preview = DBSession.query(View).filter_by(name=preview_template_name).first()

        if not preview:
            return 'Preview not Implemented'

        data_as_dict = self.to_dict(data)
        try:
            t = MarkupTemplate(u'<html xmlns:py="http://genshi.edgewall.org/" py:strip="">%s</html>' % preview.code)
            t = t.generate(acr=self.acr_dict, slice_uid=slice.uid, **data_as_dict)
            return t.render('xhtml').decode('utf-8')
        except Exception, e:
            return str(e)
