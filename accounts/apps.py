from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # This line is kept as is
    name = 'accounts'

    def ready(self):
        import accounts.signals  # This ensures that the signals are connected
