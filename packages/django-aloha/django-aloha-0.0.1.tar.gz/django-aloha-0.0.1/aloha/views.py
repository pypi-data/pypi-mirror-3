# coding: utf-8

from django.contrib.auth.decorators import login_required
from django.db.models import get_model
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.contrib import messages


@login_required
@require_POST
def save(request):
    """Save the field contents for the object"""

    def show_message(msg, level=messages.ERROR):
        messages.add_message(request, level, msg)
        return HttpResponseRedirect(request.POST.get('next', '/'))

    # TODO: check permissions better
    if not request.user.is_staff:
        return HttpResponseForbidden()
    try:
        app_label, model_name = request.POST['object_name'].split('.')
    except ValueError, e:
        return show_message(_('Cannot find the model'))

    model = get_model(app_label, model_name)
    if not model:
        return show_message(_('Cannot find the model'))

    field_name = request.POST.get('field_name')
    if (field_name and hasattr(model, field_name)):
        return show_message(_('No field_name parameter'))

    try:
        contents = request.POST['content']
    except KeyError:
        return show_message(_('No contents parameter provided'))

    try:
        obj = model.objects.get(pk=request.POST['object_pk'])
    except KeyError:
        return show_message(_('object_pk not provided'))
    except model.DoesNotExist:
        return show_message(_('Cannot find the object with this primary key'))

    setattr(obj, field_name, contents)
    obj.save()

    return show_message(_('Object saved'), messages.SUCCESS)
