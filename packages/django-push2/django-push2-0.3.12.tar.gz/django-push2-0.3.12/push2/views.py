from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import simplejson as json
from django.http import HttpResponse
from push2.models import Channel, Message
from push2.connections import PushConnections
from push2.signals import message_write, message_get, connection_get


def prepare_connection(request):
    acks = []
    channels = json.loads(request.POST['channels'])
    if request.POST['acks']:
        acks = json.loads(request.POST['acks'])
    return PushConnections(request.user, channels, acks)


@login_required
@csrf_exempt
def channel_connection(request):
    dp_connection = prepare_connection(request)
    dp_connection.clean_queue()
    external_response = connection_get.send(sender=PushConnections, connection_data=request.POST)
    try:
        if external_response[0][1]:
            return external_response[0][1]
    except:
        pass
    dp_connection.listen()
    data = dp_connection.get_new_messages()
    external_response = message_get.send(sender=Message, messages=data)
    try:
        if external_response[0][1]:
            return external_response[0][1]
    except:
        pass
    return HttpResponse(json.dumps({'success': 'True', 'data': data}))


@csrf_exempt
@login_required
def channel_write(request):
    channels = json.loads(request.POST['write_channels'])
    for channel in channels:
        message = Message.objects.create(
            text=json.loads(request.POST['text']),
            channel=Channel.objects.get(pk=channel),
            sender=request.user,
            time_send=datetime.fromtimestamp(float(request.POST['time_send']) / 1000),
        )
    external_response = message_write.send(sender=Message, message=message)
    try:
        if external_response[0][1]:
            return external_response[0][1]
    except:
        pass
    return HttpResponse(json.dumps({'success': 'True'}))
