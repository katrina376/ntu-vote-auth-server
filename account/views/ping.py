from account.models import Session
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.views.decorators import check_prerequisites
from core.views.utils import error, logger

@api_view(['POST'])
@check_prerequisites('token')
def ping(request):
    token = request.DATA['token']
    current_time = timezone.now()
    try:
        session = Session.objects.get(token=token)
        if session.expired_on >= current_time:
            logger.error('Session expired for token %s', token)
            return error('unauthorized', status.HTTP_401_UNAUTHORIZED)
    except Session.DoesNotExist:
        logger.error('Ping attempted failed for token %s', token)
        return error('unauthorized', status.HTTP_401_UNAUTHORIZED)

    session.last_seen = current_time
    session.save()
    return Response({'status': 'success', 'timestamp': current_time.isoformat()})