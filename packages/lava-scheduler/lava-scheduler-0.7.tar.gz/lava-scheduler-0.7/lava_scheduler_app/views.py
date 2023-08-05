from collections import defaultdict
import simplejson
import logging
import os
import StringIO

from logfile_helper import formatLogFile, getDispatcherErrors
from logfile_helper import getDispatcherLogMessages, getDispatcherLogSize

from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
    )
from django.template import RequestContext
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render_to_response,
)

from lava_scheduler_app.models import Device, TestJob
from lava_server.views import index as lava_index
from lava_server.bread_crumbs import (
    BreadCrumb,
    BreadCrumbTrail,
)


def post_only(func):
    def decorated(request, *args, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed('Only POST here')
        return func(request, *args, **kwargs)
    return decorated


@BreadCrumb("Scheduler", parent=lava_index)
def index(request):
    return render_to_response(
        "lava_scheduler_app/index.html",
        {
            'devices': Device.objects.select_related("device_type"),
            'jobs': TestJob.objects.select_related(
                "actual_device", "requested_device", "requested_device_type",
                "submitter").filter(status__in=[
                TestJob.SUBMITTED, TestJob.RUNNING]),
            'bread_crumb_trail': BreadCrumbTrail.leading_to(index),
        },
        RequestContext(request))


@BreadCrumb("All Jobs", parent=index)
def job_list(request):
    return render_to_response(
        "lava_scheduler_app/alljobs.html",
        {
            'jobs': TestJob.objects.select_related(
                "actual_device", "requested_device", "requested_device_type",
                "submitter").all(),
            'bread_crumb_trail': BreadCrumbTrail.leading_to(job_list),
        },
        RequestContext(request))


@BreadCrumb("Job #{pk}", parent=index, needs=['pk'])
def job_detail(request, pk):
    job = get_object_or_404(TestJob, pk=pk)
    job_errors = getDispatcherErrors(job.log_file)
    job_log_messages = getDispatcherLogMessages(job.log_file)

    levels = defaultdict(int)
    for kl in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        levels[kl] = 0
    for level, msg in job_log_messages:
        levels[level] += 1
    levels = sorted(levels.items(), key=lambda (k,v):logging._levelNames.get(k))

    return render_to_response(
        "lava_scheduler_app/job.html",
        {
            'job': TestJob.objects.get(pk=pk),
            'show_cancel': job.status <= TestJob.RUNNING and job.can_cancel(request.user),
            'bread_crumb_trail': BreadCrumbTrail.leading_to(job_detail, pk=pk),
            'job_errors' : job_errors,
            'job_has_error' : len(job_errors) > 0,
            'job_log_messages' : job_log_messages,
            'levels': levels,
            'show_reload_page' : job.status <= TestJob.RUNNING,
            'job_file_size' : getDispatcherLogSize(job.log_file),
        },
        RequestContext(request))


def job_definition(request, pk):
    job = get_object_or_404(TestJob, pk=pk)
    return render_to_response(
        "lava_scheduler_app/job_definition.html",
        {
            'job': job,
        },
        RequestContext(request))


def job_definition_plain(request, pk):
    job = get_object_or_404(TestJob, pk=pk)
    response = HttpResponse(job.definition, mimetype='text/plain')
    response['Content-Disposition'] = "attachment; filename=job_%d.json"%job.id
    return response


@BreadCrumb("Complete log", parent=job_detail, needs=['pk'])
def job_log_file(request, pk):
    job = get_object_or_404(TestJob, pk=pk)
    content = formatLogFile(job.log_file)
    return render_to_response(
        "lava_scheduler_app/job_log_file.html",
        {
            'job': TestJob.objects.get(pk=pk),
            'sections' : content,
            'job_file_size' : getDispatcherLogSize(job.log_file),
        },
        RequestContext(request))


def job_log_file_plain(request, pk):
    job = get_object_or_404(TestJob, pk=pk)
    response = HttpResponse(job.log_file, mimetype='text/plain')
    response['Content-Disposition'] = "attachment; filename=job_%d.log"%job.id
    return response


def job_log_incremental(request, pk):
    start = int(request.GET.get('start', 0))
    job = get_object_or_404(TestJob, pk=pk)
    log_file = job.log_file
    log_file.seek(start)
    new_content = log_file.read()
    m = getDispatcherLogMessages(StringIO.StringIO(new_content))
    response = HttpResponse(
        simplejson.dumps(m), content_type='application/json')
    response['X-Current-Size'] = str(start + len(new_content))
    if job.status not in [TestJob.RUNNING, TestJob.CANCELING]:
        response['X-Is-Finished'] = '1'
    return response


def job_full_log_incremental(request, pk):
    start = int(request.GET.get('start', 0))
    job = get_object_or_404(TestJob, pk=pk)
    log_file = job.log_file
    log_file.seek(start)
    new_content = log_file.read()
    nl_index = new_content.rfind('\n', -NEWLINE_SCAN_SIZE)
    if nl_index >= 0:
        new_content = new_content[:nl_index+1]
    m = formatLogFile(StringIO.StringIO(new_content))
    response = HttpResponse(
        simplejson.dumps(m), content_type='application/json')
    response['X-Current-Size'] = str(start + len(new_content))
    if job.status not in [TestJob.RUNNING, TestJob.CANCELING]:
        response['X-Is-Finished'] = '1'
    return response


LOG_CHUNK_SIZE = 512*1024
NEWLINE_SCAN_SIZE = 80


def job_output(request, pk):
    start = int(request.GET.get('start', 0))
    count_present = 'count' in request.GET
    job = get_object_or_404(TestJob, pk=pk)
    log_file = job.log_file
    log_file.seek(0, os.SEEK_END)
    size = int(request.GET.get('count', log_file.tell()))
    if size - start > LOG_CHUNK_SIZE and not count_present:
        log_file.seek(-LOG_CHUNK_SIZE, os.SEEK_END)
        content = log_file.read(LOG_CHUNK_SIZE)
        nl_index = content.find('\n', 0, NEWLINE_SCAN_SIZE)
        if nl_index > 0 and not count_present:
            content = content[nl_index + 1:]
        skipped = size - start - len(content)
    else:
        skipped = 0
        log_file.seek(start, os.SEEK_SET)
        content = log_file.read(size - start)
    nl_index = content.rfind('\n', -NEWLINE_SCAN_SIZE)
    if nl_index >= 0 and not count_present:
        content = content[:nl_index+1]
    response = HttpResponse(content)
    if skipped:
        response['X-Skipped-Bytes'] = str(skipped)
    response['X-Current-Size'] = str(start + len(content))
    if job.status not in [TestJob.RUNNING, TestJob.CANCELING]:
        response['X-Is-Finished'] = '1'
    return response


@post_only
def job_cancel(request, pk):
    job = get_object_or_404(TestJob, pk=pk)
    if job.can_cancel(request.user):
        job.cancel()
        return redirect(job)
    else:
        return HttpResponseForbidden(
            "you cannot cancel this job", content_type="text/plain")


def job_json(request, pk):
    job = get_object_or_404(TestJob, pk=pk)
    json_text = simplejson.dumps({
        'status': job.get_status_display(),
        'results_link': job.results_link,
        })
    content_type = 'application/json'
    if 'callback' in request.GET:
        json_text = '%s(%s)'%(request.GET['callback'], json_text)
        content_type = 'text/javascript'
    return HttpResponse(json_text, content_type=content_type)


@BreadCrumb("Device {pk}", parent=index, needs=['pk'])
def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk)
    return render_to_response(
        "lava_scheduler_app/device.html",
        {
            'device': device,
            'recent_job_list': device.recent_jobs,
            'show_maintenance': device.can_admin(request.user) and \
                device.status in [Device.IDLE, Device.RUNNING],
            'show_online': device.can_admin(request.user) and \
                device.status in [Device.OFFLINE, Device.OFFLINING],
            'bread_crumb_trail': BreadCrumbTrail.leading_to(device_detail, pk=pk),
        },
        RequestContext(request))


@post_only
def device_maintenance_mode(request, pk):
    device = Device.objects.get(pk=pk)
    if device.can_admin(request.user):
        device.put_into_maintenance_mode()
        return redirect(device)
    else:
        return HttpResponseForbidden(
            "you cannot administer this device", content_type="text/plain")


@post_only
def device_online(request, pk):
    device = Device.objects.get(pk=pk)
    if device.can_admin(request.user):
        device.put_into_online_mode()
        return redirect(device)
    else:
        return HttpResponseForbidden(
            "you cannot administer this device", content_type="text/plain")
