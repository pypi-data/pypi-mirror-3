from tgext.tagging.model.tagging import Tagging, Tag
from model_meta import DBSession, User, FakeObject

class TestTagging(object):
    def teardown(self):
        DBSession.rollback()

    def setup(self):
        DBSession.add(User())
        self.fake_o = FakeObject()
        DBSession.add(self.fake_o)
        self.fake_o2 = FakeObject()
        DBSession.add(self.fake_o2)
        self.fake_o3 = FakeObject()
        DBSession.add(self.fake_o3)
        DBSession.flush()
    
    def test_add_tags(self):
        Tagging.add_tags(self.fake_o, 'TaG1,tAg2')

        tags = DBSession.query(Tag).all()
        assert len(tags) == 2
        assert tags[0].name == 'tag1'
        assert tags[1].name == 'tag2'

    def test_repeated_add_tags(self):
        Tagging.add_tags(self.fake_o, 'TaG1,tAg2,tag2,TAG2')

        tags = DBSession.query(Tag).all()
        assert len(tags) == 2
        assert tags[0].name == 'tag1'
        assert tags[1].name == 'tag2'

    def test_tag_cloud(self):
        Tagging.add_tags(self.fake_o, 'TaG1,tAg2,tag2,TAG2')
        tag_cloud = Tagging.tag_cloud_for_object(self.fake_o)
        assert tag_cloud.count() == 2

    def test_tag_cloud_weights(self):
        Tagging.add_tags(self.fake_o, 'TaG1,tAg2,tag2,TAG2')
        Tagging.add_tags(self.fake_o2, 'tag1')

        tag_cloud = Tagging.tag_cloud_for_set(FakeObject, [self.fake_o, self.fake_o2])
        for tag in tag_cloud:
            if tag[0] == 'tag1':
                assert tag[1] == 2
            elif tag[0] == 'tag2':
                assert tag[1] == 1

    def test_tag_cloud_for_type(self):
        Tagging.add_tags(self.fake_o, 'tag1,tag2,tag3')
        Tagging.add_tags(self.fake_o2, 'tag1')
        Tagging.add_tags(self.fake_o3, 'tag1,tag2')

        tag_cloud = Tagging.tag_cloud_for_set(FakeObject)
        assert tag_cloud.count() == 3
        for tag in tag_cloud:
            if tag[0] == 'tag1':
                assert tag[1] == 3
            elif tag[0] == 'tag2':
                assert tag[1] == 2
            elif tag[0] == 'tag3':
                assert tag[1] == 1

    def test_del_tags(self):
        Tagging.add_tags(self.fake_o, 'TaG1,tAg2,tag2,TAG2')
        Tagging.del_tags(self.fake_o, 'tag2')

        tag_cloud = Tagging.tag_cloud_for_object(self.fake_o).all()
        assert len(tag_cloud) == 1
        assert tag_cloud[0].name == 'tag1'

    def test_set_tags(self):
        Tagging.add_tags(self.fake_o, 'TaG1,tAg2,tag2,TAG2')
        tag_cloud = Tagging.tag_cloud_for_object(self.fake_o).all()
        assert len(tag_cloud) == 2

        Tagging.set_tags(self.fake_o, 'tag1,TAG1')
        tag_cloud = Tagging.tag_cloud_for_object(self.fake_o).all()
        assert len(tag_cloud) == 1
        