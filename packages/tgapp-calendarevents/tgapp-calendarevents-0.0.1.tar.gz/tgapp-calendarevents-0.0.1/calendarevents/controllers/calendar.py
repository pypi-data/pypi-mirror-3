from tg import TGController
from tg import expose, flash, require, url, lurl, request, redirect, validate, config
from tg.i18n import ugettext as _, lazy_ugettext as l_

from calendarevents import model
from calendarevents.model import DBSession

from tgext.pluggable import plug_redirect
from tgext.datahelpers.validators import SQLAEntityConverter
from tgext.datahelpers.utils import fail_with, object_primary_key

from calendarevents.lib import get_form
from calendarevents.model.models import CalendarEvent
from repoze.what import predicates
import json

class CalendarController(TGController):
    @expose('calendarevents.templates.calendar.calendar')
    @validate(dict(cal=SQLAEntityConverter(model.Calendar)),
            error_handler=fail_with(404))
    def _default(self, cal):
        events = [{'uid':e.uid, 'title':e.name, 'start':e.datetime.strftime('%Y-%m-%d %H:%M')} for e in cal.events]
        return dict(cal=cal, events=json.dumps(events))

    @expose('calendarevents.templates.calendar.list')
    @validate(dict(cal=SQLAEntityConverter(model.Calendar)),
              error_handler=fail_with(404))
    def list(self, cal):
        return dict(cal=cal)

    @require(predicates.in_group('calendarevents'))
    @expose('calendarevents.templates.calendar.newevent')
    @validate(dict(cal=SQLAEntityConverter(model.Calendar)),
              error_handler=fail_with(403))
    def newevent(self, cal, **kw):
        if isinstance(cal, basestring):
            cal = SQLAEntityConverter(model.Calendar).to_python(cal)

        event_type = cal.events_type_info
        if not event_type:
            linkable_entities = []
        else:
            linkable_entities = event_type.get_linkable_entities(cal)

        return dict(cal=cal, form=get_form(), linkable_entities=linkable_entities)

    @require(predicates.in_group('calendarevents'))
    @expose()
    @validate(get_form(), error_handler=newevent)
    def addevent(self, cal, **kw):
        new_event = model.CalendarEvent(calendar_id=cal.uid, name=kw['name'],
                                        summary=kw['summary'], datetime=kw['datetime'],
                                        location=kw['location'],
                                        linked_entity_type=cal.events_type,
                                        linked_entity_id=kw.get('linked_entity'))
        model.DBSession.add(new_event)
        flash(_('Event successfully added'))
        return plug_redirect('calendarevents', '/calendar/%s' % cal.uid)

    @require(predicates.in_group('calendarevents'))
    @expose()
    @validate(dict(event=SQLAEntityConverter(model.CalendarEvent)),
              error_handler=fail_with(404))
    def remove_event(self, event):
        DBSession.delete(event)
        return redirect(request.referer)
