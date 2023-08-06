"""
TinyMCE rich text editor ToscaWidget.

Bundles tinyMCE from http://tinymce.moxiecode.com/

Copyright 2007 Alberto Valverde Gonzalez

Licensed under the LGPL license due to bundled JS library's license.
"""
import os
import re
from warnings import warn

from pkg_resources import resource_filename

from tw.api import JSLink, js_function, adapt_value
from tw.forms import TextArea
from tw.forms.validators import UnicodeString

from genshi.core import Markup, stripentities

__all__ = ["TinyMCE", "MarkupConverter",
           "tiny_mce_js", "tiny_mce_popup_js",
           "mce_options_simple", "mce_options_advanced",
           "mce_options_rich", "mce_options_default"
          ]

class MarkupConverter(UnicodeString):
    """A validator for TinyMCE widget.

    Will make sure the text that reaches python will be unicode un-xml-escaped
    HTML content.

    Will also remove any trailing <br />s tinymce sometimes leaves at the end
    of pasted text.
    """
    cleaner = re.compile(r'(\s*<br />\s*)+$').sub
    if_missing = ''

    def _to_python(self, value, state=None):
        value = super(MarkupConverter, self)._to_python(value, state)
        if value:
            value = Markup(stripentities(value)).unescape()
            return self.cleaner('', value)


def _get_available_languages():
    filename_re = re.compile(r'(\w+)\.js')
    locale_dir = resource_filename("libacr.contrib.tinymce", "static/javascript/langs")
    langs = []
    for filename in os.listdir(locale_dir):
        match = filename_re.match(filename)
        if match:
            langs.append(match.groups(0)[0])
    return langs

from tw.jquery.base import jquery_js

tiny_mce_js = JSLink(
    modname = "libacr.contrib.tinymce",
    filename = 'static/javascript/tiny_mce.js',
    javascript = [jquery_js],
    init = js_function('tinyMCE.init'),
    )

tiny_mce_popup_js = JSLink(
    modname = "libacr.contrib.tinymce",
    filename = 'static/javascript/tiny_mce_popup.js',
    javascript = [tiny_mce_js],
    )

# old name
tinyMCE = tiny_mce_js


# Here are a few example mce_options to allow you not to start from scratch:

mce_options_simple = {
    'theme' : "simple",
}

mce_options_advanced = {
    'theme' : "advanced",
}

mce_options_rich = {
    'theme' : "advanced",
    'plugins' : "safari,pagebreak,style,layer,table,save,advhr,advimage,advlink,emotions,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template",
    # Theme options
    'theme_advanced_buttons1' : "save,newdocument,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,styleselect,formatselect,fontselect,fontsizeselect",
    'theme_advanced_buttons2' : "cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code,|,insertdate,inserttime,preview,|,forecolor,backcolor",
    'theme_advanced_buttons3' : "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,media,advhr,|,print,|,ltr,rtl,|,fullscreen",
    'theme_advanced_buttons4' : "insertlayer,moveforward,movebackward,absolute,|,styleprops,|,cite,abbr,acronym,del,ins,attribs,|,visualchars,nonbreaking,template,pagebreak",
    'theme_advanced_toolbar_location' : "top",
    'theme_advanced_toolbar_align' : "left",
    'theme_advanced_statusbar_location' : "bottom",
    'theme_advanced_resizing' : True,
}

mce_options_default = {
    'theme': "advanced",
    'plugins': "advimage",
    'theme_advanced_toolbar_location': "top",
    'theme_advanced_toolbar_align': "center",
    'theme_advanced_statusbar_location': "bottom",
    'extended_valid_elements': "a[href|target|name]",
    'theme_advanced_resizing': True,
    'paste_use_dialog': False,
    'paste_auto_cleanup_on_paste': True,
    'paste_convert_headers_to_strong': False,
    'paste_strip_class_attributes': "all",
}

class TinyMCE(TextArea):
    """TinyMCE WYSIWYG rich text editor.

    You can pass options directly to tinyMCE JS object at consruction or
    display via the ``mce_options`` dict parameter.

    Allows localization. To see available languages peek into the ``langs``
    attribute of the TinyMCE class. Language codes can be passed as the
    ``locale`` parameter to display or provide a default at construction
    time. To dynamically switch languages based on HTTP headers a callable
    can be passed to return a language code by parsing/fetching headers
    whereever the app/framework makes them available. Same technique can be
    used to use cookies, session data or whatever.

    If a custom validator is supplied, it is recommended that it inherits from
    ``toscawidgets.widgets.tinymce.MarkupConverter`` to deal with markup
    conversion and unicode issues.
    """
    javascript = [tiny_mce_js]
    langs = _get_available_languages()
    locale = 'en'
    params = ["mce_options", "locale"]
    cols = 79
    rows = 25
    mce_options = {}
    default_options = mce_options_default
    validator = MarkupConverter
    include_dynamic_js_calls = True

    def update_params(self, d):
        super(TinyMCE, self).update_params(d)
        options = self.default_options.copy()
        options.update(d.mce_options)
        if d.locale in self.langs:
            options.setdefault('language', d.locale)
        else:
            warn("Language file for '%s' not available" % d.locale)
            d.locale = 'en'
        if options.setdefault('mode', 'exact') == 'exact':
            options['elements'] = d.id
        # Next line creates a javascript call which will be placed at bodybottom
        # to initialize tinyMCE with desired options.
        self.add_call(tiny_mce_js.init(options))
