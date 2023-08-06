import hashlib
import fcntl


def get_hash_file_name(channel):
    hash_str = hashlib.md5('%s' % (channel.name)).hexdigest()
    return hash_str


def ack_and_touch(sender, **kwargs):
    from push2.models import Ack
    message = kwargs['instance']
    Ack.objects.create(
        user=message.sender,
        message=message
    )
    f = open(message.channel.file_path, 'w')
    fcntl.flock(f, fcntl.LOCK_EX)
    f.write(message.time_insert.strftime("%Y-%m-%d %H:%M:%S.%f"))
    f.close()
