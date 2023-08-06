import time
import fcntl
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils import simplejson as json
from push2.models import Channel, Message, Ack


class PushConnections:
    def __init__(self, user, channels, acks=[]):
        self.DATA_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
        self.user = user
        self.channels = []
        for channel_id in channels:
            self.channels.append(Channel.objects.get(pk=channel_id))
        self.last_time = datetime.fromtimestamp(time.time())
        self.add_user_to_channel()
        self.response_message = []
        self.first_time = True
        if len(acks) > 0:
            self.set_acks(acks)

    def add_user_to_channel(self):
        for channel in self.channels:
            if self.user not in channel.users_connected.all():
                channel.users_connected.add(self.user)

    def set_acks(self, acks):
        for ack in acks:
            Ack.objects.create(
                user=self.user,
                message=Message.objects.get(pk=int(ack))
            )

    def clean_queue(self):
        for channel in self.channels:
            border_date = datetime.today() - timedelta(minutes=channel.messages_ttl)
            messages_to_delete = Message.objects.filter(channel=channel).filter(time_insert__lt=border_date)
            try:
                messages_to_delete.ack_set.all().delete()
                messages_to_delete.delete()
            except:
                pass
        return True

    def check_lose_messages(self, channel):
        prev_messages = Message.objects.filter(channel=channel).order_by('time_insert')
        for pm in prev_messages:
            if pm.ack_set.filter(user=self.user).count() == 0:
                self.last_time = pm.time_insert
                break
        self.first_time = False

    def channel_updated(self, channel):
        if self.first_time:
            self.check_lose_messages(channel)
        f = open(channel.file_path, 'r')
        fcntl.flock(f, fcntl.LOCK_EX)
        time_last_mod = f.read()
        time_last_mod = datetime.now() if not time_last_mod else datetime.strptime(time_last_mod, self.DATA_FORMAT)
        f.close()
        has_message = False
        if time_last_mod > self.last_time:
            has_message = True
        return has_message

    def get_message_from_channel(self, channel):
        messages = Message.objects.filter(channel=channel).filter(time_insert__gt=self.last_time).order_by('-time_insert')
        list_of_message = []
        for message in messages:
            missed_acks = Ack.objects.filter(user=self.user).filter(message=message)
            if missed_acks.count() == 0:
                list_of_message.append({
                                        'text': message.text,
                                        'channel': channel.pk,
                                        'time': message.time_insert.strftime(self.DATA_FORMAT),
                                        'id': message.pk,
                                        'sender': message.sender.pk
                                        })
        return list_of_message

    def listen(self):
        last_mod_is_the_same = True
        while last_mod_is_the_same:
            time.sleep(0.5)
            for channel in self.channels:
                if self.channel_updated(channel):
                    list_of_message = self.get_message_from_channel(channel)
                    for message in list_of_message:
                        self.response_message.append(message)
                        last_mod_is_the_same = False
        self.response_message

    def get_new_messages(self, format=None):
        if not format:
            return self.response_message
        elif format == 'json':
            return json.dumps(self.response_message)

    def delete_users_to_channel(self):
        try:
            for channel in self.channels:
                user_connected = channel.users_connected_set.filter(user=self.user)
                user_connected.delete()
        except Channel.DoesNotExist:
            return HttpResponse(json.dumps({'success': 'False', 'error': 'Can\'t delete users from Channel'}))
