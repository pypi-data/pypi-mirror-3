# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from visits.utils import is_ignored, gen_hash

try:
    from django.utils.timezone import now
except ImportError:
    from datetime.datetime import now


class VisitManager(models.Manager):
    def get_uri_visits_for(self, request, app_model, uri=None):
        if uri:
            return self.filter(
                visitor_hash=gen_hash(request, uri),
                uri=uri,
                ip_address=request.META.get('REMOTE_ADDR',''))
        return self.filter(
                object_app=app_model._meta.app_label,
                object_model=app_model.__class__.__name__,
                uri__regex=r"^.*/{0,}$"
        )
    def get_object_visits_for(self, request, app_model, obj=None):
        if obj:
            visitor_hash = gen_hash(request, obj._meta.app_label, obj.__class__.__name__, obj.id)
            return self.filter(
                    visitor_hash=visitor_hash,
                    object_app=obj._meta.app_label,
                    object_model=obj.__class__.__name__,
                    object_id=obj.id)

        return self.filter(
            object_app=app_model._meta.app_label,
            object_model=app_model.__class__.__name__)
 
    def add_uri_visit(self, request, uri):
        visitor_hash = gen_hash(request, uri)
        visit = self.get_or_create(
                visitor_hash=visitor_hash,
                uri=uri,
                ip_address=request.META.get('REMOTE_ADDR','')
        )

        if len(visit) and not is_ignored(request, visit[0]):
            visit[0].last_visit = now()
            visit[0].visits += 1
            visit[0].save()

    def add_object_visit(self, request, obj):
        visitor_hash = gen_hash(request, obj._meta.app_label, obj.__class__.__name__, obj.id)
        visit = self.get_or_create(
                visitor_hash=visitor_hash,
                object_app=obj._meta.app_label,
                object_model=obj.__class__.__name__,
                object_id=obj.id,
                ip_address=request.META.get('REMOTE_ADDR','')
        )

        if not is_ignored(request, visit[0]):
            visit[0].last_visit = now()
            visit[0].visits += 1
            visit[0].save()

class Visit(models.Model):
    visitor_hash = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    uri = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.IPAddressField(blank=True, null=True, db_index=True)
    last_visit = models.DateTimeField(blank=True, null=True)
    visits = models.IntegerField(default=0)
    object_app = models.CharField(max_length=255)
    object_model = models.CharField(max_length=255)
    object_id = models.CharField(max_length=255)
    blocked = models.BooleanField(default=False)

    objects = VisitManager()

    def __unicode__(self):
        return self.visitor_hash

    class Meta:
        app_label = "visits"
        ordering = ('uri', 'object_model', 'object_id')
        verbose_name = _('visit')
        verbose_name_plural = _('visits')
