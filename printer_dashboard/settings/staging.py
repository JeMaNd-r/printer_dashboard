from .base import *  # noqa

SECRET_KEY = env.str("DJANGO_SECRET_KEY")
DEBUG = False

FRONTEND_URL = "http://localhost:5173"  # TODO: Update this to your frontend URL in stagings

ALLOWED_HOSTS = [".v2.singular-it-test.de"]

CSRF_TRUSTED_ORIGINS = ["https://*.v2.singular-it-test.de"]


# CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.v2\.singular-it-test\.de$",
]


# SECURITY

# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = True

# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_NAME = "bifsofmNfWxDETCkhULF"

# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_NAME = "EKoEInTMtwPGYweqYPpv"

# https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7  # 1 week

# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = True

# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = True
