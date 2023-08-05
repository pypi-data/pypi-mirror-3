from Products.Five import BrowserView
from Acquisition import aq_inner
import simplejson as json

from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage

class TransformView(BrowserView):

    def transform(self):
        request = self.request
        method = request.form.get('method')
        context = aq_inner(self.context)
        error = ''
        if not method is None:
            try:
                context.transformImage(method)
            except Exception, msg:
                error = msg
                
        if 'ajax' in request.form:
            request.response.setHeader('content-type', 'application/json; charset=utf-8')
            
            if error:
                response_body = {'success': False, 'error': {'title': _(u'Error'), 'msg': unicode(error)}}
            else:
                response_body = {'success': True}
                
            response_http = json.dumps(response_body)
            request.response.setHeader('content-length', len(response_http))
            return response_http
        else:
            target = context.absolute_url() + '/view'
            if error:
                IStatusMessage(request).addStatusMessage(error, type='error')
                
            request.response.redirect(target)
