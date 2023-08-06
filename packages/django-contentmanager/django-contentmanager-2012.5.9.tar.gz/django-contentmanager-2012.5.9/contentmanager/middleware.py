class EditmodeMiddleware(object):
    """
    Change editmode in session.
    """
    def process_request(self, request):
        if 'editmode' in request.GET:
            # Don't update session if no change has been made.
            current = request.session.get('contentmanager_editmode', False)
            if request.GET['editmode'] == '1' and not current \
               and request.user.is_authenticated():
                request.session['contentmanager_editmode'] = True
            elif request.GET['editmode'] == '0' and current:
                request.session['contentmanager_editmode'] = False
        elif not request.user.is_authenticated():
            request.session['contentmanager_editmode'] = False
