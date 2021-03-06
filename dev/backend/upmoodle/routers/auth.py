from django.views.decorators.csrf import csrf_exempt

from upmoodle.controllers.decorators.exceptions import zero_exceptions
from upmoodle.controllers.decorators.router import method, authenticated
from upmoodle.models import OkMessage
from upmoodle.routers.response.factory import ResponseFactory
from upmoodle.services.auth import AuthService


@zero_exceptions
@csrf_exempt
@method('POST')
def login(request, session_token=None, data=None):
    cookies = AuthService.login(session_token=session_token, data=data)
    return ResponseFactory().ok(message_id=OkMessage.Type.SUCCESS_LOGIN).cookies(cookies=cookies).build()


@zero_exceptions
@csrf_exempt
@method('POST')
def signup(request, session_token=None, data=None):
    cookies = AuthService.signup(session_token=session_token, data=data)
    return ResponseFactory().ok(message_id=OkMessage.Type.SUCCESS_SIGNUP).cookies(cookies=cookies).build()


@zero_exceptions
@csrf_exempt
@authenticated
@method('POST')
def logout(request, session_token=None, **kwargs):
    cookies = AuthService.logout(session_token=session_token)
    return ResponseFactory().ok(message_id=OkMessage.Type.SUCCESS_LOGOUT).cookies(cookies=cookies).build()


@zero_exceptions
@csrf_exempt
@method('POST')
def confirm_email(request, data=None, **kwargs):
    AuthService.confirm_email(session_token=data['token'])
    return ResponseFactory().ok(message_id=OkMessage.Type.ACCOUNT_VALIDATED).build()


@zero_exceptions
@csrf_exempt
@method('POST')
def recover_password(request, data=None, **kwargs):
    AuthService.recover_password(data)
    return ResponseFactory().ok(message_id=OkMessage.Type.RECOVER_PASS_EMAIL).build()
