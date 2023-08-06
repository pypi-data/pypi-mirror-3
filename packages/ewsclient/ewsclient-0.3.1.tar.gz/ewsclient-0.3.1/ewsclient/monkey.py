"""
Monkeypatch suds to provide local copy of www.w3.org/2001/xml.xsd;
www.w3.org's overloaded server will often fail to return the document.

Also apply fix from suds ticket #292, necessary to work with Exchange .wsdl
"""

def bind_xml_xsd():
    import pkg_resources
    import os.path
    from suds.xsd.sxbasic import Import

    xml_xsd_url = 'file://%s' % os.path.abspath(pkg_resources.resource_filename('ewsclient', 'xml.xsd'))
    Import.bind('http://www.w3.org/XML/1998/namespace', xml_xsd_url)

bind_xml_xsd()

def patch_292():
    from functools import wraps
    from suds.xsd.sxbase import SchemaObject
    
    unpatched_namespace = SchemaObject.namespace
    @wraps(SchemaObject.namespace)
    def patched_namespace(self, prefix=None):
        """From suds ticket #292"""
        if self.ref is not None:
            return (prefix, self.ref[1])
        return unpatched_namespace(self, prefix)
    SchemaObject.namespace = patched_namespace

patch_292()
