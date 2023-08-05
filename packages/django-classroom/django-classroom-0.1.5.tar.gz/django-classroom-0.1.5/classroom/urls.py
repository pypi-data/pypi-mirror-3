from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from classroom.models import Staff, Position, School 


# custom views vendors
urlpatterns = patterns('',
    url(r'^$', view=ListView.as_view(model=Position, template_name="classroom/index.html"), name="cl-index"),
    url(r'^teachers/$', view=ListView.as_view(context_object_name='teacher_list', queryset=Staff.teacher_objects.all()), name="cl-staff-list"),
	url(r'^teachers/(?P<slug>[-\w]+)/$', view=DetailView.as_view(model=Staff), name="cl-staff-detail"),

    #url(r'^schools/$', view=ListView.as_view(model=School), name="cl-school-list"),
    #url(r'^schools/(?P<slug>[-\w]+)/$', view=DetailView.as_view(model=School), name="cl-school-detail"),

)
