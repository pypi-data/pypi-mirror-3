# RIM-specific extensions to PAP.

from xml.dom.minidom import Element, getDOMImplementation, parseString

from pypap.statuscodes import get_status
from pypap.utils import from_isoformat, get_dom_attribute


class BPDSMessage(object):

    PAP_VERSION = "2.1"
    BPDS_VERSION = "1.0"

    def __init__(self, entity):
        self.entity = entity

    def to_xml(self):
        impl = getDOMImplementation()
        dt = impl.createDocumentType(
            "pap",
            "-//WAPFORUM//DTD PAP {0}//EN".format(self.PAP_VERSION),
            ("http://www.openmobilealliance.org"
             "/tech/DTD/pap_{0}.dtd").format(self.PAP_VERSION))
        doc = impl.createDocument(None, "bpds", dt)
        root = doc.documentElement
        root.setAttribute("version", self.BPDS_VERSION)
        root.appendChild(self.entity.node)

        return doc.toxml()


# Entities -------------------------------------------------------------


class SubscriptionQueryMessage(object):
    """
    Represents a <subscriptionquery-message> control element entity.
    """

    def __init__(self, service_id, status):
        self.service_id = service_id
        self.status = status

    @property
    def node(self):
        elem = Element("subscriptionquery-message")
        elem.setAttribute("pushservice-id", self.service_id)

        status_elem = Element("status")
        status_elem.setAttribute("status-value", self.status)
        elem.appendChild(status_elem)

        return elem


class SubscriptionQueryResponse(object):

    def __init__(self, service_id):
        self.service_id = service_id
        self.results = []

    @classmethod
    def from_node(cls, node):
        if node.tagName != "subscriptionquery-response":
            raise ValueError, ("{0} is not a subscriptionquery-response "
                               "entity").format(node.tagName)
        result = node.firstChild
        if not (result and result.attributes.get("code")):
            raise ValueError, ("Response missing subscriptionquery-response "
                               "result")
        if not result.attributes['code'].value.startswith("21"):
            raise ValueError, ("Response returned an error: {0} {1}").format(
                result.attributes['code'].value,
                result.attributes['desc'].value)

        r = cls(node.attributes.get("pushservice-id").value)

        results = node.getElementsByTagName("subscriptionquery-detail")
        for result in results:
            if not result.attributes.get("status"):
                raise ValueError, ("subscriptionquery-detail missing status "
                                   "attribute")
            if not result.attributes.get("event-time"):
                raise ValueError, ("subscriptionquery-detail missing "
                                   "event-time attribute")
            address = result.firstChild
            if (address.tagName != "address" and
                not address.attributes.get("address-value")):
                raise ValueError, ("subscriptionquery-detail received "
                                   "malformed address element")
            r.results.append(dict(
                status=result.attributes['status'].value,
                event_time=from_isoformat(
                    result.attributes['event-time'].value),
                address=address.attributes['address-value'].value))

        return r

    @classmethod
    def from_raw_xml(cls, xml):
        dom = parseString(xml)
        root = dom.documentElement

        return cls.from_node(root.firstChild)
