from django.core import validators


class CustomURLValidator(validators.URLValidator):
    schemes = ["http", "https", "ftp", "ftps", "postgres"]
