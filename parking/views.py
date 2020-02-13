from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django_tables2 import SingleTableView

from .models import Spot, Future
from .tables import FutureTable
from .forms import FutureForm

@login_required
def index(request):
    context = {'spots': Spot.objects.all()}
    return render(request, 'index.html', context)

# class SavingCreateView(LoginRequiredMixin, CreateView):

#     def form_valid(self, form):
#         form.instance.creator = self.request.user
#         return super().form_valid(form)


class FutureCreate(LoginRequiredMixin, CreateView):
    model = Future
    form_class = FutureForm
    template_name = 'create_form.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        print(self.object)
        return '/'


class FutureList(LoginRequiredMixin, SingleTableView):
    table_class = FutureTable
    queryset = Future.objects.all()
    template_name = 'future_list.html'