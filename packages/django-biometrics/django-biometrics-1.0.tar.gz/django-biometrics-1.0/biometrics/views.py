from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

import json

@csrf_exempt
def handle(request, user):
    user = User.objects.get(pk=user)
    if request.method == "POST":
        try:
            user.fingerprint_templates.create(data=request.raw_post_data)
        except IntegrityError, arg:
            return HttpResponse(arg.args[0], status=409)

        return HttpResponse("Template added", status=201)
    elif request.method == "GET":
        return HttpResponse(
            json.dumps([ft.serialized_data for ft in user.fingerprint_templates.all()])
        )