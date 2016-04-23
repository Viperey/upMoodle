from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt

from backend.settings import SESSION_COOKIE_NAME
from rest.JSONResponse import JSONResponse, JSONResponseID
from rest.MESSAGES_ID import INCORRECT_DATA, FILE_REMOVED, FILE_UPLOADED, FILE_UPDATED
from rest.controllers.Exceptions.requestException import RequestException, RequestExceptionByCode, \
    RequestExceptionByMessage
from rest.controllers.controllers import check_signed_in_request, check_authorized_author
from rest.models import File, Level, User
from rest.orm.serializers import FileSerializer
from rest.orm.unserializer import unserialize_file_binary, unserialize_file


def file_metadata_get(request, pk):
    try:
        check_signed_in_request(request, 'GET')
        files = File.objects.filter(hash=pk, visible=True)
        serializer = FileSerializer(files, many=True)
        return JSONResponse(serializer.data)
    except RequestException as r:
        return r.jsonResponse
    except ObjectDoesNotExist or OverflowError or ValueError:
        return RequestExceptionByCode(INCORRECT_DATA).jsonResponse


def file_get_binary(request, file_hash):
    try:
        check_signed_in_request(request, 'GET')
        response_file = File.objects.get(hash=file_hash)

        response = HttpResponse(response_file.file)
        response['Content-Disposition'] = 'attachment; filename=' + response_file.filename
        return response
    except RequestException as r:
        return r.jsonResponse
    except ObjectDoesNotExist or OverflowError or ValueError:
        return RequestExceptionByCode(INCORRECT_DATA).jsonResponse


@csrf_exempt
def file_metadata_update(request, file_hash):
    try:
        file_original = File.objects.get(hash=file_hash)

        check_signed_in_request(request, method='POST')
        check_authorized_author(request, file_original.uploader_id, level=True, same=False)

        form = request.POST
        fields = ['name', 'text', 'fileType_id']
        file_updated = unserialize_file(form, fields=fields, optional=True)

        file_original.update(file_updated, fields)
        file_original.lastUpdater_id = User.get_signed_user_id(request.COOKIES[SESSION_COOKIE_NAME])
        file_original.save()

        return JSONResponseID(FILE_UPDATED)
    except RequestException as r:
        return r.jsonResponse
    except ObjectDoesNotExist or OverflowError or ValueError or MultiValueDictKeyError:
        return RequestExceptionByCode(INCORRECT_DATA).jsonResponse
    except ValidationError as v:
        return RequestExceptionByMessage(v).jsonResponse


@csrf_exempt
def file_delete(request, pk):
    try:
        check_signed_in_request(request, method='DELETE')
        model = File.objects.get(id=pk)
        check_authorized_author(request, model.uploader_id, level=True, same=False)
        model.visible = False
        model.save()
        return JSONResponseID(FILE_REMOVED)
    except RequestException as r:
        return r.jsonResponse
    except ObjectDoesNotExist:
        return RequestExceptionByCode(INCORRECT_DATA).jsonResponse


@csrf_exempt
def file_post(request):
    try:

        uploader = int(request.POST['uploader_id'])
        check_signed_in_request(request, method='POST')
        check_authorized_author(request, uploader, level=True)

        form = request.POST
        Level.validate_exists_level(form['subject_id'])

        fields = ['uploader_id', 'subject_id', 'name', 'text', 'fileType_id']
        new_file = unserialize_file_binary(form, fields=fields, optional=True, binary=request.FILES['file'])
        new_file.save()
        return JSONResponseID(FILE_UPLOADED)
    except Exception as e:
        return RequestExceptionByCode(INCORRECT_DATA).jsonResponse
