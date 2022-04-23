from django.apps import AppConfig


class MyfolderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myfolder'
    def ready(self):
        import myfolder.signals
