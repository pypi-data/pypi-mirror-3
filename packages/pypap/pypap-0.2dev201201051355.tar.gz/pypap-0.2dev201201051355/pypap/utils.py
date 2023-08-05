from datetime import datetime
from time import strptime


def from_isoformat(timestamp, sep="T"):
    """ Return a datetime object from an ISO formatted timestamp."""
    t = strptime(timestamp, "%Y-%m-%d{0}%H:%M:%SZ".format(sep))
    return datetime(t[0], t[1], t[2], t[3], t[4], t[5])


def pap_isoformat(dt):
    """ Return an isoformat string from a datetime object.  This
    isoformat string conforms with the PAP specification."""
    date = datetime(dt.year, dt.month, dt.day,
                    dt.hour, dt.minute, dt.second)
    return date.isoformat() + "Z"


def get_dom_attribute(node, name):
    """ Return the value of the attribute or None if it doesn't exist."""
    attr = node.attributes.get(name)
    return attr.value if attr else None
