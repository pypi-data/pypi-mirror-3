from tw_compat import TW1, TW2, FakeW
import tg

from tgext.tagging.model.sautils import get_primary_key
Tagging = None

if TW2:
    from tw2.core import Param

    class TagList(TW2.Widget):
        template = "genshi:tgext.tagging.templates.taglist"
        resources= [TW2.jquery_js, TW2.JSLink(modname='tgext.tagging', filename='static/tagging.js'),
                    TW2.CSSLink(modname='tgext.tagging', filename='static/tagging.css')]

        editmode = Param(description='Enable Tags removal and adding', default=True)
        tagging_url = Param(description='Url of the tagging controller', default='/tagging')

        def prepare(self):
            global Tagging
            if Tagging is None:
                from tgext.tagging.model.tagging import Tagging

            super(TagList, self).prepare()
            self.tg_url = tg.url
            self.Tagging = Tagging
            if not isinstance(self.value, dict):
                obj = self.value
                self.value = {'target_id': getattr(obj, get_primary_key(obj.__class__)),
                              'tag_list': Tagging.tag_cloud_for_object(obj)}
if not TW2:
    class TagList(TW1.Widget):
        template = "genshi:tgext.tagging.templates.taglist"
        javascript = [TW1.jquery_js, TW1.JSLink(modname='tgext.tagging', filename='static/tagging.js')]
        css = [TW1.CSSLink(modname='tgext.tagging', filename='static/tagging.css')]

        params = {'editmode': 'Enable Tags removal and adding',
                  'tagging_url': 'Url of the tagging controller'}

        editmode = True
        tagging_url = '/tagging'

        def update_params(self, d):
            global Tagging
            if Tagging is None:
                from tgext.tagging.model.tagging import Tagging

            super(TagList, self).update_params(d)
            d['tg_url'] = tg.url
            d['Tagging'] = Tagging
            if not isinstance(d['value'], dict):
                d['value'] = {'target_id': getattr(d['value'], get_primary_key(d['value'].__class__)),
                               'tag_list': Tagging.tag_cloud_for_object(d['value'])}
            d['w'] = FakeW(d)