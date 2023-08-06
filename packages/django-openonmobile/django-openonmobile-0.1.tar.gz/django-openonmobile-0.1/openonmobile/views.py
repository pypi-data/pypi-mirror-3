# Create your views here.

import qrcode
from django.http import HttpResponse

import utils


def qr(request):

    absolute_uri = utils.mobile_url(request)

    image = qrcode.make(absolute_uri)
    rotate = request.GET.get('rotate')
    if rotate:
        image = image._img.convert('RGBA').rotate(45, expand=1)
    response = HttpResponse(mimetype="image/png")
    image.save(response, "PNG")
    return response
