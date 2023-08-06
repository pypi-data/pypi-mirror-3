from tw.api import WidgetsList
from tw.forms import TableForm, TextField, HiddenField, TextArea, SingleSelectField
from tw.forms import validators
from tw.forms.calendars import CalendarDateTimePicker
from tgext.datahelpers.validators import SQLAEntityConverter
from tg import config
from tg.i18n import lazy_ugettext as l_
from calendarevents import model

class NewEventForm(TableForm):
    class fields(WidgetsList):
        event = HiddenField()
        cal = HiddenField(validator=SQLAEntityConverter(model.Calendar))
        name = TextField(label_text=l_('Event Name'), validator=validators.UnicodeString(not_empty=True))
        summary = TextArea(label_text=l_('Event short summary'), validator=validators.UnicodeString(not_empty=False))
        datetime = CalendarDateTimePicker(label_text=l_('Event date'))
        location = TextField(label_text=l_('Event Location (es: turin,it)'),
                             validator=validators.UnicodeString(not_empty=True))
        linked_entity = SingleSelectField(label_text=l_('Linked Entity'))

class NewCalendarForm(TableForm):
    class fields(WidgetsList):
        name = TextField(label_text=l_("Calendar Name"), validator=validators.UnicodeString(not_empty=True))
        events_type = SingleSelectField(label_text=l_('Events Type'),
                                        options=lambda: [e.name for e in config['_calendarevents']['event_types']],
                                        validator=validators.UnicodeString(not_empty=False))
new_calendar_form = NewCalendarForm()
