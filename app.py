from datetime import datetime, timedelta
from typing import Union, Literal

from flask import Flask
from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment

app = Flask(__name__)

AVG_DAYS_IN_A_YEAR = 365.2425


class Event(object):
    def __init__(self, event_id, start):
        self.id = event_id
        self.start = start


class Contact(object):
    def __init__(self, contact_id, date_of_birth_as_string):
        self.id = contact_id
        self.date_of_birth_as_string = date_of_birth_as_string


class Learner(object):
    def __init__(self, learner_id, contact, event):
        self.id = learner_id
        self.contact = contact
        self.event = event


class Registration(object):
    def __init__(self, learners):
        self.learners = learners


def ensure_date(value: Union[str, datetime]):
    if isinstance(value, datetime):
        return value
    return datetime.strptime(value, "%Y-%m-%d")


def date_diff(value_1, value_2):
    return ensure_date(value_1) - ensure_date(value_2)


def timedelta_to_unit(value: timedelta, unit: Union[Literal['days'], Literal['years']]) -> float:
    if unit == 'days':
        return value.days
    if unit == 'years':
        # python-dateutil provides more accurate count (leap years etc), this will do for now
        return value.days / AVG_DAYS_IN_A_YEAR
    raise NotImplementedError(f"Unit '${unit}' unsupported for timedelta filter")


def render(**kwargs):
    with open('template.html', 'r') as f:
        contents = f.read()
    environment = SandboxedEnvironment(undefined=StrictUndefined)
    environment.filters.update({
        "date_diff": date_diff,
        "timedelta": timedelta_to_unit
    })
    return environment.from_string(contents).render(**kwargs)


@app.route("/")
def hello_world():
    learner_contact = Contact("contact1", "1987-12-31")
    event_1 = Event("event1", datetime(2020, 12, 31, 18, 30))
    registration = Registration([
        Learner("learner1", Contact("contact2", "2010-12-31"), event_1),
        Learner("learner2", learner_contact, event_1),
        Learner("learner3", learner_contact, Event("event2", datetime(2000, 12, 31, 17))),
        Learner("learner4", learner_contact, Event("event3", datetime(2005, 12, 30, 6))),
    ])
    return render(learner_contact=learner_contact, registration=registration)
