# -*- coding: utf-8 -*-
from tg import request

from datetime import datetime
from sqlalchemy import *
from sqlalchemy import Table, ForeignKey, Column, and_
from sqlalchemy.types import Unicode, Integer, DateTime, Boolean
from sqlalchemy.orm import backref, relation, synonym, MapperExtension
from sqlalchemy.ext.declarative import synonym_for

from metadata import DeclarativeBase, metadata, DBSession
from app_auth import User
from sautils import get_primary_key

import re
clean_up_regexp = re.compile('[^a-zA-Z0-9]')

class Tag(DeclarativeBase):
    class Hooks(MapperExtension):
        def before_insert(self, mapper, connection, instance):
            instance.name = clean_up_regexp.sub('', instance.name.strip().lower())

        def before_update(self, mapper, connection, instance):
            instance.name = clean_up_regexp.sub('', instance.name.strip().lower())

    __tablename__ = 'tgext_tagging_tags'
    __mapper_args__ = {'extension': Hooks()}


    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    last_use = Column(DateTime, nullable=False, default=datetime.now)

    @classmethod
    def lookup(cls, tag_name):
        tag = DBSession.query(cls).filter_by(name=tag_name.strip().lower()).first()
        if tag:
            return tag

    @classmethod
    def lookup_list(cls, tag_list_as_string):
        tag_names = tag_list_as_string.split(',')
        tags = {'found':[], 'missing':[]}

        for tag in tag_names:
            tag = clean_up_regexp.sub('', tag.strip().lower())
            found = Tag.lookup(tag)
            if found:
                tags['found'].append(found)
            else:
                tags['missing'].append(tag)

        return tags


class Tagging(DeclarativeBase):
    __tablename__ = 'tgext_tagging_taggings'

    id = Column(Integer, autoincrement=True, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    taggable_id = Column(Integer, nullable=False, index=True)
    taggable_type = Column(String(255), nullable=False, index=True)

    user_id = Column(Integer, ForeignKey('%s.%s' % (User.__tablename__, get_primary_key(User))),
                              nullable=True)
    user = relation(User, primaryjoin=user_id == getattr(User, get_primary_key(User)), uselist=False,
                            backref=backref("perfomed_tagging", order_by=desc('created_at'),
                                                                cascade='all, delete-orphan'))

    tag_id = Column(Integer, ForeignKey('tgext_tagging_tags.id'), nullable=False)
    tag = relation('Tag', backref=backref('taggings', cascade="all, delete-orphan"), uselist=False)

    @classmethod
    def items_for_tags(cls, Type, tags):
        type_primary_key = get_primary_key(Type)
        tags = tags.split(',')
        
        return DBSession.query(Type).join((Tagging, Tagging.taggable_id == getattr(Type, type_primary_key)))\
                                    .join((Tag, Tag.id == Tagging.tag_id))\
                                    .filter(Tagging.taggable_type == Type.__name__)\
                                    .filter(Tag.name.in_(tags))\
                                    .group_by(Tagging.taggable_id)\
                                    .having(func.count(Tagging.taggable_id) == len(tags))

    @classmethod
    def tag_cloud_for_user(cls, user, Type=None):
        q = DBSession.query(Tag.name, func.count('*').label('tags_count')).join(Tagging)\
                     .filter(Tagging.user == user)

        if Type:
            type_primary_key = get_primary_key(Type)
            q = q.join((Type, getattr(Type, type_primary_key) == Tagging.taggable_id))\
                 .filter(Tagging.taggable_type == Type.__name__)

        q = q.group_by(Tag.id)
        return q.order_by(Tag.name)

    @classmethod
    def tag_cloud_for_object(cls, entry):
        Type = entry.__class__
        type_primary_key = get_primary_key(Type)
        oid = getattr(entry, type_primary_key)
        
        q = DBSession.query(Tag.name, func.count('*').label('tags_count')).join(Tagging)\
                     .join((Type, getattr(Type, type_primary_key) == Tagging.taggable_id))\
                     .filter(getattr(Type, type_primary_key) == oid)\
                     .filter(Tagging.taggable_type == Type.__name__)\
                     .group_by(Tag.id)
        return q.order_by(Tag.name)

    @classmethod
    def tag_cloud_for_set(cls, Type, set=None):
        type_primary_key = get_primary_key(Type)

        if set:
            filter_on_items = [Tagging.taggable_id == getattr(o, type_primary_key) for o in set]
            if not filter_on_items:
                return []

        q = DBSession.query(Tag.name, func.count('*').label('tags_count'))\
                     .join(Tagging).filter(Tagging.taggable_type == Type.__name__)

        if set:
            q = q.filter(or_(*filter_on_items))

        q = q.group_by(Tag.id)
        return q.order_by(Tag.name)

    @classmethod
    def add_tags(cls, entry, tags, user=None):
        Type = entry.__class__
        oid = getattr(entry, get_primary_key(Type))
        
        tags = Tag.lookup_list(tags)
        tag_cloud = [x[0] for x in cls.tag_cloud_for_object(entry)]
            
        for tag in tags['found']:
            if tag.name not in tag_cloud and tag.name != '':
                try:
                    tagging = Tagging(taggable_type=Type.__name__, taggable_id=oid,
                                      user=user, tag=tag)
                    DBSession.add(tagging)
                    tag.last_use = datetime.now()
                except IntegrityError:
                    pass

        for tag in tags['missing']:
            if tag:
                check_just_been_added = Tag.lookup_list(tag)
                if check_just_been_added['found']:
                    continue

                tag = Tag(name=tag.strip().lower())
                DBSession.add(tag)
                DBSession.flush()
                try:
                    tagging = Tagging(taggable_type=Type.__name__, taggable_id=oid,
                                      user=user, tag=tag)
                    DBSession.add(tagging)
                except IntegrityError:
                    pass

    @classmethod
    def del_tags(cls, entry, tags):
        Type = entry.__class__
        oid = getattr(entry, get_primary_key(Type))
        
        tags = Tag.lookup_list(tags)
        tag_cloud = (x[0] for x in cls.tag_cloud_for_object(entry))

        for tag in tags['found']:
            if tag.name in tag_cloud:
                tagging = DBSession.query(Tagging).filter(Tagging.tag_id == tag.id)\
                                                  .filter(Tagging.taggable_type == Type.__name__)\
                                                  .filter(Tagging.taggable_id == oid).first()
                if tagging:
                    DBSession.delete(tagging)
 
    @classmethod
    def set_tags(cls, entry, tags):
        Type = entry.__class__
        oid = getattr(entry, get_primary_key(Type))

        item_tag_cloud = (x[0].lower() for x in cls.tag_cloud_for_object(entry))
        tags_to_set = list(set(x.strip().lower() for x in tags.split(',')))
        tags_to_remove = filter(lambda tag : tag not in tags_to_set, item_tag_cloud)

        cls.del_tags(entry, ",".join(tags_to_remove))
        cls.add_tags(entry, ",".join(tags_to_set))
