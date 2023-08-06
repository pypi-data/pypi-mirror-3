from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.dates import YearArchiveView, MonthArchiveView, DayArchiveView

from devotionals.models import Devotional

urlpatterns = patterns('',
    url(r'^(?P<year>[\d]+)/$', 
	view=YearArchiveView.as_view(
				model=Devotional,
				make_object_list=True), 
	name='dv-devotional-year-archive'),
    url(r'^(?P<year>[\d]+)/(?P<month>[\w]+/$', 
        view=MonthArchiveView.as_view(
				model=Devotional,
				make_object_list=True), 
	name='dv-devotional-month-archive'),
    url(r'^(?P<year>[\d]+)/(?P<month>[\w]+/(?P<day>[\d]+)/$', 
        view=DayArchiveView.as_view(
				model=Devotional,
				make_object_list=True), 
	name='dv-devotional-detail'),
)

