import suds.client
import suds.plugin
import suds.store
import urlparse

class EWSClient(suds.client.Client):
    pass

class AddService(suds.plugin.DocumentPlugin):
    # WARNING: suds hides exceptions in plugins
    def loaded(self, ctx):
        """Add missing service."""
        urlprefix = urlparse.urlparse(ctx.url)
        service_url = urlparse.urlunparse(urlprefix[:2] + ('/EWS/Exchange.asmx', '', '', ''))
        servicexml = u'''  <wsdl:service name="ExchangeServices">
    <wsdl:port name="ExchangeServicePort" binding="tns:ExchangeServiceBinding">
      <soap:address location="%s"/>
    </wsdl:port>
  </wsdl:service>
</wsdl:definitions>''' % service_url
        ctx.document = ctx.document.replace('</wsdl:definitions>', servicexml.encode('utf-8'))
        return ctx
