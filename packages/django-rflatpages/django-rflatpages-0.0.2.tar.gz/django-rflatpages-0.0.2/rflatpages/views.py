# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from django.contrib.sites.models import Site
import models as mymodels
import forms as myforms

from django.conf import settings as conf

from django.views.generic import DetailView


class FlatpageDetailView(DetailView):

    template_name = "rflatpages/default.html"
    context_object_name = "myflatpage"

    def __init__(self):
        pass

    def get_object(self):
        if (not self.kwargs['slug']):
            self.kwargs['slug'] = 'start'
        self.obj = get_object_or_404(mymodels.Pages, slug=self.kwargs['slug'], status=1)
        self.obj.hits = self.obj.hits + 1
        self.obj.save()
        return self.obj

    def get_context_data(self, **kwargs):
        context = super(FlatpageDetailView, self).get_context_data(**kwargs)
        context.update({
        })
        return context
