from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _
from django.views.generic.list_detail import object_list
from django.conf.urls.defaults import *

from views import answers_list, answers_detail,\
               survey_detail, survey_edit, survey_add,\
               editable_survey_list, survey_update,\
               question_add, question_update,\
               choice_add, choice_update, delete_image,\
               visible_survey_list, object_delete

urlpatterns = patterns('',


    url(r'^$', visible_survey_list, name='surveys-visible'),
    url(r'^editable/$', editable_survey_list, name='surveys-editable'),
    url(r'^new/$', survey_add,   name='survey-add'),

    url(r'^(?P<survey_slug>[-\w]+)/answers/$',
        answers_list,    name='survey-results'),
    url(r'^(?P<survey_slug>[-\w]+)/answers/(?P<key>[a-fA-F0-9]{10,40})/$',
        answers_detail,  name='answers-detail'),
    url(r'^(?P<survey_slug>[-\w]+)/edit$', survey_edit,   name='survey-edit'),
    url(r'^(?P<survey_slug>[-\w]+)/update$', survey_update,   name='survey-update'),
    url(r'^(?P<survey_slug>[-\w]+)/delete$', object_delete, {'object_type': 'survey', }, name='survey-delete'),

    url(r'^(?P<survey_slug>[-\w]+)/question/add$', question_add,   name='question-add'),
    url(r'^(?P<survey_slug>[-\w]+)/(?P<question_id>\d+)/question/update$', question_update,   name='question-update'),
    url(r'^(?P<survey_slug>[-\w]+)/(?P<question_id>\d+)/question/delete$', object_delete, {'object_type':'question', }, name='question-delete'),

    url(r'^(?P<survey_slug>[-\w]+)/(?P<question_id>\d+)/choice/add$', choice_add,   name='choice-add'),
    url(r'^(?P<survey_slug>[-\w]+)/(?P<question_id>\d+)/choice/(?P<choice_id>\d+)/update$', choice_update,   name='choice-update'),
    url(r'^(?P<survey_slug>[-\w]+)/choice/(?P<object_id>\d+)/delete$', object_delete, {'object_type': 'choice', }, name='choice-delete'),

    url(r'^delete_image/(?P<model_string>[-\w]+)/(?P<object_id>\d+)/$', delete_image, name='delete-image'),
    url(r'^(?P<survey_slug>[-\w]+)/$', survey_detail,   name='survey-detail'),

    )
