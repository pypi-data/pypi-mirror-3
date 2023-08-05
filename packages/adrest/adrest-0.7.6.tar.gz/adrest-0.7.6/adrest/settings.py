" Adrest API settings. "
from django.conf import settings


# Enable Adrest API logs
ACCESS_LOG = getattr(settings, 'ADREST_ACCESS_LOG', False)

# Auto create adrest access-key for created user
AUTO_CREATE_ACCESSKEY = getattr(settings, 'ADREST_AUTO_CREATE_ACCESSKEY', False)

# Max resources per page in list views
LIMIT_PER_PAGE = int(getattr(settings, 'ADREST_LIMIT_PER_PAGE', 50))

# Display django standart technical 500 page
DEBUG = getattr(settings, 'ADREST_DEBUG', False)

# Limit request number per second from same identifier, null is not limited
THROTTLE_AT = getattr(settings, 'ADREST_THROTTLE_AT', 120)
THROTTLE_TIMEFRAME = getattr(settings, 'ADREST_THROTTLE_TIMEFRAME', 60)

# We do not restrict access for OPTIONS request.
AUTHENTICATE_OPTIONS_REQUEST = getattr(settings, 'ADREST_AUTHENTICATE_OPTIONS_REQUEST', False)
