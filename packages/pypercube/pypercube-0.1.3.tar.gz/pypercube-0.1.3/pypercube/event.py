import json
import types

from dateutil import parser as date_parser


class Event(object):
    """A Cube Event has a timestamp, a type, and a data dictionary."""

    TYPE_FIELD_NAME = "type"
    TIME_FIELD_NAME = "time"
    DATA_FIELD_NAME = "data"

    def __init__(self, type, time, data):
        """Create a Cube Event.

        :param type: The type of the event.
        :type type: str
        :param time: The timestamp of the event.
        :type time: str or datetime
        :param data: The data dictionary for the event.
        :type data: dict
        """
        self.type = type
        if isinstance(time, types.StringTypes):
            time = date_parser.parse(time, fuzzy=True)
        self.time = time
        self.data = data

    @classmethod
    def from_json(cls, json_obj):
        """Build an Event from JSON.

        :param json_obj: JSON data representing a Cube Event
        :type json_obj: `String` or `json`
        :throws: `InvalidEventError` when any of time field is not present
        in json_obj.
        """
        if isinstance(json_obj, str):
            json_obj = json.loads(json_obj)

        type = None
        time = None
        data = None
        if cls.TYPE_FIELD_NAME in json_obj:
            type = json_obj[cls.TYPE_FIELD_NAME]

        if cls.TIME_FIELD_NAME in json_obj:
            time = json_obj[cls.TIME_FIELD_NAME]
        else:
            raise InvalidEventError("{field} must be present!".format(
                field=cls.TIME_FIELD_NAME))

        if cls.DATA_FIELD_NAME in json_obj:
            data = json_obj[cls.DATA_FIELD_NAME]

        return cls(type, time, data)

    def to_json(self):
        d = dict()
        d[self.TYPE_FIELD_NAME] = self.type
        d[self.TIME_FIELD_NAME] = self.time.isoformat()
        d[self.DATA_FIELD_NAME] = self.data
        return d

    def __repr__(self):
        return "<Event: {value}>".format(value=self)

    def __str__(self):
        return json.dumps(self.to_json())

    def __eq__(self, other):
        return self.type == other.type and \
                self.time == other.time and \
                len(self.data) == len(other.data) and \
                self.data == other.data


class InvalidEventError(Exception):
    pass
