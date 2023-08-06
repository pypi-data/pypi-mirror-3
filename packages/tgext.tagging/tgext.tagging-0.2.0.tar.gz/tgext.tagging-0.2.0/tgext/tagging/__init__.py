from model import setup_model

try:
    #This is here to make TW2 serve the image
    from tw2.core import Link
    register_delete_image = Link(modname='tgext.tagging', filename='static/delete.png')
except ImportError:
    pass

class PlugTagging(object):
    def __init__(self, app_config):
        self.app_config = app_config

    def plug(self):
        app_config = self.app_config

        app_models = dict(DBSession=app_config.model.DBSession,
                          DeclarativeBase=app_config.model.DeclarativeBase,
                          metadata=app_config.model.metadata,
                          User=app_config.model.User)
        app_config.model.Tag, app_config.model.Tagging = setup_model(app_models)

def plugme(app_config, options):
    app_config.register_hook('startup', PlugTagging(app_config).plug)
    return dict(appid='tgext.tagging', plug_controller=False)