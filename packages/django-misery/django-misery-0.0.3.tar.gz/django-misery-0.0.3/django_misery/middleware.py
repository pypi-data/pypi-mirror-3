import logging
from random import randint
from time import sleep
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout
from django.shortcuts import render_to_response

from django.db import models
from models import MiseryIP

from django.conf import settings

logger = logging.getLogger('django_misery')

slowBanStrength = int(getattr(settings, 'MISERY_SLOW_STRENGTH', 6))
logoutProbability = int(getattr(settings, 'MISERY_LOGOUT_PROBABILITY', 10))
e403Probability = int(getattr(settings, 'MISERY_403_PROBABILITY', 10))
e404Probability = int(getattr(settings, 'MISERY_404_PROBABILITY', 10))
whiteScreenProbability = int(getattr(settings, 'MISERY_WHITE_SCREEN_PROBABILITY', 10))
ASPdeathProbability = int(getattr(settings, 'MISERY_ASP_ERROR_PROBABILITY', 10))

assert slowBanStrength >= 0
assert logoutProbability >= 0 and logoutProbability <= 100
assert e403Probability >= 0 and e403Probability <= 100
assert e404Probability >= 0 and e404Probability <= 100
assert whiteScreenProbability >= 0 and whiteScreenProbability <= 100
assert ASPdeathProbability >= 0 and ASPdeathProbability <= 100

class miserize(object):
    def process_request(self, request):
        user = request.user
        ip = request.META['REMOTE_ADDR']

        is_miserized = MiseryIP.objects.filter(ip=ip).count() > 0

        if is_miserized:
            # unleash the wrath
            logger.debug(ip + " is miserized")
            sleep(randint(int(slowBanStrength), 2*int(slowBanStrength)))

            miserize.luck = randint(0, 100)
            def out_of_luck(probability):
                miserize.luck -= int(probability)
                return miserize.luck <= 0

            if out_of_luck(logoutProbability):
                logout(request)
            elif out_of_luck(e403Probability):
                raise PermissionDenied
            elif out_of_luck(e404Probability):
                raise Http404
            elif out_of_luck(whiteScreenProbability):
                return HttpResponse("")
            elif out_of_luck(ASPdeathProbability):
                return render_to_response('django_misery/ASPerror.html')
            # else leave him alone, the poor pal
