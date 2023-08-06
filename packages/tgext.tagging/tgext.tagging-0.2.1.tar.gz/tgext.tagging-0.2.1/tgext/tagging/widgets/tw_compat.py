try:
    from tw.api import JSLink as Tw1JSLink,\
                      CSSLink as Tw1CSSLink, \
                       Widget as Tw1Widget
    class TW1:
        JSLink = Tw1JSLink
        CSSLink = Tw1CSSLink
        Widget = Tw1Widget
except ImportError:
    TW1 = None


try:
    from tw2.core.resources import JSLink as Tw2JSLink, \
                                  CSSLink as Tw2CSSLink
    from tw2.core import Widget as Tw2Widget
    class TW2:
        JSLink = Tw2JSLink
        CSSLink = Tw2CSSLink
        Widget = Tw2Widget
except ImportError:
    TW2 = None

if TW2:
    from tw2.jquery import jquery_js as tw2_jquery_js
    TW2.jquery_js = tw2_jquery_js

if TW1 and not TW2:
    from tw.jquery import jquery_js as tw1_jquery_js
    TW1.jquery_js = tw1_jquery_js

def is_tw2_form(w):
    return hasattr(w, 'req')

class FakeW(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError()

    @property
    def compound_id(self):
        return self['id']
