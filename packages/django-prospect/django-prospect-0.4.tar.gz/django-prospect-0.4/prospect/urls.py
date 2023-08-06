# -*- coding: utf-8 -*-
from intranet.utils import get_default_model_url
from models import Prospect, Field, Activity
from views import ProspectListView, ProspectCreateView, ActivityCreateView, ActivityUpdateView, ActivityListView, ProspectActivityView, FieldListView
from django.conf.urls import patterns, url

# Add specific patterns
urlpatterns = patterns('',
    url(
        r'^import/$',
        'prospect.views.import_index',
        name = 'import-index',
    ),
    url(
        r'^import/correction/cancel$',
        'prospect.views.treat_correction',
        kwargs = {'cancel': True, 'skip': False},
        name = 'import-cancel',
    ),
    url(
        r'^import/correction/skip$',
        'prospect.views.treat_correction',
        kwargs = {'cancel': False, 'skip': True},
        name = 'import-skip',
    ),
    url(
        r'^import/correction/create$',
        'prospect.views.treat_correction',
        kwargs = {'cancel': False, 'skip': False},
        name = 'import-submit',
    ),
    url(
        r'^prospect/(?P<prospect_id>\d+)/activities$',
        ProspectActivityView.as_view(),
        kwargs = {},
        name = 'prospect-activity-index',
    ),
)

urlpatterns += get_default_model_url(
    Prospect, 
    list_view = ProspectListView,
    creation_view = ProspectCreateView,
)

urlpatterns += get_default_model_url(
    Field,
    list_view = FieldListView,
)

urlpatterns += get_default_model_url(
    Activity,
    creation_view = ActivityCreateView,
    update_view = ActivityUpdateView,
    list_view = ActivityListView,
)

