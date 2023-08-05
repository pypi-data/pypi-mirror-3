from tw.api import Widget, JSLink, CSSLink
from tw.jquery import jquery_js
import tg

class TagCloud(Widget):
    template = "genshi:tgext.tagging.templates.tagcloud"
    javascript = [jquery_js, JSLink(modname='tgext.tagging', filename='static/tagging.js')]
    css = [CSSLink(modname='tgext.tagging', filename='static/tagging.css')]

    params = {'tagging_url': 'Url of the tagging controller'}

    tagging_url = '/tagging'

    def update_params(self, d):
        super(TagCloud, self).update_params(d)
        d['tg_url'] = tg.url
        d['weight_min'] = 0
        d['weight_max'] = max((t[1] for t in d['value']))
        d['weight_range'] = d['weight_max'] - d['weight_min']

        
    
    
