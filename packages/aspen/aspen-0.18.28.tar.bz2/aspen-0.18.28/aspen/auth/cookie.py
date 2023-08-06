from aspen import Response
from aspen import auth


def inbound(request):
    """Authenticate from a cookie.
    """
    if 'session' in request.headers.cookie:
        token = request.headers.cookie['session'].value
        user = auth.User.from_session_token(token)
    else:
        user = auth.User({})
    request.context['user'] = user


def outbound(response):
    session = {}
    if 'user' in response.request.context:
        user = response.request.context['user']
        if not isinstance(user, auth.User):
            raise Response(400, "If you define 'user' in a simplate it has to "
                                "be a User instance.")
        session = user.session
    if not session:                                 # user is anonymous
        if 'session' not in response.request.headers.cookie:
            # no cookie in the request, don't set one on response
            return
        else:
            # expired cookie in the request, instruct browser to delete it
            response.headers.cookie['session'] = '' 
            expires = 0
    else:                                           # user is authenticated
        response.headers['Expires'] = BEGINNING_OF_EPOCH # don't cache
        response.headers.cookie['session'] = session['session_token']
        expires = session['session_expires'] = time.time() + TIMEOUT
        SQL = """
            UPDATE participants SET session_expires=%s WHERE session_token=%s
        """
        db.execute( SQL
                  , ( datetime.datetime.fromtimestamp(expires)
                    , session['session_token']
                     )
                   )

    cookie = response.headers.cookie['session']
    # I am not setting domain, because it is supposed to default to what we 
    # want: the domain of the object requested.
    #cookie['domain']
    cookie['path'] = '/'
    cookie['expires'] = rfc822.formatdate(expires)
    cookie['httponly'] = "Yes, please."


