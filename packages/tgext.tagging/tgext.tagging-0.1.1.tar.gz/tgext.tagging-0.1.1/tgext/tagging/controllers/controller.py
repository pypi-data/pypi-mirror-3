from tg import expose, flash, require, url, request, redirect
from tg import tmpl_context, validate, config, TGController
from repoze.what import predicates

def can_edit(predicate):
    if not predicate:
        return True
        
    try:
        predicate.check_authorization(pylons.request.environ)
    except WhatNotAuthorizedError, e:
        return False
    except NotAuthorizedError, e:
        return False
    return True

def get_tagging_base_url(request, method):
    pos = request.path.rfind(method)-1
    return request.path[:pos]

class TaggingController(TGController):
    def __init__(self, session, model, allow_edit=None):
        super(TaggingController, self).__init__()
        self.session = session
        self.model = model
        self.allow_edit = allow_edit

    @expose(content_type='text/plain')
    def add(self, target_id, tags, *args, **kw):
        from tgext.tagging.model.tagging import Tagging

        if not can_edit(self.allow_edit):
            return 'DENIED'

        obj = self.session.query(self.model).get(target_id)
        Tagging.add_tags(obj, tags)
        return 'OK'

    @expose(content_type='text/plain')
    def remove(self, target_id, tags, *args, **kw):
        from tgext.tagging.model.tagging import Tagging

        if not can_edit(self.allow_edit):
            return 'DENIED'

        obj = self.session.query(self.model).get(target_id)
        Tagging.del_tags(obj, tags)
        return 'OK'

    @expose('genshi:tgext.tagging.templates.taglist')
    def tags(self, target_id):
        from tgext.tagging.model.tagging import Tagging

        obj = self.session.query(self.model).get(target_id)
        value = {}
        value['tag_list'] = Tagging.tag_cloud_for_object(obj)
        value['target_id'] = target_id

        editmode = can_edit(self.allow_edit)
        base_url = get_tagging_base_url(request, 'tags')
        return dict(value=value, tagging_url=base_url, editmode=editmode, tg_url=url)

    @expose('genshi:tgext.tagging.templates.search')
    def search(self, tags):
        from tgext.tagging.model.tagging import Tagging

        items = Tagging.items_for_tags(self.model, tags)
        return dict(items=items, tags=tags)