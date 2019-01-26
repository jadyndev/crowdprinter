from django.contrib.auth.decorators import login_required
from django.views.generic.base import View, TemplateView
from django.views.generic import DetailView, ListView
import crowdprinter.models as models
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.urls import reverse
import os.path


class PrintJobListView(ListView):
    model = models.PrintJob


class PrintJobDetailView(DetailView):
    model = models.PrintJob


@login_required
def take_print_job(request, slug):
    if request.method != 'POST':
        return HttpResponseNotAllowed(permitted_methods=['POST'])

    models.PrintAttempt.objects.create(
        job=get_object_or_404(models.PrintJob, slug=slug),
        user=request.user,
    )

    return HttpResponseRedirect(reverse('printjob_detail', kwargs={'slug': slug}))


class ServeFileView(View):

    def get(self, *args, **kwargs):
        with open(self.get_file_path(**kwargs), mode='rb') as f:
            response = HttpResponse(
                f.read(),
                content_type='application/force-download',
            )
        dl_path = self.get_download_file_name(**kwargs)
        response['Content-Disposition'] = f'attachment; filename={dl_path}'
        return response

    def get_file_path(self, **kwargs):
        raise NotImplementedError()

    def get_download_file_name(self, **kwargs):
        raise NotImplementedError()


class ServeStlView(ServeFileView):
    def get_file_path(self, **kwargs):
        printjob = get_object_or_404(models.PrintJob, slug=kwargs['slug'])
        return printjob.stl.path

    def get_download_file_name(self, **kwargs):
        return f'eh19_{kwargs["slug"]}.stl'


class ServeRenderView(ServeFileView):
    def get_file_path(self, **kwargs):
        printjob = get_object_or_404(models.PrintJob, slug=kwargs['slug'])
        return printjob.render.path

    def get_download_file_name(self, **kwargs):
        printjob = get_object_or_404(models.PrintJob, slug=kwargs['slug'])
        ext = os.path.splitext(printjob.render.path)[1]
        return f'eh19_{kwargs["slug"]}.{ext}'
