from models import (StatusCheck,
                    Service,
                    Instance,
                    GraphiteStatusCheck,
                    ICMPStatusCheck,
                    HttpStatusCheck,
                    JenkinsStatusCheck,
                    Schedule)

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from datetime import timedelta
from itertools import groupby, dropwhile, izip_longest
import re


class SymmetricalForm(forms.ModelForm):
    symmetrical_fields = ()  # Iterable of 2-tuples (field, model)

    def __init__(self, *args, **kwargs):
        super(SymmetricalForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            for field in self.symmetrical_fields:
                self.fields[field].initial = getattr(
                    self.instance, field).all()

    def save(self, commit=True):
        instance = super(SymmetricalForm, self).save(commit=False)
        if commit:
            instance.save()
        if instance.pk:
            for field in self.symmetrical_fields:
                setattr(instance, field, self.cleaned_data[field])
            self.save_m2m()
        return instance

base_widgets = {
    'name': forms.TextInput(attrs={
        'style': 'width:30%',
    }),
    'importance': forms.RadioSelect(),
}


class StatusCheckForm(SymmetricalForm):

    symmetrical_fields = ('service_set', 'instance_set')

    service_set = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        help_text='Link to service(s).',
        widget=forms.SelectMultiple(
            attrs={
                'data-rel': 'chosen',
                'style': 'width: 70%',
            },
        )
    )

    instance_set = forms.ModelMultipleChoiceField(
        queryset=Instance.objects.all(),
        required=False,
        help_text='Link to instance(s).',
        widget=forms.SelectMultiple(
            attrs={
                'data-rel': 'chosen',
                'style': 'width: 70%',
            },
        )
    )


class GraphiteStatusCheckForm(StatusCheckForm):

    class Meta:
        model = GraphiteStatusCheck
        fields = (
            'name',
            'metric',
            'metric_selector',
            'group_by',
            'fill_empty',
            'where_clause',
            'check_type',
            'value',
            'frequency',
            'active',
            'importance',
            'interval',
            'expected_num_hosts',
            'expected_num_metrics',
            'debounce',
        )
        widgets = dict(**base_widgets)
        widgets.update({
            'value': forms.TextInput(attrs={
                'style': 'width: 100px',
                'placeholder': 'threshold value',
            }),
            'metric': forms.TextInput(attrs={
                'style': 'width: 100%',
                'placeholder': 'graphite metric key'
            }),
            'check_type': forms.Select(attrs={
                'data-rel': 'chosen',
            })
        })


class InfluxDBStatusCheckForm(StatusCheckForm):

    class Meta:
        model = GraphiteStatusCheck
        fields = (
            'name',
            'metric',
            'metric_selector',
            'group_by',
            'fill_empty',
            'where_clause',
            'check_type',
            'value',
            'frequency',
            'active',
            'importance',
            'interval',
            'expected_num_hosts',
            'expected_num_metrics',
            'debounce',
        )
        widgets = dict(**base_widgets)
        widgets.update({
            'value': forms.TextInput(attrs={
                'style': 'width: 100px',
                'placeholder': 'threshold value',
            }),
            'metric': forms.TextInput(attrs={
                'style': 'width: 100%',
                'placeholder': 'graphite metric key'
            }),
            'check_type': forms.Select(attrs={
                'data-rel': 'chosen',
            })
        })


class ICMPStatusCheckForm(StatusCheckForm):

    class Meta:
        model = ICMPStatusCheck
        fields = (
            'name',
            'frequency',
            'importance',
            'active',
            'debounce',
        )
        widgets = dict(**base_widgets)


class HttpStatusCheckForm(StatusCheckForm):

    class Meta:
        model = HttpStatusCheck
        fields = (
            'name',
            'endpoint',
            'http_method',
            'username',
            'password',
            'http_params',
            'http_body',
            'text_match',
            'header_match',
            'allow_http_redirects',
            'status_code',
            'timeout',
            'verify_ssl_certificate',
            'frequency',
            'importance',
            'active',
            'debounce',
        )
        widgets = dict(**base_widgets)
        widgets.update({
            'endpoint': forms.TextInput(attrs={
                'style': 'width: 100%',
                'placeholder': 'https://www.arachnys.com',
            }),
            'username': forms.TextInput(attrs={
                'style': 'width: 30%',
            }),
            'password': forms.TextInput(attrs={
                'style': 'width: 30%',
            }),
            'text_match': forms.TextInput(attrs={
                'style': 'width: 100%',
                'placeholder': '[Aa]rachnys\s+[Rr]ules',
            }),
            'status_code': forms.TextInput(attrs={
                'style': 'width: 20%',
                'placeholder': '200',
            }),
        })


class JenkinsStatusCheckForm(StatusCheckForm):

    class Meta:
        model = JenkinsStatusCheck
        fields = (
            'name',
            'importance',
            'debounce',
            'max_queued_build_time',
        )
        widgets = dict(**base_widgets)


class InstanceForm(SymmetricalForm):

    symmetrical_fields = ('service_set',)
    service_set = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        help_text='Link to service(s).',
        widget=forms.SelectMultiple(
            attrs={
                'data-rel': 'chosen',
                'style': 'width: 70%',
            },
        )
    )

    class Meta:
        model = Instance
        template_name = 'instance_form.html'
        fields = (
            'name',
            'address',
            'users_to_notify',
            'status_checks',
            'service_set',
        )
        widgets = {
            'name': forms.TextInput(attrs={'style': 'width: 30%;'}),
            'address': forms.TextInput(attrs={'style': 'width: 70%;'}),
            'status_checks': forms.SelectMultiple(attrs={
                'data-rel': 'chosen',
                'style': 'width: 70%',
            }),
            'service_set': forms.SelectMultiple(attrs={
                'data-rel': 'chosen',
                'style': 'width: 70%',
            }),
            'alerts': forms.SelectMultiple(attrs={
                'data-rel': 'chosen',
                'style': 'width: 70%',
            }),
            'users_to_notify': forms.CheckboxSelectMultiple(),
            'hackpad_id': forms.TextInput(attrs={'style': 'width:30%;'}),
        }

    def __init__(self, *args, **kwargs):
        ret = super(InstanceForm, self).__init__(*args, **kwargs)
        self.fields['users_to_notify'].queryset = User.objects.filter(
            is_active=True)
        return ret


class ServiceForm(forms.ModelForm):

    class Meta:
        model = Service
        template_name = 'service_form.html'
        fields = (
            'name',
            'url',
            'users_to_notify',
            'schedule',
            'status_checks',
            'instances',
            'alerts',
            'alerts_enabled',
            'hackpad_id',
        )
        widgets = {
            'name': forms.TextInput(attrs={'style': 'width: 30%;'}),
            'url': forms.TextInput(attrs={'style': 'width: 70%;'}),
            'status_checks': forms.SelectMultiple(attrs={
                'data-rel': 'chosen',
                'style': 'width: 70%',
            }),
            'instances': forms.SelectMultiple(attrs={
                'data-rel': 'chosen',
                'style': 'width: 70%',
            }),
            'alerts': forms.SelectMultiple(attrs={
                'data-rel': 'chosen',
                'style': 'width: 70%',
            }),
            'users_to_notify': forms.CheckboxSelectMultiple(),
            'schedule': forms.Select(),
            'hackpad_id': forms.TextInput(attrs={'style': 'width:30%;'}),
        }

    def __init__(self, *args, **kwargs):
        ret = super(ServiceForm, self).__init__(*args, **kwargs)
        self.fields['users_to_notify'].queryset = User.objects.filter(
            is_active=True)
        self.fields['schedule'].queryset = Schedule.objects.all()
        return ret

    def clean_hackpad_id(self):
        value = self.cleaned_data['hackpad_id']
        if not value:
            return ''
        for pattern in settings.RECOVERY_SNIPPETS_WHITELIST:
            if re.match(pattern, value):
                return value
        raise ValidationError('Please specify a valid JS snippet link')


class ScheduleForm(forms.ModelForm):

    class Meta:
        model = Schedule
        template_name = 'schedule_form.html'
        fields = (
            'name',
            'ical_url',
        )
        widgets = {
            'name': forms.TextInput(attrs={'style': 'width: 30%;'}),
            'ical_url': forms.TextInput(attrs={'style': 'width: 30%;'}),
        }

    def __init__(self, *args, **kwargs):
        return super(ScheduleForm, self).__init__(*args, **kwargs)


class StatusCheckReportForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        widget=forms.HiddenInput
    )
    checks = forms.ModelMultipleChoiceField(
        queryset=StatusCheck.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'data-rel': 'chosen',
                'style': 'width: 70%',
            },
        )
    )
    date_from = forms.DateField(label='From', widget=forms.DateInput(attrs={'class': 'datepicker'}))
    date_to = forms.DateField(label='To', widget=forms.DateInput(attrs={'class': 'datepicker'}))

    def get_report(self):
        checks = self.cleaned_data['checks']
        now = timezone.now()
        for check in checks:
            # Group results of the check by status (failed alternating with succeeded),
            # take time of the first one in each group (starting from a failed group),
            # split them into pairs and form the list of problems.
            results = check.statuscheckresult_set.filter(
                time__gte=self.cleaned_data['date_from'],
                time__lt=self.cleaned_data['date_to'] + timedelta(days=1)
            ).order_by('time')
            groups = dropwhile(lambda item: item[0], groupby(results, key=lambda r: r.succeeded))
            times = [next(group).time for succeeded, group in groups]
            pairs = izip_longest(*([iter(times)] * 2))
            check.problems = [(start, end, (end or now) - start) for start, end in pairs]
            if results:
                check.success_rate = results.filter(succeeded=True).count() / float(len(results)) * 100
        return checks
