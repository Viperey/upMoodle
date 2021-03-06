from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer

from upmoodle.models import ErrorMessage


class ResponseFactory:

    def __init__(self):
        self.response = dict()
        self.obj = None
        self.flatten_obj = None
        self._identity = False
        self._media_type = 'application/json'
        self.http_code = 200
        self._cookies = {}
        self.http_response = HttpResponse()

    def ok(self, message_id=None):
        if message_id:
            message = message_id.get()
            self.response.__setitem__('message', message.json)
            self.http_code = message.http_code
        return self

    def error(self, message_id=ErrorMessage.Type.INCORRECT_DATA, **kwargs):
        message = message_id.get()
        self.response.__setitem__('error', message.json)
        self.http_code = message.http_code
        if 'exception' in kwargs:
            exception = kwargs.get('exception', None)
            if hasattr(exception, 'stack_trace'):
                stack_trace = exception.stack_trace
            else:
                stack_trace = self.__get_stack_trace(kwargs.get('exception'))
            self.response.get('error')['text'] += stack_trace
        elif 'stack_trace' in kwargs:
            self.response.get('error')['text'] += kwargs.get('stack_trace')

        return self

    def body(self, obj=None, flatten=None):
        if flatten:
            self.flatten_obj = flatten
        elif obj is not None:
            self.obj = obj
        return self

    def identity(self, obj=None):
        self.obj = obj.id
        self._identity = True
        return self

    def media_type(self, media_type='application/json'):
        self._media_type = media_type
        return self

    def cookies(self, cookies=None):
        self._cookies = cookies
        return self

    def build(self):
        switcher = {
            'application/json': self.get_json_response,
            'application/octet-stream': self.get_octet_stream_response
        }
        return switcher.get(self._media_type)()

    def get_json_response(self):
        self.response.__setitem__('data', self.get_flatten_object())
        response_json = JSONRenderer().render(self.response)
        self.http_response = self._ensure_headers(HttpResponse(response_json, content_type=self._media_type, status=self.http_code))
        self.set_cookies()
        return self.http_response

    def get_octet_stream_response(self):
        http_response = HttpResponse(self.obj.file)
        http_response['Content-Disposition'] = 'attachment; filename=' + self.obj.filename
        return http_response

    def set_cookies(self):
        if self._cookies:
            for key, value in self._cookies.iteritems():
                self.http_response.set_cookie(key=key, value=value)

    def _ensure_headers(self, http_response):
        http_response['Content-Type'] = self._media_type
        http_response['Access-Control-Expose-Headers'] = '*'
        http_response['Access-Control-Allow-Credentials'] = 'true'
        return http_response

    def get_flatten_object(self):
        if self.flatten_obj:
            pass
        else:
            if self.obj is not None and not self._identity:
                try:
                    self.flatten_obj = type(self.obj).get_flatten_object(self.obj, collection=False)
                except Exception:
                    self.flatten_obj = self.obj.model.get_flatten_object(self.obj, collection=True)
            elif self.obj and self._identity:
                self.flatten_obj = dict()
                self.flatten_obj.__setitem__('id', self.obj)
        return self.flatten_obj

    def __get_stack_trace(self, exception):
        if len(exception.message):
            return exception.message
        elif hasattr(exception, 'messages') and len(exception.messages):
            return '\n. '.join(exception.messages)
        else:
            return ''

