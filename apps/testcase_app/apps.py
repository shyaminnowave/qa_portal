from django.apps import AppConfig


class TestcaseAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.testcase_app'

    def ready(self) -> None:
        import apps.testcase_app.signals