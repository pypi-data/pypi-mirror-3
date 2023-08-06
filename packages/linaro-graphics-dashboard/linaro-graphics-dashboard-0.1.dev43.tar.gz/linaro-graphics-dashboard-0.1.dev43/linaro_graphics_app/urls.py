from django.conf.urls.defaults import url, patterns


urlpatterns = patterns(
    'linaro_graphics_app.views',
    (r'board/(?P<board_name>\w+?)/$', 'board'),
    (r'board/(?P<board_name>\w+?)/(?P<test_id>\w+?)/$', 'test'),
    (r'board/(?P<board_name>\w+?)/(?P<test_id>\w+?)/(?P<test_case_id>.+?)/$', 'test_case'),
    (r'^$', 'index'))
