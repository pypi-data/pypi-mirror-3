from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.conf import settings

def get_template(request, template_name):
    if settings.DISABLE_MOBILITY_HELPERS:
        return template_name

    if not hasattr(request, 'is_mobile'):
        return template_name

    base, extension = template_name.rsplit('.')
    if settings.DETECT_MOBILE_FLAVOUR and request.mobile_flavour:
        template_name = "%s.%s.%s" % (base, request.mobile_flavour, extension)
    else:
        template_name = "%s.mobile.%s" % (base, extension)

    return template_name


def smart_response(request, template, data):
    return render_to_response(get_template(request, template), data, context_instance=RequestContext(request))
