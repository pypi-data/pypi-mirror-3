# -*- coding: utf-8 -*-
from intranet.utils import get_default_model_url
from models import Prospect, Field
from views import ProspectListView

# Add specific patterns
urlpatterns = get_default_model_url(Prospect, 
                                    list_view=ProspectListView)
                                    
urlpatterns += get_default_model_url(Field)

