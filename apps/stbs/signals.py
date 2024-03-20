from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.stbs.models import Language

# @receiver(post_save, sender=Language)
# def capture_request_langugae_info(sender, instance, **kwargs):
#     request = kwargs.get('request')
#     if request:
#         instance.history_user = request.user
#         instance.request_method = request.method
#     else:
#         # For Django admin modifications
#         instance.history_user = None
#         instance.request_method = 'POST'