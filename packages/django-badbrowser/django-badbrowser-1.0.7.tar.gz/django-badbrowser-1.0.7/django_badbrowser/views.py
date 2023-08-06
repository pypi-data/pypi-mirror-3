from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.conf import settings


def unsupported(request):
    
    context = {
        "next": request.path,
        "suggest": getattr(settings, "BADBROWSER_SUGGEST", ["firefox"]),
        "STATIC_URL": settings.STATIC_URL,
        "base_template": getattr(settings, "BADBROWSER_BASE_TEMPLATE", "django_badbrowser/base.html")
    }
    
    return render_to_response("django_badbrowser/unsupported.html", context)

def ignore(request):
    response = HttpResponseRedirect(request.GET.get("next", "") or "/")
    response.set_cookie("badbrowser_ignore", "1")
    return response
