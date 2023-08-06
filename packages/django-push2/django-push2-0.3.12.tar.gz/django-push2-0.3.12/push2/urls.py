from django.conf.urls.defaults import url, patterns

urlpatterns = patterns("",
    url(r"^channel/connections/", 'push2.views.channel_connection', name="channel_connections"),
    url(r"^channel/write/$", 'push2.views.channel_write', name="channel_write"),
)
