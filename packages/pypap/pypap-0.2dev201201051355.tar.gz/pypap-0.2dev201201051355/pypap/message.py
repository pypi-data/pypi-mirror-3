from xml.dom.minidom import getDOMImplementation


class PAPMessage(object):

    VERSION = "2.1"

    def __init__(self,
                 product_name=None,
                 control_part=None,
                 content_part=None):
        self.product_name = product_name
        self.control_part = control_part
        self.content_part = content_part

    def to_xml(self):
        impl = getDOMImplementation()
        dt = impl.createDocumentType(
            "pap",
            "-//WAPFORUM//DTD PAP {0}//EN".format(self.VERSION),
            ("http://www.openmobilealliance.org"
             "/tech/DTD/pap_{0}.dtd").format(self.VERSION))
        doc = impl.createDocument(None, "pap", dt)
        root = doc.documentElement
        if self.product_name:
            root.setAttribute("product-name", self.product_name)
        root.appendChild(self.control_part.node)

        return doc.toxml()
