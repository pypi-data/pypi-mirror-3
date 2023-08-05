ADMINS = (
    ("loci", "opensource@jensnistler.de"),
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = "yourSecretKey"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "social_auth.backends.facebook.FacebookBackend",
    "social_auth.backends.twitter.TwitterBackend",
    "social_auth.backends.contrib.github.GithubBackend",
)

SOCIAL_AUTH_ENABLED_BACKENDS = ("facebook", "twitter", "github",)

TWITTER_CONSUMER_KEY = "LeEZ6EmnhUDHCPJgCKnJ5A"
TWITTER_CONSUMER_SECRET = "kpel23moe6wCa8N4WpIgJvDkC4jKXhfZKUmfQYvs71A"

GITHUB_APP_ID = "e46d7c062b3158259cd1"
GITHUB_API_SECRET = "3a8b5f1e09cb0878999fa248bfe3e6a7c4a73539"

FACEBOOK_APP_ID = "299877236703542"
FACEBOOK_API_SECRET = "9a581e96f686f4ca5b57b378b90d395d"


