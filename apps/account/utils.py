import string
import requests
from requests.auth import HTTPBasicAuth
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_user():
    try:
        letters = string.ascii_letters
    except AttributeError:
        letters = string.letters
    allowed_char = letters + string.digits + '_'
    username = get_random_string(length=15, allowed_chars=allowed_char)
    try:
        User.objects.get(username=username)
        return generate_user()
    except User.DoesNotExist:
        return username
        

def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


def get_project(data):
    project_url = f"{data.get('domain_url')}/rest/api/3/project"
    auth = HTTPBasicAuth(data.get('username'), data.get('token'))
    response = requests.get(project_url, auth=auth)
    projects = []
    if response.status_code == 200:
        for names in response.json():
            projects.append(names['name'])
        return projects
    else:
        return None


def new_get_project(data):
    project_url = f"{data.get('domain_url')}/rest/api/3/project"
    auth = HTTPBasicAuth(data.get('username'), data.get('token'))
    response = requests.get(project_url, auth=auth)
    projects = []
    if response.status_code == 200:
        for names in response.json():
            project = {
                'key': names['key'],
                'name': names['name']
            }
            projects.append(project)
        return projects
    else:
        return None