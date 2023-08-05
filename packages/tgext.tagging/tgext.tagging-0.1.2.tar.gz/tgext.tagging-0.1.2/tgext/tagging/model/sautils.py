import inspect
from sqlalchemy.types import Integer
from sqlalchemy.orm import class_mapper

#mostly adapted from sprox

def get_fields(entity):
    if inspect.isfunction(entity):
        entity = entity()
        
    mapper = class_mapper(entity)
    field_names = mapper.c.keys()
    for prop in mapper.iterate_properties:
        try:
            getattr(mapper.c, prop.key)
            field_names.append(prop.key)
        except AttributeError:
            mapper.get_property(prop.key)
            field_names.append(prop.key)

    return field_names

def get_primary_key(entity):
    if inspect.isfunction(entity):
        entity = entity()
        
    mapper = class_mapper(entity)
    for field_name in get_fields(entity):
        try:
            value = getattr(mapper.c, field_name)
        except AttributeError:
            continue
        
        if value.primary_key:
            if not isinstance(value.type, Integer):
                raise LookupError('Primary Key is not an Integer column')
            return value.key

    #should never arrive here, SQLA should not map tables without primary keys
    raise LookupError('No primary keys found')
