from django.template import RequestContext
from django.shortcuts import render_to_response


from dashboard_app.models import Bundle
from collections import namedtuple


pair = namedtuple("pair", "x y")


def hello(request):
    import random
    return render_to_response(
        "demo_app/hello.html", {
            "data_list": [pair(i, random.random()) for i in range(100)]
        },
        RequestContext(request))
