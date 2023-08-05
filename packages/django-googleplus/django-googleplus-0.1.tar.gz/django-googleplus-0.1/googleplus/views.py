from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.models import SiteProfileNotAvailable
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import datetime
import json
import urllib
import urlparse

from googleplus import utils
from googleplus.models import GooglePlusUser
from googleplus.utils import get_registration_backend

GOOGLEPLUS_LOGIN_URL = '/googleplus/login/'
REDIRECT_URI = urlparse.urljoin( 
        #     'http://' + Sit.objects.get_current().domain, GOOGLEPLUS_LOGIN_URL
        'http://localhost:8000', GOOGLEPLUS_LOGIN_URL
)

def login_handler(request, backend=None):
    """
    Google+ OAuth2 login handler.
    """

    if request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    
    if 'error' in request.GET:
        messages.add_message(request, messages.ERROR, 
                             request.GET['error'])
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    elif 'code' in request.GET:
        params = { \
            'client_id': settings.GOOGLEPLUS_CLIENT_ID, \
            'redirect_uri': REDIRECT_URI, \
            'client_secret': settings.GOOGLEPLUS_CLIENT_SECRET, \
            'code': request.GET['code'], \
            'grant_type': 'authorization_code', \
        }
        req = urllib.urlopen('https://accounts.google.com/o/oauth2/token',
            urllib.urlencode(params)
        )
        if req.getcode() != 200:
            response = render_to_response('500.html', {}, \
                               context_instance=RequestContext(request))
            response.status_code = 500
            return response
        
        response = req.read()
        response_query_dict = json.loads(response)
        access_token = response_query_dict['access_token']
        expires_in = response_query_dict['expires_in']

        #
        #p #= #{#'#c#l#i#e#n#t#_#i#d#'#: #s#e#t#t#i#n#g#s#.#G#O#O#G#L#E#P#L#U#S#_#C#L#I#E#N#T#_#I#D#,
                #'#c#l#i#e#n#t#_#s#e#c#r#e#t#'#: #s#e#t#t#i#n#g#s#.#G#O#O#G#L#E#P#L#U#S#_#C#L#I#E#N#T#_#S#E#C#R#E#T#,
                #'#a#c#c#e#s#s#_#t#o#k#e#n#'#: #a#c#c#e#s#s#_#t#o#k#e#n#,
                #'#s#c#o#p#e#'#: #'#h#t#t#p#s#:#/#/#w#w#w#.#g#o#o#g#l#e#a#p#i#s#.#c#o#m#/#a#u#t#h#/#u#s#e#r#i#n#f#o#.#e#m#a#i#l#' #}
        #r#e#s #= #u#r#l#l#i#b#.#u#r#l#o#p#e#n#(#'#h#t#t#p#s#:#/#/#w#w#w#.#g#o#o#g#l#e#a#p#i#s#.#c#o#m#/#u#s#e#r#i#n#f#o#/#e#m#a#i#l#'#,
                #u#r#l#l#i#b#.#u#r#l#e#n#c#o#d#e#(#p#a#r#a#m#s#)#)
        #
        
        profile = utils.api('people/me', {'access_token': access_token})
        
        googleplus_user = _create_or_update_googleplus_user(request, profile, access_token, expires_in, backend)
        
        user = authenticate(googleplus_user=googleplus_user)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session.set_expiry(googleplus_user.expiry_at)
                if 'next' in request.GET:
                    return HttpResponseRedirect(request.GET['next'])
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.add_message(request, messages.ERROR, "Account disabled.")
        else:
            messages.add_message(request, messages.ERROR, "Login failed.")
    else:
        params = { \
            'client_id': settings.GOOGLEPLUS_CLIENT_ID, \
            'redirect_uri': REDIRECT_URI, \
            'scope': 'https://www.googleapis.com/auth/plus.me', \
            'response_type': 'code', \
        }    
        return HttpResponseRedirect('https://accounts.google.com/o/oauth2/auth?' +
            urllib.urlencode(params)
        )

def _create_or_update_googleplus_user(request, profile, access_token, expires_in, backend):
    """Creates or updates a Google+ user profile in local database.
    """
    user_is_created = False

    # Get the profile model. This can either be a user defined model
    # through AUTH_PROFILE_MODULE or the default GooglePlusUser
    if not hasattr(settings, 'AUTH_PROFILE_MODULE'):
        profile_model = GooglePlusUser
    else:
        profile_module = getattr(settings, 'AUTH_PROFILE_MODULE');
        try:
            app_label, model_name = profile_module.split('.')
        except ValueError:
            raise SiteProfileNotAvailable('sdf')

        try:
            profile_model = models.get_model(app_label, model_name)
        except ImportErorr:
            raise SiteProfileNotAvailable('sdf')



    try:
        googleplus_user = profile_model.objects.get(googleplus_id=profile['id'])
    except GooglePlusUser.DoesNotExist:
        import string
        from random import choice
        size = 9
        password = ''.join([choice(string.letters + string.digits) for i in range(size)]).lower()

        data = { 'username': profile['id'],
                 'password1': password,
                 'password2': password }

        # Get the first and last name from google
        first_name, last_name = _get_first_and_last_name(profile['displayName'])

        # Setup the backend
        backend = get_registration_backend(backend)
        form_class = backend.get_form_class(request)

        form = form_class(data=data, files=request.FILES)

        import pdb
        pdb.set_trace()
        if form.is_valid():
            user = backend.register(request, **form.cleaned_data)
        else:
            raise ValidationError('Something went wrong')

        #u#s#e#r #= #U#s#e#r#.#o#b#j#e#c#t#s#.#c#r#e#a#t#e#( #\
            #f#i#r#s#t#_#n#a#m#e#=#f#i#r#s#t#_#n#a#m#e#,
            #l#a#s#t#_#n#a#m#e#=#l#a#s#t#_#n#a#m#e#,
            #u#s#e#r#n#a#m#e#=#'#g#o#o#g#l#e#p#l#u#s#_#' #+ #p#r#o#f#i#l#e#[#'#i#d#'#]
        #)
        user_is_created = True
        
    if user_is_created:
        googleplus_user = profile_model()
        googleplus_user.googleplus_id = profile['id']
        googleplus_user.user = user
    else:
        first_name, last_name = _get_first_and_last_name(profile['displayName'])
        googleplus_user.user.first_name = first_name
        googleplus_user.last_name = last_name
        
    googleplus_user.googleplus_display_name = profile['displayName']
    googleplus_user.access_token = access_token
    googleplus_user.expiry_at = datetime.datetime.now() + \
        datetime.timedelta(seconds=int(expires_in))    
    googleplus_user.save()
    
    return googleplus_user

def _get_first_and_last_name(display_name):
    try:
        first_name, last_name = display_name.strip().rsplit(' ', 1)
    except ValueError:
        first_name = display_name
        last_name = ''
    return first_name, last_name
