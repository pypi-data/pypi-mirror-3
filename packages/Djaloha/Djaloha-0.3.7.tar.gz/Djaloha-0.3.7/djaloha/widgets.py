# -*- coding: utf-8 -*-

from floppyforms.widgets import TextInput
from django.utils.encoding import force_unicode
from django.forms import Media
from django.core.urlresolvers import reverse

class AlohaInput(TextInput):
    """
    Text widget with aloha html editor
    requires floppyforms to be installed
    """
    
    template_name='djaloha/alohainput.html'
    
    def __init__(self, *args, **kwargs):
        self._text_color_plugin = kwargs.pop('text_color_plugin', True)
        super(AlohaInput, self).__init__(*args, **kwargs)
    
    def _get_media(self):
        """
        return code for inserting required js and css files
        need aloha , plugins and initialization
        include the 3rd party ImagePlugin from tapo: make possible to drag-and-drop and edit images
        """
        
        css = {
            'all': (
                "aloha/plugins/at.tapo.aloha.plugins.Image/resources/imageplugin.css",
                "css/djaloha.css",
            )
        }
        
        js = (
            "js/_lib/jquery.cookie.js",
            "aloha/sizzle.js",
            "aloha/ext-jquery-adapter.js",
            "aloha/ext-all.js",
            "aloha/aloha-nodeps.js",
            "aloha/plugins/com.gentics.aloha.plugins.Format/plugin.js",
            "aloha/plugins/com.gentics.aloha.plugins.List/plugin.js",
            "aloha/plugins/com.gentics.aloha.plugins.HighlightEditables/plugin.js",
            "aloha/plugins/com.gentics.aloha.plugins.Table/plugin.js",
            "aloha/plugins/com.gentics.aloha.plugins.Link/plugin.js",
            "aloha/plugins/com.gentics.aloha.plugins.Link/LinkList.js",
            "aloha/plugins/com.gentics.aloha.plugins.Paste/plugin.js",
            "aloha/plugins/com.gentics.aloha.plugins.Paste/wordpastehandler.js",
            "aloha/plugins/at.tapo.aloha.plugins.Image/plugin.js",
        )
        
        if self._text_color_plugin:
            js = js + ("aloha/plugins/TextColor/plugin.js",)

        js = js + (reverse('aloha_init'), )
        
        return Media(css=css, js=js)
    
    media = property(_get_media)
