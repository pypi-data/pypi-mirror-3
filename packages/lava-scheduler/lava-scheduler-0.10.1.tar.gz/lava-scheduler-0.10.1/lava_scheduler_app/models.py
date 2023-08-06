import simplejson

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _

from linaro_django_xmlrpc.models import AuthToken

class JSONDataError(ValueError):
    """Error raised when JSON is syntactically valid but ill-formed."""


class Tag(models.Model):

    name = models.SlugField(unique=True)

    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name


def validate_job_json(data):
    try:
        ob = simplejson.loads(data)
    except ValueError, e:
        raise ValidationError(str(e))
    else:
        if not isinstance(ob, dict):
            raise ValidationError(
                "job json must be an object, not %s" % type(ob).__name__)


class DeviceType(models.Model):
    """
    A class of device, for example a pandaboard or a snowball.
    """

    name = models.SlugField(primary_key=True)

    def __unicode__(self):
        return self.name

    health_check_job = models.TextField(
        null=True, blank=True, default=None, validators=[validate_job_json])


class Device(models.Model):
    """
    A device that we can run tests on.
    """

    OFFLINE = 0
    IDLE = 1
    RUNNING = 2
    OFFLINING = 3

    STATUS_CHOICES = (
        (OFFLINE, 'Offline'),
        (IDLE, 'Idle'),
        (RUNNING, 'Running'),
        (OFFLINING, 'Going offline'),
    )

    # A device health shows a device is ready to test or not
    HEALTH_UNKNOWN, HEALTH_PASS, HEALTH_FAIL = range(3)
    HEALTH_CHOICES = (
        (HEALTH_UNKNOWN, 'Unknown'),
        (HEALTH_PASS, 'Pass'),
        (HEALTH_FAIL, 'Fail'),
    )

    hostname = models.CharField(
        verbose_name = _(u"Hostname"),
        max_length = 200,
        primary_key = True,
    )

    device_type = models.ForeignKey(
        DeviceType, verbose_name=_(u"Device type"))

    current_job = models.ForeignKey(
        "TestJob", blank=True, unique=True, null=True, related_name='+')

    tags = models.ManyToManyField(Tag, blank=True)

    status = models.IntegerField(
        choices = STATUS_CHOICES,
        default = IDLE,
        verbose_name = _(u"Device status"),
    )

    health_status = models.IntegerField(
        choices = HEALTH_CHOICES,
        default = HEALTH_UNKNOWN,
        verbose_name = _(u"Device Health"),
    )

    last_health_report_job = models.ForeignKey(
            "TestJob", blank=True, unique=True, null=True, related_name='+')

    def __unicode__(self):
        return self.hostname

    @models.permalink
    def get_absolute_url(self):
        return ("lava.scheduler.device.detail", [self.pk])

    @models.permalink
    def get_device_health_url(self):
        return ("lava.scheduler.labhealth.detail", [self.pk])

    def recent_jobs(self):
        return TestJob.objects.select_related(
            "actual_device",
            "requested_device",
            "requested_device_type",
            "submitter",
        ).filter(
            actual_device=self
        ).order_by(
            '-start_time'
        )

    def can_admin(self, user):
        return user.has_perm('lava_scheduler_app.change_device')

    def put_into_maintenance_mode(self, user, reason):
        if self.status in [self.RUNNING, self.OFFLINING]:
            new_status = self.OFFLINING
        else:
            new_status = self.OFFLINE
        DeviceStateTransition.objects.create(
            created_by=user, device=self, old_state=self.status,
            new_state=new_status, message=reason, job=None).save()
        self.status = new_status
        self.save()

    def put_into_online_mode(self, user, reason):
        if self.status not in [Device.OFFLINE, Device.OFFLINING]:
            return
        new_status = self.IDLE
        DeviceStateTransition.objects.create(
            created_by=user, device=self, old_state=self.status,
            new_state=new_status, message=reason, job=None).save()
        self.status = new_status
        self.health_status = Device.HEALTH_UNKNOWN
        self.save()

    #@classmethod
    #def find_devices_by_type(cls, device_type):
    #    return device_type.device_set.all()


class TestJob(models.Model):
    """
    A test job is a test process that will be run on a Device.
    """

    SUBMITTED = 0
    RUNNING = 1
    COMPLETE = 2
    INCOMPLETE = 3
    CANCELED = 4
    CANCELING = 5

    STATUS_CHOICES = (
        (SUBMITTED, 'Submitted'),
        (RUNNING, 'Running'),
        (COMPLETE, 'Complete'),
        (INCOMPLETE, 'Incomplete'),
        (CANCELED, 'Canceled'),
        (CANCELING, 'Canceling'),
    )

    id = models.AutoField(primary_key=True)

    submitter = models.ForeignKey(
        User,
        verbose_name = _(u"Submitter"),
    )

    submit_token = models.ForeignKey(AuthToken, null=True, blank=True)

    description = models.CharField(
        verbose_name = _(u"Description"),
        max_length = 200,
        null = True,
        blank = True,
        default = None
    )

    health_check = models.BooleanField(default=False)

    # Only one of these two should be non-null.
    requested_device = models.ForeignKey(
        Device, null=True, default=None, related_name='+', blank=True)
    requested_device_type = models.ForeignKey(
        DeviceType, null=True, default=None, related_name='+', blank=True)

    tags = models.ManyToManyField(Tag, blank=True)

    # This is set once the job starts.
    actual_device = models.ForeignKey(
        Device, null=True, default=None, related_name='+', blank=True)

    #priority = models.IntegerField(
    #    verbose_name = _(u"Priority"),
    #    default=0)
    submit_time = models.DateTimeField(
        verbose_name = _(u"Submit time"),
        auto_now = False,
        auto_now_add = True
    )
    start_time = models.DateTimeField(
        verbose_name = _(u"Start time"),
        auto_now = False,
        auto_now_add = False,
        null = True,
        blank = True,
        editable = False
    )
    end_time = models.DateTimeField(
        verbose_name = _(u"End time"),
        auto_now = False,
        auto_now_add = False,
        null = True,
        blank = True,
        editable = False
    )
    status = models.IntegerField(
        choices = STATUS_CHOICES,
        default = SUBMITTED,
        verbose_name = _(u"Status"),
    )
    definition = models.TextField(
        editable = False,
    )
    log_file = models.FileField(
        upload_to='lava-logs', default=None, null=True, blank=True)

    results_link = models.CharField(
        max_length=400, default=None, null=True, blank=True)

    def __unicode__(self):
        r = "%s test job" % self.get_status_display()
        if self.requested_device:
            r += " for %s" % (self.requested_device.hostname,)
        return r

    @models.permalink
    def get_absolute_url(self):
        return ("lava.scheduler.job.detail", [self.pk])

    @classmethod
    def from_json_and_user(cls, json_data, user):
        job_data = simplejson.loads(json_data)
        if 'target' in job_data:
            target = Device.objects.get(hostname=job_data['target'])
            device_type = None
        elif 'device_type' in job_data:
            target = None
            device_type = DeviceType.objects.get(name=job_data['device_type'])
        else:
            raise JSONDataError(
                "Neither 'target' nor 'device_type' found in job data.")
        job_name = job_data.get('job_name', '')

        is_check = job_data.get('health_check', False)

        tags = []
        for tag_name in job_data.get('device_tags', []):
            try:
                tags.append(Tag.objects.get(name=tag_name))
            except Tag.DoesNotExist:
                raise JSONDataError("tag %r does not exist" % tag_name)
        job = TestJob(
            definition=json_data, submitter=user, requested_device=target,
            requested_device_type=device_type, description=job_name,
            health_check=is_check)
        job.save()
        for tag in tags:
            job.tags.add(tag)
        return job

    def can_cancel(self, user):
        return user.is_superuser or user == self.submitter

    def cancel(self):
        if self.status == TestJob.RUNNING:
            self.status = TestJob.CANCELING
        else:
            self.status = TestJob.CANCELED
        self.save()


class DeviceStateTransition(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, blank=True)
    device = models.ForeignKey(Device, related_name='transitions')
    job = models.ForeignKey(TestJob, null=True, blank=True)
    old_state = models.IntegerField(choices=Device.STATUS_CHOICES)
    new_state = models.IntegerField(choices=Device.STATUS_CHOICES)
    message = models.TextField(null=True, blank=True)
