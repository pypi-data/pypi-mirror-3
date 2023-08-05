from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from xml.dom.minidom import getDOMImplementation, parseString

from pypap.entities import (BadMessageResponse,
                            CancelResponse,
                            PushResponse,
                            ResultNotificationMessage,
                            StatusQueryResponse)


def encode(message):
    """
    Return a MIME/Multipart encoded string.

    `message': a PAPMessage instance
    """
    if not message.control_part:
        raise ValueError, "{0} missing control part".format(message)

    if not message.content_part:
        raise ValueError, "{0} missing content part".format(message)

    mime = MIMEMultipart("related")
    mime.attach(MIMEApplication(message.to_xml(), "xml"))
    mime.attach(message.content_part)

    return mime.as_string()


def decode(response):
    dom = parseString(response)
    root = dom.documentElement

    response_handlers = {
        'push-response': PushResponse,
        'cancel-response': CancelResponse,
        'resultnotification-message': ResultNotificationMessage,
        'statusquery-response': StatusQueryResponse,
        'badmessage-response': BadMessageResponse}

    handler = response_handlers.get(root.firstChild.tagName)
    return handler.from_node(root.firstChild)
