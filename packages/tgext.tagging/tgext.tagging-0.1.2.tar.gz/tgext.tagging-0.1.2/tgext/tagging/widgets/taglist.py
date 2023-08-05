from tw.api import Widget, JSLink, CSSLink
from tw.jquery import jquery_js
import tg

from tgext.tagging.model.sautils import get_primary_key

class TagList(Widget):
    template = "genshi:tgext.tagging.templates.taglist"
    javascript = [jquery_js, JSLink(modname='tgext.tagging', filename='static/tagging.js')]
    css = [CSSLink(modname='tgext.tagging', filename='static/tagging.css')]

    params = {'editmode': 'Enable Tags removal and adding',
              'tagging_url': 'Url of the tagging controller'}

    editmode = True
    tagging_url = '/tagging'

    def update_params(self, d):
        from tgext.tagging.model.tagging import Tagging
        
        super(TagList, self).update_params(d)
        d['tg_url'] = tg.url
        d['Tagging'] = Tagging

        if not isinstance(d['value'], dict):
            d['value'] = {'target_id': getattr(d['value'], get_primary_key(d['value'].__class__)),
                           'tag_list': Tagging.tag_cloud_for_object(d['value'])}
    
    
