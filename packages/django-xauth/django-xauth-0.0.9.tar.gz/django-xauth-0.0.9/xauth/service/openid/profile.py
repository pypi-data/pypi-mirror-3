from openid.extensions import ax, sreg

# http://openid.net/specs/openid-simple-registration-extension-1_0.html
SREG_MAPPING = {
    'nickname': 'openid.sreg.nickname',
    'email': 'openid.sreg.email',
    'fullname': 'openid.sreg.fullname',
    'dob': 'openid.sreg.dob', # YYYY-MM-DD
    'sex': 'openid.sreg.gender', # (M|F)
    'postcode': 'openid.sreg.postcode',
    'country': 'openid.sreg.country', # (ISO3166)',
    'language': 'openid.sreg.language', # (ISO639
    'timezone': 'openid.sreg.timezone', # (http://www.twinsun.com/tz/tz-link.htm):
}

# http://webcache.googleusercontent.com/search?q=cache:3JZitb3SjnsJ:www.axschema.org/types/+openid+ax&cd=5&hl=en&ct=clnk&gl=ru&source=www.google.ru
AX_MAPPING = {
    'nickname': 'http://axschema.org/namePerson/friendly',
    'email': 'http://axschema.org/contact/email',
    'fullname': 'http://axschema.org/namePerson',
    'dob': 'http://axschema.org/birthDate',
    'sex': 'http://axschema.org/person/gender',
    'postcode': 'http://axschema.org/contact/postalCode/home',
    'country': 'http://axschema.org/contact/country/home',
    'language': 'http://axschema.org/pref/language',
    'timezone': 'http://axschema.org/pref/timezone',
}


def add_profile_query(auth_request, fields):
    """
    Update authentication request with Sreg/AX details.

    # Add Simple Registration request information.  Some fields
    # are optional, some are required.  It's possible that the
    # server doesn't support sreg or won't return any of the
    # fields.
    """
    sreg_request = sreg.SRegRequest(optional=[SREG_MAPPING[x].rsplit('.', 1)[1] for x in fields])
    auth_request.addExtension(sreg_request)

    # Add Attribute Exchange request information.
    ax_request = ax.FetchRequest()
    for field in fields:
        ax_request.add(ax.AttrInfo(AX_MAPPING[field], required=True))
    auth_request.addExtension(ax_request)


def process_profile_data(response, fields):
    """
    Get a Simple Registration response object if response
    information was included in the OpenID response.
    """
    
    profile = {}
    sreg_response = sreg.SRegResponse.fromSuccessResponse(response)
    if sreg_response:
        for field in fields:
            if field in sreg_response:
                profile[field] = sreg_response.get(SREG_MAPPING[field].rsplit('.', 1)[1])

    ax_response = ax.FetchResponse.fromSuccessResponse(response)
    if ax_response:
        for field in fields:
            try:
                value = ax_response.get(AX_MAPPING[field])[0]
            except (KeyError, IndexError):
                pass
            else:
                if value:
                    profile[field] = value
    return profile
