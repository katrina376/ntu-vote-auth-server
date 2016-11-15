from core.models import Record
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .decorators import login_required, permission, check_prerequisites
from account.models import User
from .utils import logger, error


@api_view(['GET'])
@login_required
@permission(User.ADMIN, User.SUPERVISOR)
def reset_list(request):
    return Response({
        'status': 'success',
        'target': [{'student_id': r.student_id} for r in Record.objects.filter(state=Record.RESETTING)],
    })


@api_view(['POST'])
@login_required
@permission(User.ADMIN)
@check_prerequisites('uid')
def apply_reset(request):
    uid = request.data['uid']

    # Fetch Elector
    try:
        record = Record.objects.get(student_id=uid)

    except Record.DoesNotExist:
        logger.error('reset target (%s) not found', uid)
        return error('student not found')

    # Log this event
    logger.info('Admin %s create a reset request (%s - %s)', request.user.username, uid, record.state)

    record.state = Record.RESETTING
    record.save()

    return Response({
        'status': 'success',
        'message': 'reset request created',
    })


@api_view(['POST'])
@login_required
@permission(User.SUPERVISOR)
@check_prerequisites('uid')
def confirm_reset(request):
    uid = request.data['uid']

    # Fetch Elector
    try:
        record = Record.objects.get(student_id=uid)

    except Record.DoesNotExist:
        logger.error('student (%s) not found', uid)
        return error('student not found')

    # Checking elector state
    if record.state != Record.RESETTING:
        logger.info('reset request (%s) not found', uid)
        return error('reset request (%s) not found', uid)

    # Log this event
    logger.info('Resetting event (%s) accepted by %s', uid, request.user.username)

    # Reset to state AVAILABLE
    record.state = Record.AVAILABLE
    record.save()

    # Log this event
    logger.info('Supervisor %s apply the reset request (%s)', request.user.username, uid)

    return Response({
        'status': 'success',
        'message': 'reset request confirmed',
    })
