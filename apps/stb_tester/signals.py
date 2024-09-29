import json
from django.db.models.signals import Signal
from apps.stb_tester.models import StbConfiguration
from django.dispatch import receiver


token_expiry = Signal()

@receiver(token_expiry)
def token_expiry_notification(sender=None, **kwargs):
    print('Testing')
    token = StbConfiguration.objects.get()
    token.is_active = False
    token.save()
    response = {
        "success": False,
        "status": 403,
        "data": "Token Expired",
        "message": "Token Expired Please Renew the Token"
    }
    return json.dumps(response)