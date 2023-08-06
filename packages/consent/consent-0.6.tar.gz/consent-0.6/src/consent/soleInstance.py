import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'consent.django.settings.main'

import consent.application

application = consent.application.Application()

