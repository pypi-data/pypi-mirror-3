from datetime import datetime
from xml.dom.minidom import Element, parseString

from pypap.statuscodes import get_status
from pypap.utils import from_isoformat, get_dom_attribute, pap_isoformat


### Client Query Control Entities --------------------------------------

class PushMessage(object):
    """
    Represents a <push-message> control element entity.
    """

    def __init__(self, push_id):
        self.push_id = push_id
        self.addresses = []
        self.replace_push_id = None
        self.replace_method = "all"
        self.deliver_before = None
        self.deliver_after = None
        self.source_reference = None
        self.results_notification_to = None
        self.ppg_notify_requested_to = None
        self.request_progress_notes = False
        self.qos = {} # optional quality-of-service sub-element

    def add_addresses(self, *args):
        self.addresses.extend(args)

    def request_quality_of_service(self,
                                   priority="medium",
                                   delivery_method="notspecified",
                                   network=None,
                                   network_required=False,
                                   bearer=None,
                                   bearer_required=False):
        # Not sure I like this method
        self.qos['priority'] = priority
        self.qos['delivery-method'] = delivery_method

        if network:
            self.qos['network'] = network
        if network_required:
            self.qos['network-required'] = ("true" if network_required
                                            else "false")
        if bearer:
            self.qos['bearer'] = bearer
        if bearer_required:
            self.qos['bearer-required'] = ("true" if bearer_required
                                           else "false")

    @property
    def node(self):
        elem = Element("push-message")
        elem.setAttribute("push-id", self.push_id)

        if self.replace_push_id:
            elem.setAttribute("replace-push-id", self.replace_push_id)
            elem.setAttribute("replace-method", self.replace_method)

        if self.deliver_before:
            elem.setAttribute("deliver-before-timestamp",
                              pap_isoformat(self.deliver_before))

        if self.deliver_after:
            elem.setAttribute("deliver-after-timestamp",
                              pap_isoformat(self.deliver_after))

        if self.source_reference:
            elem.setAttribute("source-reference", self.source_reference)

        if self.results_notification_to:
            elem.setAttribute("results-notification-to",
                              self.results_notification_to)

        if self.ppg_notify_requested_to:
            elem.setAttribute("ppg-notifiy-requested-to",
                               self.ppg_notify_requested_to)

        request_progress = "true" if self.request_progress_notes else "false"
        if self.request_progress_notes:
            elem.setAttribute("request-progress-notes", request_progress)

        for address in self.addresses:
            addr_elem = Element("address")
            addr_elem.setAttribute("address-value", address)
            elem.appendChild(addr_elem)

        if self.qos:
            qos_elem = Element("quality-of-service")
            for k, v in self.qos.items():
                qos_elem.setAttribute(k, v)
            elem.appendChild(qos_elem)

        return elem

    def __str__(self):
        return "<PushMessage {0}>".format(self.push_id)


class CancelMessage(object):
    """
    Represents a <cancel-message> control element entity.
    """

    def __init__(self, push_id):
        self.push_id = push_id
        self.addresses = []

    def add_addresses(self, *args):
        self.addresses.extend(args)

    @property
    def node(self):
        elem = Element("cancel-message")
        elem.setAttribute("push-id", self.push_id)

        for address in self.addresses:
            addr_elem = Element("address")
            addr_elem.setAttribute("address-value", address)
            elem.appendChild(addr_elem)

        return elem

    def __str__(self):
        return "<CancelMessage {0}>".format(self.push_id)


class ResultNotificationResponse(object):
    """
    Represents a <resultnotification-response> control element entity.

    `code': Valid values are either 1000 or 2000.  See PAP
            specification for details or pypap.statuscodes
    """

    def __init__(self, push_id, code, description=None):
        self.push_id = push_id
        self.code = code
        self.description = description

    @property
    def node(self):
        elem = Element("resultnotification-response")
        elem.setAttribute("push-id", self.push_id)
        elem.setAttribute("code", self.code)

        if self.description:
            elem.setAttribute("desc", self.description)

        return elem

    def __str__(self):
        return "<ResultNotificationResponse {0}>".format(self.push_id)


class StatusQueryMessage(object):
    """
    Represents a <statusquery-message> control element entity.
    """

    def __init__(self, push_id):
        self.push_id = push_id
        self.addresses = []

    def add_addresses(self, *args):
        self.addresses.extend(args)

    @property
    def node(self):
        elem = Element("statusquery-message")
        elem.setAttribute("push-id", self.push_id)

        for address in self.addresses:
            addr_elem = Element("address")
            addr_elem.setAttribute("address-value", address)
            elem.appendChild(addr_elem)

        return elem

    def __str__(self):
        return "<StatusQueryMessage {0}>".format(self.push_id)


# Server Response Control Entities -------------------------------------

class PushResponse(object):

    def __init__(self, push_id,
                 sender_address=None,
                 sender_name=None,
                 reply_time=None):
        self.push_id = push_id
        self.sender_address = sender_address
        self.sender_name = sender_name
        self.reply_time = reply_time
        self.status = None
        self.progress_notes = []

    @classmethod
    def from_node(cls, node):
        """
        Return a PushResponse from a minidom Node object.
        """
        if node.tagName != "push-response":
            raise ValueError, "{0} is not a push-response node".format(
                node.tagName)
        if not node.attributes.get("push-id"):
            raise ValueError, "push-response missing push-id"

        try:
            response_result = node.getElementsByTagName("response-result")[0]
        except IndexError:
            raise ValueError, "push-response missing response-result"

        status = get_status(get_dom_attribute(response_result, "code"))
        sender_address = get_dom_attribute(node, "sender-address")
        sender_name = get_dom_attribute(node, "sender-name")
        reply_time = get_dom_attribute(node, "reply-time")
        reply_time = from_isoformat(reply_time) if reply_time else None

        r = cls(node.attributes['push-id'].value,
                sender_address=sender_address,
                sender_name=sender_name,
                reply_time=reply_time)
        r.status = status

        for note in node.getElementsByTagName("progress-note"):
            stage = get_dom_attribute(note, "stage")
            code = get_dom_attribute(note, "code")
            time = get_dom_attribute(note, "time")
            time = from_isoformat(time) if time else None
            r.progress_notes.append({'stage': stage,
                                     'code': code,
                                     'time': time})
        return r


class CancelResponse(object):

    def __init__(self, push_id):
        self.push_id = push_id
        self.status = None
        self.addresses = []

    @classmethod
    def from_node(cls, node):
        """ Return a CancelResponse object constructed from a minidom
        Node object.
        """
        if node.tagName != "cancel-response":
            raise ValueError, "{0} is not a <cancel-response> entity".format(
                node.tagName)
        if not node.attributes.get("push-id"):
            raise ValueError, "cancel-response missing push-id"

        try:
            cancel_result = node.getElementsByTagName("cancel-result")[0]
        except IndexError:
            raise ValueError, "cancel-response missing cancel-result"

        r = cls(node.attributes['push-id'].value)
        r.status = get_status(get_dom_attribute(cancel_result, "code"))

        for address in cancel_result.getElementsByTagName("address"):
            r.addresses.append(get_dom_attribute(address, "address-value"))

        return r


class ResultNotificationMessage(object):

    def __init__(self, push_id, state, code, address,
                 sender_address=None,
                 sender_name=None,
                 received_time=None,
                 event_time=None,
                 desc=None):
        self.push_id = push_id
        self.state = state
        self.status = get_status(code)
        self.address = address
        self.sender_address = sender_address
        self.sender_name = sender_name
        self.received_time = received_time
        self.event_time = event_time
        self.desc = desc

    @classmethod
    def from_node(cls, node):
        if not node.tagName == "resultnotification-message":
            raise ValueError, ("{0} is not a <resultnotification-message>"
                               "entity".format(node.tagName))
        if not node.attributes.get("push-id"):
            raise ValueError, "resultnotification-message missing push-id"
        if not node.attributes.get("message-state"):
            raise ValueError, ("resultnotification-message missing "
                               "message-state")
        if not node.attributes.get("code"):
            raise ValueError, "resultnotification-message missing code"

        try:
            address = node.getElementsByTagName("address")[0]
        except IndexError:
            raise ValueError, "missing address sub-element"

        if not address.attributes.get("address-value"):
            raise ValueError, "address sub-element missing value"

        sender_address = get_dom_attribute(node, "sender-address")
        sender_name = get_dom_attribute(node, "sender-name")
        received_time = get_dom_attribute(node, "received-time")
        received_time = (from_isoformat(received_time)
                         if received_time else None)
        event_time = get_dom_attribute(node, "event-time")
        event_time = from_isoformat(event_time) if event_time else None
        desc = get_dom_attribute(node, "desc")

        r = cls(node.attributes['push-id'].value,
                node.attributes['message-state'].value,
                node.attributes['code'].value,
                address.attributes['address-value'].value,
                sender_address=sender_address,
                sender_name=sender_name,
                received_time=received_time,
                event_time=event_time,
                desc=desc)

        return r


class StatusQueryResponse(object):

    def __init__(self, push_id):
        self.push_id = push_id
        self.results = []

    @classmethod
    def from_node(cls, node):
        if node.tagName != "statusquery-response":
            raise ValueError, ("{0} is not a <statusquery-response> "
                               "entity".format(node.tagName))
        if not node.attributes.get("push-id"):
            raise ValueError, "statusquery-response missing push-id"

        r = cls(node.attributes['push-id'].value)

        results = node.getElementsByTagName("statusquery-result")
        if not results:
            raise ValueError, ("statusquery-response missing "
                               "statusquery-result sub-elements")
        for result in results:
            if not result.attributes.get("message-state"):
                raise ValueError, "statusquery-result missing message-state"
            if not result.attributes.get("code"):
                raise ValueError, "statusquery-result missing code"
            addresses = result.getElementsByTagName("address")
            if not addresses:
                raise ValueError, "statusquery-result missing addresses"
            addresses = [get_dom_attribute(a, "address-value")
                         for a in addresses]
            event_time = get_dom_attribute(result, "event-time")
            event_time = from_isoformat(event_time) if event_time else None
            r.results.append(
                {'status': get_status(result.attributes['code'].value),
                 'addresses': addresses,
                 'message_state': result.attributes['message-state'].value,
                 'event_time': event_time})
        return r


class BadMessageResponse(object):

    def __init__(self, status,
                 message_fragment=None):
        self.status = status
        self.message_fragment = message_fragment

    @classmethod
    def from_node(cls, node):
        if node.tagName != "badmessage-response":
            raise ValueError, "{0} is not a badmessage-response entity".format(
                node.tagName)
        if not node.attributes.get("code"):
            raise ValueError, "badmessage-response is missing code"

        message_fragment = get_dom_attribute(node, "bad-message-fragment")

        r = cls(get_status(node.attributes['code'].value),
                message_fragment=message_fragment)

        return r
