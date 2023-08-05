import inspect
import metadata
import app_auth

def setup_model(models=None):
    if not models:
        models = inspect.currentframe().f_back.f_locals
    
    metadata.DBSession = models['DBSession']
    metadata.DeclarativeBase = models['DeclarativeBase']
    metadata.metadata = models['metadata']
    app_auth.User = models['User']

    from tagging import Tag, Tagging
    return Tag, Tagging