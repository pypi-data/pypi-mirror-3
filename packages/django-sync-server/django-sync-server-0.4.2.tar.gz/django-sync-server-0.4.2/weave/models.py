'''
Models.
FIXME: I dropped site framework integration for the sake 
       of simpler debugging. Add it back once API is stable 
       and working. 

Created on 15.03.2010

@license: GNU GPL v3 or above, see LICENSE for more details.
@copyright: 2010 see AUTHORS for more details.
@author: Jens Diemer
@author: FladischerMichael
'''

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

from weave.utils import weave_timestamp


class BaseModel(models.Model):
    modified = models.DateTimeField(auto_now=True, help_text="Time of the last change.")

    class Meta:
        abstract = True


class CollectionManager(CurrentSiteManager):
    def create_or_update(self, user, col_name, timestamp, since=None):
        collection, created = super(CollectionManager, self).get_or_create(
            user=user, name=col_name,
        )

        # See if we have a constraint on the last modified date  
        if since is not None:
            if since < collection.modified:
                raise ValidationError

        collection.modified = timestamp
        collection.save()
        return collection, created


class Collection(BaseModel):
    """
    http://docs.services.mozilla.com/storage/apis-1.1.html
    
    inherited from BaseModel:
        modified -> datetime of the last change
    """
    user = models.ForeignKey(User)
    name = models.CharField(max_length=96)

    site = models.ForeignKey(Site, editable=False, default=settings.SITE_ID)
    on_site = CollectionManager('site')

    def __unicode__(self):
        return u"%r (user: %r, site: %r)" % (self.name, self.user.username, self.site)

    class Meta:
        ordering = ("-modified",)


class WboManager(models.Manager):
    def create_or_update(self, payload_dict, collection, user, timestamp):
        """
        create or update a wbo
        TODO:
            - Check parentid, but how?
            - must wboid + parentid be unique?
        """
        payload = payload_dict['payload']
        payload_size = len(payload)

        wbo, created = Wbo.objects.get_or_create(
            collection=collection,
            user=user,
            wboid=payload_dict['id'],
            defaults={
                'parentid': payload_dict.get('parentid', None),
                'predecessorid': payload_dict.get('predecessorid', None),
                'sortindex': payload_dict.get('sortindex', None),
                'ttl': payload_dict.get('ttl', None),
                'modified': timestamp,
                'payload_size': payload_size,
                'payload': payload,
            }
        )
        if not created:
            wbo.parentid = payload_dict.get("parentid", None)
            wbo.predecessorid = payload_dict.get("predecessorid", None)
            wbo.sortindex = payload_dict.get("sortindex", None)
            wbo.ttl = payload_dict.get("ttl", None)
            wbo.modified = timestamp
            wbo.payload_size = payload_size
            wbo.payload = payload
            wbo.save()

        return wbo, created


class Wbo(BaseModel):
    """
    http://docs.services.mozilla.com/storage/apis-1.1.html
    
    inherited from BaseModel:
        modified -> datetime of the last change
    """
    objects = WboManager()
    collection = models.ForeignKey(Collection, blank=True, null=True)
    user = models.ForeignKey(User)
    wboid = models.CharField(max_length=64,
        help_text="wbo identifying string"
    )
    parentid = models.CharField(max_length=64, blank=True, null=True,
        help_text="wbo parent identifying string"
    )
    predecessorid = models.CharField(max_length=64, blank=True, null=True,
        help_text="wbo predecessorid"
    )
    sortindex = models.IntegerField(blank=True, null=True,
        help_text="An integer indicting the relative importance of this item in the collection."
    )
    payload = models.TextField(blank=True,
        help_text=(
            "A string containing a JSON structure encapsulating the data of the record."
            " This structure is defined separately for each WBO type. Parts of the"
            " structure may be encrypted, in which case the structure should also"
            " specify a record for decryption."
        )
    )
    payload_size = models.PositiveIntegerField(help_text="Size of the payload.")
    ttl = models.IntegerField(blank=True, null=True,
        help_text=(
            "The number of seconds to keep this record."
            " After that time, this item will not be returned."
        )
    )

    def clean(self):
        # Don't allow draft entries to have a pub_date.
        if self.ttl is not None:
            if self.ttl < 0 or self.ttl > 31536000:
                # from https://hg.mozilla.org/services/server-storage/file/830a414aaed7/syncstorage/wbo.py#l80
                raise ValidationError('TTL %r out of range.' % self.ttl)

    def save(self, *args, **kwarg):
        self.full_clean()
        super(Wbo, self).save(*args, **kwarg)

    def get_response_dict(self):
        response_dict = {
            "id": self.wboid,
            "modified": weave_timestamp(self.modified),
            "payload": self.payload,
        }
        # Don't send additional properties if payload is emtpy -> deleted Wbo
        if self.payload != '':
            for key in ("parentid", "predecessorid", "sortindex"):
                value = getattr(self, key)
                if value:
                    response_dict[key] = value
        return response_dict

    def __unicode__(self):
        return u"%r (%r)" % (self.wboid, self.collection)

    class Meta:
        ordering = ("-modified",)
