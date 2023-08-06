import os
from django.db.models import signals
from django.db import models
from django.contrib.auth.models import User
from push2.utils import get_hash_file_name
from push2.utils import ack_and_touch
from settings import MEDIA_ROOT


class Channel(models.Model):
    creation_date = models.DateTimeField('creation_date', auto_now=True)
    name = models.CharField('name', max_length=255, blank=False, null=True, unique=True)
    users_connected = models.ManyToManyField(User, related_name='clients', verbose_name='clients')
    file_path = models.CharField('file path', max_length=255, editable=False, unique=True)
    description = models.TextField('description', max_length=200, blank=True, null=True)
    owner = models.ForeignKey(User, verbose_name='owner')
    messages_ttl = models.IntegerField('messages TTL', default=720, help_text='in minutes')

    def save(self, *args, **kwargs):
        if not os.path.exists(os.path.join(MEDIA_ROOT, 'storage')):
            os.makedirs(os.path.join(MEDIA_ROOT, 'storage'))
        self.file_path = '%s/storage/%s.ch' % (MEDIA_ROOT, get_hash_file_name(self))
        f = open(self.file_path, "w+")
        f.close()
        super(Channel, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'channel'
        verbose_name_plural = 'channels'

    def __unicode__(self):
        return '%s - %s' % (self.pk, self.name)


class Message(models.Model):
    channel = models.ForeignKey(Channel, verbose_name='channel', db_index=True)
    text = models.TextField('text')
    time_insert = models.DateTimeField('insert time', auto_now=True)
    time_send = models.DateTimeField('send time')
    sender = models.ForeignKey(User, verbose_name='sender')


class Ack(models.Model):
    message = models.ForeignKey(Message, verbose_name='message')
    user = models.ForeignKey(User, verbose_name='user')


signals.post_save.connect(ack_and_touch, sender=Message)
