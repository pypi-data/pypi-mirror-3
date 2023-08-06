import django.dispatch

message_write = django.dispatch.Signal(providing_args=["message"])
message_get = django.dispatch.Signal(providing_args=["messages"])
connection_get = django.dispatch.Signal(providing_args=["connection_data"])
