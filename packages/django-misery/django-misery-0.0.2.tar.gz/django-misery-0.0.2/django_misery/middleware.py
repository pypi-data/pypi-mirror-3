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

slowBanStrenght = getattr(settings, 'MISERY_SLOW_STRENGHT', '6')
logoutProbability = getattr(settings, 'MISERY_LOGOUT_PROBABILITY', '10')
e403Probability = getattr(settings, 'MISERY_403_PROBABILITY', '10')
e404Probability = getattr(settings, 'MISERY_404_PROBABILITY', '10')
whiteScreenProbability = getattr(settings, 'MISERY_WHITE_SCREEN_PROBABILITY', '20')
ASPdeathProbability = getattr(settings, 'MISERY_ASP_ERROR_PROBABILITY', '20')

class miserize(object):
    def process_request(self, request):
        user = request.user
        ip = request.META['REMOTE_ADDR']

        is_miserized = MiseryIP.objects.filter(ip=ip).count() > 0
        logger.debug(is_miserized)

        if is_miserized:
            # unleash the wrath
            sleep(randint(int(slowBanStrenght), 2*int(slowBanStrenght)))
            
            if randint(0, 100) <= int(logoutProbability):
                logout(request)
            elif randint(0, 100) <= int(e403Probability):
                raise PermissionDenied
            elif randint(0, 100) <= int(e404Probability):
                raise Http404
            elif randint(0, 100) <= int(whiteScreenProbability):
                return HttpResponse("")
            elif randint(0, 100) <= int(ASPdeathProbability):
                return render_to_response('django_misery/ASPerror.html')
            # else leave him alone, the poor pal
