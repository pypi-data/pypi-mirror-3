from tgext.tagging.model.tagging import Tag
from model_meta import DBSession

class TestTags(object):
    def teardown(self):
        DBSession.rollback()
    
    def test_case_insensitive_tag(self):
        DBSession.add(Tag(name='Hi'))
        tag = Tag.lookup('hi')

        assert tag
        assert tag.name == 'hi'

    def test_case_insensitive_tag2(self):
        DBSession.add(Tag(name='hi'))
        tag = Tag.lookup('Hi')

        assert tag
        assert tag.name == 'hi'

    def test_list_lookup(self):
        DBSession.add(Tag(name='tag1'))
        DBSession.add(Tag(name='tag2'))

        tags = Tag.lookup_list('tag1, tag2, tag3')
        assert len(tags['found']) == 2
        assert len(tags['missing']) == 1
