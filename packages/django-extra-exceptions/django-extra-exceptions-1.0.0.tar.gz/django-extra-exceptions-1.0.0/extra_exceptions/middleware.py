from django.shortcuts import render
from django.core.exceptions import ViewDoesNotExist
from django.http import HttpResponse
from django.template import loader, TemplateDoesNotExist
from .utils import HttpException
import httplib

class HttpExceptionMiddleware(object):
    """
    Replace Status code raises for a {{status}}.html rendered template
    """
    def process_exception(self, request, exception):
        """
        Render a {{status}}.html template or default template as status page, but only if
        exception is instance of HttpException class
        """
        # we need to import to use isinstance
        if not isinstance(exception,HttpException):
            # Return None so that django will reraise the exception:
            # http://docs.djangoproject.com/en/dev/topics/http/middleware/#process_exception
            return None
        
        context = {
            'message': exception.message,
            'w3cname': httplib.responses.get(exception.status, str(exception.status))
        }
        
        try:
            template_name = str(exception.status) + '.html'
            loader.get_template(str(exception.status) + '.html')
        except TemplateDoesNotExist:
            template_name = ("extra_exceptions/default_error_page.html")

        # now use context and render template      

    
        return render(
            request,
            template_name,
            dictionary = {
                'message': exception.message,
                'w3cname': httplib.responses.get(exception.status, str(exception.status))
            },
            status=exception.status,
        )
