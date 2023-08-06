# -*- coding: utf-8 -*-
import sys
from tg import config
import forms

def get_form():
    registration_form = config.get('_calendarevents.form_instance')
    if not registration_form:
        form_path = config.get('_calendarevents.form', 'calendarevents.lib.forms.NewEventForm')
        root_module, path = form_path.split('.', 1)
        form_class = reduce(getattr, path.split('.'), sys.modules[root_module])
        registration_form = config['_calendarevents.form_instance'] = form_class()
    return registration_form
