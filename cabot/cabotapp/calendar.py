from django.conf import settings
from django.db import models
from icalendar import Calendar
import requests


class Schedule(models.Model):
    name = models.TextField(default='Main')
    feed_url = models.TextField(default=settings.CALENDAR_ICAL_URL)

    def get_calendar_data(self):
        resp = requests.get(self.feed_url)
        return Calendar.from_ical(resp.content)


def get_events(schedule):
    events = []
    for component in schedule.get_calendar_data().walk():
        if component.name == 'VEVENT':
            events.append({
                'start': component.decoded('dtstart'),
                'end': component.decoded('dtend'),
                'summary': component.decoded('summary'),
                'uid': component.decoded('uid'),
                'attendee': component.decoded('attendee'),
            })
    return events
