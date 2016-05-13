import uuid

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone

from backend import settings
from backend.settings import SESSION_COOKIE_NAME
from upmoodle.models import User
from upmoodle.models.exceptions.messageBasedException import MessageBasedException
from upmoodle.models.message.errorMessage import ErrorMessage
from upmoodle.models.message.okMessage import OkMessage
from upmoodle.models.utils.jsonResponse import JsonResponse
from upmoodle.models.utils.newJsonResponse import NewJsonResponse
from upmoodle.models.utils.requestException import RequestException
from upmoodle.services.utils.email import EmailService
from upmoodle.services.utils.randoms import RandomStringsService


class AuthService:

    def __init__(self):
        pass

    @staticmethod
    def get_cookie(session_token):
        if not session_token:
            return uuid.uuid4().hex
        else:
            return session_token

    @staticmethod
    def login(session_token=None, data=None):
        try:
            session_token = AuthService.get_cookie(session_token)

            request_email = data['email']
            request_pass = data['password']
            user = User.objects.get(email=request_email, password=request_pass)
            if not user.confirmedEmail:
                return MessageBasedException(message_id=ErrorMessage.Type.UNCONFIRMED_EMAIL).get_json_response()
            else:
                user.sessionToken = session_token
                user.lastTimeActive = timezone.now()
                user.save()
                json_response = JsonResponse(message_id=OkMessage.Type.SUCCESS_LOGIN)
                json_response.set_cookie(settings.SESSION_COOKIE_NAME, session_token)
                return json_response
        except (ObjectDoesNotExist, KeyError):
            return MessageBasedException(message_id=ErrorMessage.Type.INCORRECT_DATA).get_json_response()
        except RequestException as r:
            return r.jsonResponse

    @staticmethod
    def signup(session_token=None, data=None):
        try:
            session_token = AuthService.get_cookie(session_token)

            user = User.parse(data, sessionToken=session_token, fields=['email', 'password', 'nick', 'name'])
            EmailService.send_signup_confirmation_email(email=user.email, session_token=session_token)
            user.save()
            json_response = JsonResponse(body=user)
            json_response.set_cookie(settings.SESSION_COOKIE_NAME, session_token)
            return json_response
        except MessageBasedException as ex:
            return NewJsonResponse(exception=ex)
        except ValidationError as v:
            r = MessageBasedException(exception=v)
            return r.get_json_response()
        except RequestException as r:
            return r.jsonResponse
        except Exception as e:
            return MessageBasedException(message_id=ErrorMessage.Type.INCORRECT_DATA).get_json_response()

    @staticmethod
    def logout(session_token=None):
        try:
            session_token = AuthService.get_cookie(session_token)
            user = User.objects.get(sessionToken=session_token)
            user.sessionToken = ''
            user.save()
            json_response = JsonResponse(message_id=OkMessage.Type.SUCCESS_LOGOUT)
            json_response.set_cookie(SESSION_COOKIE_NAME, '')
            return json_response
        except Exception:
            return JsonResponse(message_id=OkMessage.Type.SUCCESS_LOGOUT)

    @staticmethod
    def confirm_email(session_token=None):
        try:
            user = User.objects.get(sessionToken=session_token)
            if user.confirmedEmail:
                return MessageBasedException(message_id=ErrorMessage.Type.ALREADY_CONFIRMED).get_json_response()
            else:
                user.confirmedEmail = True
                user.save()
                return JsonResponse(message_id=OkMessage.Type.ACCOUNT_VALIDATED)
        except RequestException as r:
            return r.jsonResponse
        except ObjectDoesNotExist or OverflowError or ValueError:
            return MessageBasedException(message_id=ErrorMessage.Type.INCORRECT_DATA).get_json_response()

    @staticmethod
    def recover_password(data=None):

        try:
            email_request = data['email']
            user = User.objects.get(email=email_request)
            if not user.confirmedEmail:
                return JsonResponse(message_id=ErrorMessage.Type.UNCONFIRMED_EMAIL)
            elif user.banned:
                return JsonResponse(message_id=ErrorMessage.Type.UNAUTHORIZED)
            else:
                password = RandomStringsService.random_password()
                EmailService.send_recover_password_email(user.email, password)
                user.password = password
                user.save()
                return JsonResponse(message_id=OkMessage.Type.RECOVER_PASS_EMAIL)
        except RequestException as r:
            return r.jsonResponse
        except Exception:
            return MessageBasedException(message_id=ErrorMessage.Type.INCORRECT_DATA).get_json_response()

    @staticmethod
    def is_authenticated(session_token):
        try:
            user = User.objects.get(sessionToken=session_token)
            if user.banned:
                return False
            else:
                return True
        except ObjectDoesNotExist:
            return False

    @staticmethod
    def is_authorized_author(session_token=None, author_id=None, level=False, same=True):
        """
        :param session_token: authentication token
        :param author_id: original author of the information.
        :param level: check the hierarchy. If the signed user has a lower value, exception is raised
        :param same: checks if the user that is trying to push changes is the same than the original.
        :return:
        """

        auth_user = User.objects.get(sessionToken=session_token)
        auth_user_rol = auth_user.rol
        original_user = User.objects.get(id=author_id)
        original_user_rol = original_user.rol
        if same and not author_id == auth_user.id:
            raise MessageBasedException(message_id=ErrorMessage.Type.UNAUTHORIZED)
        elif level and auth_user_rol.priority < original_user_rol.priority:
            raise MessageBasedException(message_id=ErrorMessage.Type.UNAUTHORIZED)
