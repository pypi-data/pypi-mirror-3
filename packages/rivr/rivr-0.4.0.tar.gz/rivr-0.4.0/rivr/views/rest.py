from rivr.http import Response

class RESTMixin(object):
    pass

class RESTView(View, RESTMixin):
    def dispatch(self, request, *args, **kwargs):
        response = super(RESTView, self).dispatch(request, *args, **kwargs)

        if isinstance(response, Response):
            return Response

        accepts = request.HEADERS.get('Accepts')

