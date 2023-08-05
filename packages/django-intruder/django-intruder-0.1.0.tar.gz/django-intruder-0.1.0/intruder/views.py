# Create your views here.
from django.http import HttpResponse


def feature_under_maintenance(request):
    return HttpResponse(u'This feature is under maintenance', status=301)


def feature_is_no_longer_available(request):
    return HttpResponse(u'This feature is no longer available', status=301)
