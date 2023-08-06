from tw_compat import TW1, TW2, FakeW
import tg

if TW2:
    from tw2.core import Param

    class TagCloud(TW2.Widget):
        template = "genshi:tgext.tagging.templates.tagcloud"
        resources= [TW2.jquery_js, TW2.JSLink(modname='tgext.tagging', filename='static/tagging.js'),
                    TW2.CSSLink(modname='tgext.tagging', filename='static/tagging.css')]

        tagging_url = Param(description='Url of the tagging controller', default='/tagging')

        def prepare(self):
            super(TagCloud, self).prepare()

            self.tg_url = tg.url
            self.weight_min = 0
            try:
                self.weight_max = max((t[1] for t in self.value))
            except ValueError:
                self.weight_max = 0
            self.weight_range = self.weight_max - self.weight_min
    
if not TW2:
    class TagCloud(TW1.Widget):
        template = "genshi:tgext.tagging.templates.tagcloud"
        javascript = [TW1.jquery_js, TW1.JSLink(modname='tgext.tagging', filename='static/tagging.js')]
        css = [TW1.CSSLink(modname='tgext.tagging', filename='static/tagging.css')]
    
        params = {'tagging_url': 'Url of the tagging controller'}
    
        tagging_url = '/tagging'
    
        def update_params(self, d):
            super(TagCloud, self).update_params(d)
            d['tg_url'] = tg.url
            d['weight_min'] = 0
            try:
                d['weight_max'] = max((t[1] for t in d['value']))
            except ValueError:
                d['weight_max'] = 0
            d['weight_range'] = d['weight_max'] - d['weight_min']
            d['w'] = FakeW(d)
    
            
        
        
