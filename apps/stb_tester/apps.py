from django.apps import AppConfig


class StbTesterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.stb_tester'

    def ready(self):
        import apps.stb_tester.signals


