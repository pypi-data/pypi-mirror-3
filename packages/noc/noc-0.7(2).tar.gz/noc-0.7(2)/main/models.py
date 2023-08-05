# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Database models for main module
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python Modules
from __future__ import with_statement
import os
import datetime
import re
import threading
import types
## Django Modules
from django.utils.translation import ugettext_lazy as _
from django.db import models, connection
from django.contrib.auth.models import User, Group
from django.core.validators import MaxLengthValidator
from django.contrib import databrowse
from django.db.models.signals import class_prepared, pre_save, pre_delete,\
                                     post_save, post_delete
from django.template import Template as DjangoTemplate
from django.template import Context
## Third-party modules
from tagging.models import Tag
## NOC Modules
from noc import settings
from noc.lib.fields import BinaryField
from noc.lib.database_storage import DatabaseStorage as DBS
from noc.main.refbooks.downloaders import downloader_registry
from noc.lib.fields import TextArrayField, PickledField, ColorField, CIDRField
from noc.lib.middleware import get_user
from noc.lib.timepattern import TimePattern as TP
from noc.lib.timepattern import TimePatternList
from noc.sa.interfaces.base import interface_registry
from noc.lib.periodic import periodic_registry
from noc.lib.app.site import site
from noc.lib.ip import IP
from noc.lib.validators import check_extension, check_mimetype
## Register periodics
periodic_registry.register_all()
##
## A hash of Model.search classmethods.
## Populated by "class_prepared" signal listener
## Model.search is a generator taking parameters (user,query,limit)
## And yielding a SearchResults (ordered by relevancy)
##
search_methods = set()


def on_new_model(sender, **kwargs):
    """
    Register new search handler if model has .search() classmethod
    """
    if hasattr(sender, "search"):
        search_methods.add(getattr(sender, "search"))
    databrowse.site.register(sender)
##
## Attach to the 'class_prepared' signal
## and on_new_model on every new model
##
class_prepared.connect(on_new_model)
##
## Exclude tables from audit
##
AUDIT_TRAIL_EXCLUDE = set([
    "django_admin_log",
    "django_session",
    "auth_message",
    "main_audittrail",
    "kb_kbentryhistory",
    "kb_kbentrypreviewlog",
    "fm_eventlog",
    "sa_maptask",
    "sa_reducetask",
])


def audit_trail_save(sender, instance, **kwargs):
    """
    Audit trail for INSERT and UPDATE operations
    """
    # Exclude tables
    if sender._meta.db_table in AUDIT_TRAIL_EXCLUDE:
        return
    #
    if instance.id:
        # Update
        try:
            old = sender.objects.get(id=instance.id)
        except sender.DoesNotExist:
            # Protection for correct test fixtures loading
            return
        message = []
        operation = "M"
        for f in sender._meta.fields:
            od = f.value_to_string(old)
            nd = f.value_to_string(instance)
            if f.name == "id":
                message += ["id: %s" % nd]
            elif nd != od:
                message += ["%s: '%s' -> '%s'" % (f.name, od, nd)]
        message = "\n".join(message)
    else:
        # New record
        operation = "C"
        message = "\n".join(["%s = %s" % (f.name, f.value_to_string(instance))
                             for f in sender._meta.fields])
    AuditTrail.log(sender, instance, operation, message)


def audit_trail_delete(sender, instance, **kwargs):
    """
    Audit trail for DELETE operation
    """
    # Exclude tables
    if sender._meta.db_table in AUDIT_TRAIL_EXCLUDE:
        return
    #
    operation = "D"
    message = "\n".join(["%s = %s" % (f.name, f.value_to_string(instance))
                         for f in sender._meta.fields])
    AuditTrail.log(sender, instance, operation, message)

##
## Set up audit trail handlers
##
if settings.IS_WEB:
    pre_save.connect(audit_trail_save)
    pre_delete.connect(audit_trail_delete)
##
## Initialize download registry
##
downloader_registry.register_all()


class AuditTrail(models.Model):
    """
    Audit Trail
    """
    class Meta:
        verbose_name = "Audit Trail"
        verbose_name_plural = "Audit Trail"
        ordering = ["-timestamp"]
    user = models.ForeignKey(User, verbose_name="User")
    timestamp = models.DateTimeField("Timestamp", auto_now=True)
    model = models.CharField("Model", max_length=128)
    db_table = models.CharField("Table", max_length=128)
    operation = models.CharField("Operation", max_length=1,
                                 choices=[("C", "Create"), ("M", "Modify"),
                                          ("D", "Delete")])
    subject = models.CharField("Subject", max_length=256)
    body = models.TextField("Body")

    @classmethod
    def log(cls, sender, instance, operation, message):
        """
        Log into audit trail
        """
        user = get_user()  # Retrieve user from thread local storage
        if not user or not user.is_authenticated():
            return  # No user initialized, no audit trail
        subject = unicode(instance)
        if len(subject) > 127:
            # Narrow subject
            subject = subject[:62] + " .. " + subject[-62:]
        AuditTrail(
            user=user,
            model=sender.__name__,
            db_table=sender._meta.db_table,
            operation=operation,
            subject=subject,
            body=message
        ).save()


class Permission(models.Model):
    """
    Permissions.

    Populated by manage.py sync-perm
    @todo: Check name format
    """
    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"

    name = models.CharField("Name", max_length=128, unique=True)  # module:app:permission
    implied = models.CharField("Implied", max_length=256, null=True, blank=True)  # comma-separated
    users = models.ManyToManyField(User, related_name="noc_user_permissions")
    groups = models.ManyToManyField(Group, related_name="noc_group_permissions")

    def __unicode__(self):
        return self.name

    def get_implied_permissions(self):
        if not self.implied:
            return []
        return [Permission.objects.get(name=p.strip())
                for p in self.implied.split(",")]

    @classmethod
    def has_perm(self, user, perm):
        """
        Check user has permission either directly either via groups
        """
        if not user.is_active:
            return False
        if user.is_superuser:
            return True
        try:
            p = Permission.objects.get(name=perm)
        except Permission.DoesNotExist:
            return False  # Permission not found
        return (p.users.filter(id=user.id).exists() or
                p.groups.filter(id__in=user.groups.all()).exists())

    @classmethod
    def get_user_permissions(cls, user):
        """
        Return a set of user permissions
        """
        return set(user.noc_user_permissions.values_list("name", flat=True))

    @classmethod
    def set_user_permissions(cls, user, perms):
        """
        Set user permissions

        :param user: User
        :type user: User
        :param perms: Set of new permissions
        :type perms: Set
        """
        # Add implied permissions
        perms = set(perms)  # Copy
        for p in cls.objects.filter(name__in=list(perms), implied__isnull=False):
            perms.update([x.strip() for x in p.implied.split(",")])
        #
        current = cls.get_user_permissions(user)
        # Add new permissions
        for p in perms - current:
            try:
                Permission.objects.get(name=p).users.add(user)
            except Permission.DoesNotExist:
                raise Permission.DoesNotExist("Permission '%s' does not exist" % p)
        # Revoke permission
        for p in current - perms:
            Permission.objects.get(name=p).users.remove(user)

    @classmethod
    def get_group_permissions(cls, group):
        """
        Get set of group permissions
        """
        return set(group.noc_group_permissions.values_list("name", flat=True))

    @classmethod
    def set_group_permissions(cls, group, perms):
        """
        Set group permissions

        :param group: Group
        :type group: Group
        :param perms: Set of permissions
        :type perms: Set
        """
        # Add implied permissions
        perms = set(perms)  # Copy
        for p in cls.objects.filter(name__in=list(perms), implied__isnull=False):
            perms.update([x.strip() for x in p.implied.split(",")])
        #
        current = cls.get_group_permissions(group)
        # Add new permissions
        for p in perms - current:
            Permission.objects.get(name=p).groups.add(group)
        # Revoke permissions
        for p in current - perms:
            Permission.objects.get(name=p).groups.remove(group)


class Style(models.Model):
    """
    CSS Style
    """
    class Meta:
        verbose_name = "Style"
        verbose_name_plural = "Styles"
        ordering = ["name"]

    name = models.CharField("Name", max_length=64, unique=True)
    font_color = ColorField("Font Color", default=0)
    background_color = ColorField("Background Color", default=0xffffff)
    bold = models.BooleanField("Bold", default=False)
    italic = models.BooleanField("Italic", default=False)
    underlined = models.BooleanField("Underlined", default=False)
    is_active = models.BooleanField("Is Active", default=True)
    description = models.TextField("Description", null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def css_class_name(self):
        """
        CSS Class Name
        """
        return u"noc-color-%d" % self.id

    @property
    def style(self):
        """
        CSS Style
        """
        s = u"color: %s; background-color: %s;" % (self.font_color,
                                                   self.background_color)
        if self.bold:
            s += u" font-weight: bold;"
        if self.italic:
            s += u" font-style: italic;"
        if self.underlined:
            s += u" text-decoration: underline;"
        return s

    @property
    def css(self):
        """
        CSS class style
        """
        return u".%s { %s }\n" % (self.css_class_name, self.style)


class Language(models.Model):
    """
    Language
    """
    class Meta:
        verbose_name = "Language"
        verbose_name_plural = "Languages"
        ordering = ["name"]

    name = models.CharField("Name", max_length=32, unique=True)
    native_name = models.CharField("Native Name", max_length=32)
    is_active = models.BooleanField("Is Active", default=False)

    def __unicode__(self):
        return self.name


class DatabaseStorage(models.Model):
    """
    Database Storage
    """
    class Meta:
        verbose_name = "Database Storage"
        verbose_name_plural = "Database Storage"

    name = models.CharField("Name", max_length=256, unique=True)
    data = BinaryField("Data")
    size = models.IntegerField("Size")
    mtime = models.DateTimeField("MTime")

    ##
    ## Options for DatabaseStorage
    ##
    @classmethod
    def dbs_options(cls):
        return {
            "db_table": DatabaseStorage._meta.db_table,
            "name_field": "name",
            "data_field": "data",
            "mtime_field": "mtime",
            "size_field": "size",
        }

    @classmethod
    def get_dbs(cls):
        """
        Get DatabaseStorage instance
        """
        return DBS(cls.dbs_options())
##
## Default database storage
##
database_storage = DatabaseStorage.get_dbs()


class MIMEType(models.Model):
    """
    MIME Type mapping
    """
    class Meta:
        verbose_name = "MIME Type"
        verbose_name_plural = "MIME Types"
        ordering = ["extension"]

    extension = models.CharField("Extension", max_length=32, unique=True,
                                 validators=[check_extension])
    mime_type = models.CharField("MIME Type", max_length=63,
                                 validators=[check_mimetype])

    def __unicode__(self):
        return u"%s -> %s" % (self.extension, self.mime_type)

    @classmethod
    def get_mime_type(cls, filename):
        """
        Determine MIME type from filename
        """
        r, ext = os.path.splitext(filename)
        try:
            m = MIMEType.objects.get(extension=ext)
            return m.mime_type
        except MIMEType.DoesNotExist:
            return "application/octet-stream"


class NoPyRuleException(Exception):
    pass

rx_coding = re.compile(r"^#\s*-\*-\s*coding:\s*\S+\s*-\*-\s*$", re.MULTILINE)


class PyRule(models.Model):
    class Meta:
        verbose_name = "pyRule"
        verbose_name_plural = "pyRules"
        ordering = ["name"]

    name = models.CharField("Name", max_length=64, unique=True)
    interface = models.CharField("Interface", max_length=64,
            choices=[(i, i) for i in sorted(interface_registry)])
    description = models.TextField("Description")
    text = models.TextField("Text")
    is_builtin = models.BooleanField("Is Builtin", default=False)
    changed = models.DateTimeField("Changed", auto_now=True, auto_now_add=True)
    # Compiled pyRules cache
    compiled_pyrules = {}
    compiled_changed = {}
    compiled_lock = threading.Lock()
    NoPyRule = NoPyRuleException

    alters_data = True   # Tell Django's template engine to not call PyRule

    # Use special filter for interface
    interface.existing_choices_filter = True

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        """
        Check syntax and save
        """
        self.compile_text(unicode(self.text))
        super(PyRule, self).save(**kwargs)

    @property
    def interface_class(self):
        """
        Get interface class
        """
        return interface_registry[self.interface]

    @classmethod
    def compile_text(self, text):
        """
        Compile pyRule
        """
        # Built-in pyRule decorator
        def pyrule(f):
            f.is_pyrule = True
            return f

        # Inject @pyrule decorator into namespace
        d = {"pyrule": pyrule}
        # Remove coding declarations and \r
        text = rx_coding.sub("", text.replace("\r\n", "\n"))
        # Compile text
        exec text in d
        # Find marked pyrule
        rules = [r for r in d.values()
                 if hasattr(r, "is_pyrule") and r.is_pyrule]
        if len(rules) < 1:
            raise SyntaxError("No @pyrule decorated symbol found")
        if len(rules) != 1:
            raise SyntaxError("More than one @pyrule deorated symbols found")
        rule = rules[0]
        if not callable(rule):
            raise SyntaxError("Rule is not callable")
        return rule

    ##
    ## Call pyRule
    ##
    def __call__(self, **kwargs):
        t = datetime.datetime.now()
        # Try to get compiled rule from cache
        with self.compiled_lock:
            requires_recompile = (self.name not in self.compiled_changed or
                                  self.compiled_changed[self.name] < self.changed)
            if not requires_recompile:
                f = self.compiled_pyrules[self.name]
        # Recompile rule and place in cache when necessary
        if requires_recompile:
            f = self.compile_text(str(self.text))
            with self.compiled_lock:
                self.compiled_pyrules[self.name] = f
                self.compiled_changed[self.name] = t
        # Check interface
        i = self.interface_class()
        kwargs = i.clean(**kwargs)
        # Evaluate pyRule
        result = f(**kwargs)
        # Check and result
        return i.clean_result(result)

    @classmethod
    def call(cls, py_rule_name, **kwargs):
        """
        Call pyRule by name
        """
        try:
            rule = PyRule.objects.get(name=py_rule_name)
        except PyRule.DoesNotExist:
            raise cls.NoPyRule
        return rule(**kwargs)

##
## Search patters
##
rx_mac_3_octets = re.compile("^([0-9A-F]{6}|[0-9A-F]{12})$", re.IGNORECASE)


class RefBook(models.Model):
    """
    Reference Books
    """
    class Meta:
        verbose_name = "Ref Book"
        verbose_name_plural = "Ref Books"

    name = models.CharField("Name", max_length=128, unique=True)
    language = models.ForeignKey(Language, verbose_name="Language")
    description = models.TextField("Description", blank=True, null=True)
    is_enabled = models.BooleanField("Is Enabled", default=False)
    is_builtin = models.BooleanField("Is Builtin", default=False)
    downloader = models.CharField("Downloader", max_length=64,
            choices=downloader_registry.choices, blank=True, null=True)
    download_url = models.CharField("Download URL",
            max_length=256, null=True, blank=True)
    last_updated = models.DateTimeField("Last Updated", blank=True, null=True)
    next_update = models.DateTimeField("Next Update", blank=True, null=True)
    refresh_interval = models.IntegerField("Refresh Interval (days)", default=0)

    def __unicode__(self):
        return self.name

    def add_record(self, data):
        """
        Add new record
        :param data: Hash of field name -> value
        :type data: Dict
        """
        fields = {}
        for f in self.refbookfield_set.all():
            fields[f.name] = f.order - 1
        r = [None for f in range(len(fields))]
        for k, v in data.items():
            r[fields[k]] = v
        RefBookData(ref_book=self, value=r).save()

    def flush_refbook(self):
        """
        Delete all records in ref. book
        """
        RefBookData.objects.filter(ref_book=self).delete()

    def bulk_upload(self, data):
        """
        Bulk upload data to ref. book

        :param data: List of hashes field name -> value
        :type data: List
        """
        fields = {}
        for f in self.refbookfield_set.all():
            fields[f.name] = f.order - 1
        # Prepare empty row template
        row_template = [None for f in range(len(fields))]
        # Insert data
        for r in data:
            row = row_template[:]  # Clone template row
            for k, v in r.items():
                if k in fields:
                    row[fields[k]] = v
            RefBookData(ref_book=self, value=row).save()

    def download(self):
        """
        Download refbook
        """
        if self.downloader and self.downloader in downloader_registry.classes:
            downloader = downloader_registry[self.downloader]
            data = downloader.download(self)
            if data:
                self.flush_refbook()
                self.bulk_upload(data)
                self.last_updated = datetime.datetime.now()
                self.next_update = self.last_updated + datetime.timedelta(days=self.refresh_interval)
                self.save()

    @classmethod
    def search(cls, user, search, limit):
        """
        Search engine plugin
        """
        from noc.lib.search import SearchResult  # Must be inside method to prevent import loops

        for b in RefBook.objects.filter(is_enabled=True):
            field_names = [f.name for f in b.refbookfield_set.order_by("order")]
            for f in b.refbookfield_set.filter(search_method__isnull=False):
                x = f.get_extra(search)
                if not x:
                    continue
                q = RefBookData.objects.filter(ref_book=b).extra(**x)
                for r in q:
                    text = "\n".join(["%s = %s" % (k, v)
                                      for k, v in zip(field_names, r.value)])
                    yield SearchResult(
                        url=("main:refbook:item", b.id, r.id),
                        title=u"Reference Book: %s, column %s" % (b.name, f.name),
                        text=text,
                        relevancy=1.0,
                    )

    @property
    def can_search(self):
        """
        Check refbook has at least one searchable field
        """
        return self.refbookfield_set.filter(search_method__isnull=False).exists()

    @property
    def fields(self):
        """
        Get fields names sorted by order
        """
        return self.refbookfield_set.order_by("order")


class RefBookField(models.Model):
    """
    Refbook fields
    """
    class Meta:
        verbose_name = "Ref Book Field"
        verbose_name_plural = "Ref Book Fields"
        unique_together = [("ref_book", "order"), ("ref_book", "name")]
        ordering = ["ref_book", "order"]

    ref_book = models.ForeignKey(RefBook, verbose_name="Ref Book")
    name = models.CharField("Name", max_length="64")
    order = models.IntegerField("Order")
    is_required = models.BooleanField("Is Required", default=True)
    description = models.TextField("Description", blank=True, null=True)
    search_method = models.CharField("Search Method", max_length=64,
            blank=True, null=True,
            choices=[
                ("string", "string"),
                ("substring", "substring"),
                ("starting", "starting"),
                ("mac_3_octets_upper", "3 Octets of the MAC")])

    def __unicode__(self):
        return u"%s: %s" % (self.ref_book, self.name)

    # Return **kwargs for extra
    def get_extra(self, search):
        if self.search_method:
            return getattr(self, "search_%s" % self.search_method)(search)
        else:
            return {}

    def search_string(self, search):
        """
        string search method
        """
        return {
            "where": ["value[%d] ILIKE %%s" % self.order],
            "params": [search]
        }

    def search_substring(self, search):
        """
        substring search method
        """
        return {
            "where": ["value[%d] ILIKE %%s" % self.order],
            "params": ["%" + search + "%"]
        }

    def search_starting(self, search):
        """
        starting search method
        """
        return {
            "where": ["value[%d] ILIKE %%s" % self.order],
            "params": [search + "%"]
        }

    def search_mac_3_octets_upper(self, search):
        """
        Match 3 first octets of the MAC address
        """
        mac = search.replace(":", "").replace("-", "").replace(".", "")
        if not rx_mac_3_octets.match(mac):
            return {}
        return {
            "where": ["value[%d]=%%s" % self.order],
            "params": [mac]
        }


class RBDManader(models.Manager):
    """
    Ref Book Data Manager
    """
    # Order by first field
    def get_query_set(self):
        return super(RBDManader, self).get_query_set().extra(order_by=["main_refbookdata.value[1]"])


class RefBookData(models.Model):
    """
    Ref. Book Data
    """
    class Meta:
        verbose_name = "Ref Book Data"
        verbose_name_plural = "Ref Book Data"

    ref_book = models.ForeignKey(RefBook, verbose_name="Ref Book")
    value = TextArrayField("Value")

    objects = RBDManader()

    def __unicode__(self):
        return u"%s: %s" % (self.ref_book, self.value)

    @property
    def items(self):
        """
        Returns list of pairs (field,data)
        """
        return zip(self.ref_book.fields, self.value)


class TimePattern(models.Model):
    """
    Time Patterns
    """
    class Meta:
        verbose_name = "Time Pattern"
        verbose_name_plural = "Time Patterns"

    name = models.CharField("Name", max_length=64, unique=True)
    description = models.TextField("Description", null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def time_pattern(self):
        """
        Returns associated Time Pattern object
        """
        return TP([t.term for t in self.timepatternterm_set.all()])

    def match(self, d):
        """
        Matches DateTime objects against time pattern
        """
        return self.time_pattern.match(d)


class TimePatternTerm(models.Model):
    """
    Time pattern terms
    """
    class Meta:
        verbose_name = "Time Pattern Term"
        verbose_name_plural = "Time Pattern Terms"
        unique_together = [("time_pattern", "term")]

    time_pattern = models.ForeignKey(TimePattern, verbose_name="Time Pattern")
    term = models.CharField("Term", max_length=256)

    def __unicode__(self):
        return u"%s: %s" % (self.time_pattern.name, self.term)

    @classmethod
    def check_syntax(cls, term):
        """
        Checks Time Pattern syntax. Raises SyntaxError in case of error
        """
        TP(term)

    def save(self, *args):
        """
        Check syntax before save
        """
        TimePatternTerm.check_syntax(self.term)
        super(TimePatternTerm, self).save(*args)


class NotificationGroup(models.Model):
    """
    Notification Groups
    """
    class Meta:
        verbose_name = "Notification Group"
        verbose_name_plural = "Notification Groups"
        ordering = [("name")]
    name = models.CharField("Name", max_length=64, unique=True)
    description = models.TextField("Description", null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def members(self):
        """
        List of (time pattern, method, params, language)
        """
        default_language = settings.LANGUAGE_CODE
        m = []
        # Collect user notifications
        for ngu in self.notificationgroupuser_set.filter(user__is_active=True):
            lang = default_language
            try:
                profile = ngu.user.get_profile()
                if profile.preferred_language:
                    lang = profile.preferred_language
            except:
                continue
            for tp, method, params in profile.contacts:
                m += [(TimePatternList([ngu.time_pattern, tp]),
                       method, params, lang)]
        # Collect other notifications
        for ngo in self.notificationgroupother_set.all():
            if ngo.notification_method == "mail" and "," in ngo.params:
                for y in ngo.params.split(","):
                    m += [(ngo.time_pattern, ngo.notification_method,
                           y.strip(), default_language)]
            else:
                m += [(ngo.time_pattern, ngo.notification_method,
                       ngo.params, default_language)]
        return m

    @property
    def active_members(self):
        """
        List of currently active members: (method, param, language)
        """
        now = datetime.datetime.now()
        return set([(method, param, lang) for tp, method, param, lang
            in self.members if tp.match(now)])

    @property
    def languages(self):
        """
        List of preferred languages for users
        """
        return set([x[3] for x in self.members])

    @classmethod
    def get_effective_message(cls, messages, lang):
        for cl in (lang, settings.LANGUAGE_CODE, "en"):
            if cl in messages:
                return messages[cl]
        return "Cannot translate message"

    def notify(self, subject, body, link=None):
        """
        Send message to active members
        """
        if type(subject) != types.DictType:
            subject = {settings.LANGUAGE_CODE: subject}
        if type(body) != types.DictType:
            body = {settings.LANGUAGE_CODE: body}
        for method, params, lang in self.active_members:
            Notification(
                notification_method=method,
                notification_params=params,
                subject=self.get_effective_message(subject, lang),
                body=self.get_effective_message(body, lang),
                link=link
            ).save()

    @classmethod
    def group_notify(cls, groups, subject, body, link=None):
        """
        Send notification to a list of groups
        Prevent duplicated messages
        """
        if type(subject) != types.DictType:
            subject = {settings.LANGUAGE_CODE: subject}
        if type(body) != types.DictType:
            body = {settings.LANGUAGE_CODE: body}
        ngs = set()
        lang = {}  # (method, params) -> lang
        for g in groups:
            for method, params, l in g.active_members:
                ngs.add((method, params))
                lang[(method, params)] = l
        for method, params in ngs:
            l = lang[(method, params)]
            Notification(
                notification_method=method,
                notification_params=params,
                subject=cls.get_effective_message(subject, l),
                body=cls.get_effective_message(body, l),
                link=link
            ).save()


##
## Users in Notification Groups
##
class NotificationGroupUser(models.Model):
    class Meta:
        verbose_name = "Notification Group User"
        verbose_name_plural = "Notification Group Users"
        unique_together = [("notification_group", "time_pattern", "user")]

    notification_group = models.ForeignKey(NotificationGroup,
                                           verbose_name="Notification Group")
    time_pattern = models.ForeignKey(TimePattern, verbose_name="Time Pattern")
    user = models.ForeignKey(User, verbose_name="User")

    def __unicode__(self):
        return u"%s: %s: %s" % (self.notification_group.name,
                                self.time_pattern.name, self.user.username)

##
## Other Notification Group Items
##
NOTIFICATION_METHOD_CHOICES = [("mail", "Email"), ("file", "File")]
USER_NOTIFICATION_METHOD_CHOICES = [("mail", "Email")]


class NotificationGroupOther(models.Model):
    class Meta:
        verbose_name = "Notification Group Other"
        verbose_name_plural = "Notification Group Others"
        unique_together = [("notification_group", "time_pattern",
                            "notification_method", "params")]

    notification_group = models.ForeignKey(NotificationGroup,
                                           verbose_name="Notification Group")
    time_pattern = models.ForeignKey(TimePattern, verbose_name="Time Pattern")
    notification_method = models.CharField("Method", max_length=16,
                                           choices=NOTIFICATION_METHOD_CHOICES)
    params = models.CharField("Params", max_length=256)

    def __unicode__(self):
        return u"%s: %s: %s: %s" % (self.notification_group.name,
                                    self.time_pattern.name,
                                    self.notification_method, self.params)


class Notification(models.Model):
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    timestamp = models.DateTimeField("Timestamp", auto_now=True,
                                     auto_now_add=True)
    notification_method = models.CharField("Method", max_length=16,
                                           choices=NOTIFICATION_METHOD_CHOICES)
    notification_params = models.CharField("Params", max_length=256)
    subject = models.CharField("Subject", max_length=256)
    body = models.TextField("Body")
    link = models.CharField("Link", max_length=256, null=True, blank=True)
    next_try = models.DateTimeField("Next Try", null=True, blank=True)
    actual_till = models.DateTimeField("Actual Till", null=True, blank=True)

    def __unicode__(self):
        return self.subject


class SystemNotification(models.Model):
    """
    System Notifications
    """
    class Meta:
        verbose_name = "System Notification"
        verbose_name_plural = "System Notifications"

    name = models.CharField("Name", max_length=64, unique=True)
    notification_group = models.ForeignKey(NotificationGroup,
                                           verbose_name="Notification Group",
                                           null=True, blank=True)

    def __unicode__(self):
        return self.name

    @classmethod
    def notify(cls, name, subject, body, link=None):
        try:
            sn = SystemNotification.objects.get(name=name)
        except SystemNotification.DoesNotExist:  # Ignore undefined notifications
            return
        if sn.notification_group:
            sn.notification_group.notify(subject=subject, body=body, link=link)


class UserProfileManager(models.Manager):
    """
    @todo: remove
    User Profile Manager
    Leave only current user's profile
    """
    def get_query_set(self):
        user = get_user()
        if user:
            # Create profile when necessary
            try:
                p = super(UserProfileManager, self).get_query_set().get(user=user)
            except UserProfile.DoesNotExist:
                UserProfile(user=user).save()
            return super(UserProfileManager, self).get_query_set().filter(user=user)
        else:
            return super(UserProfileManager, self).get_query_set()


class UserProfile(models.Model):
    """
    User profile
    """
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    user = models.ForeignKey(User, unique=True)
    # User data
    preferred_language = models.CharField("Preferred Language", max_length=16,
                                          null=True, blank=True,
                                          default=settings.LANGUAGE_CODE,
                                          choices=settings.LANGUAGES)
    theme = models.CharField("Theme", max_length=32, null=True, blank=True)
    #
    objects = UserProfileManager()

    def __unicode__(self):
        return "%s's Profile" % self.user.username

    def save(self, **kwargs):
        user = get_user()
        if user and self.user != user:
            raise Exception("Invalid user")
        super(UserProfile, self).save(**kwargs)

    @property
    def contacts(self):
        return [(c.time_pattern, c.notification_method, c.params)
            for c in self.userprofilecontact_set.all()]

    @property
    def active_contacts(self):
        """
        Get list of currently active contacts

        :returns: List of (method, params)
        """
        now = datetime.datetime.now()
        return [(c.notification_method, c.params)
            for c in self.contacts if c.time_pattern.match(now)]


class UserProfileContact(models.Model):
    class Meta:
        verbose_name = "User Profile Contact"
        verbose_name_plural = "User Profile Contacts"
        unique_together = [("user_profile", "time_pattern",
                            "notification_method", "params")]
    user_profile = models.ForeignKey(UserProfile, verbose_name="User Profile")
    time_pattern = models.ForeignKey(TimePattern, verbose_name="Time Pattern")
    notification_method = models.CharField("Method", max_length=16,
                                    choices=USER_NOTIFICATION_METHOD_CHOICES)
    params = models.CharField("Params", max_length=256)


##
## Triggers
##
def model_choices():
    for m in models.get_models():
        yield (m._meta.db_table, m._meta.db_table)


class DBTrigger(models.Model):
    class Meta:
        verbose_name = "Database Trigger"
        verbose_name_plural = "Database Triggers"
        ordering = ("model", "order")

    name = models.CharField("Name", max_length=64, unique=True)
    model = models.CharField("Model", max_length=128, choices=model_choices())
    is_active = models.BooleanField("Is Active", default=True)
    order = models.IntegerField("Order", default=100)
    description = models.TextField("Description", null=True, blank=True)
    pre_save_rule = models.ForeignKey(PyRule,
            verbose_name="Pre-Save Rule",
            related_name="dbtrigger_presave_set",
            limit_choices_to={"interface": "IDBPreSave"},
            blank=True, null=True)
    post_save_rule = models.ForeignKey(PyRule,
            verbose_name="Post-Save Rule",
            related_name="dbtrigger_postsave_set",
            limit_choices_to={"interface": "IDBPostSave"},
            blank=True, null=True)
    pre_delete_rule = models.ForeignKey(PyRule,
            verbose_name="Pre-Delete Rule",
            related_name="dbtrigger_predelete_set",
            limit_choices_to={"interface": "IDBPreDelete"},
            blank=True, null=True)
    post_delete_rule = models.ForeignKey(PyRule,
            verbose_name="Post-Delete Rule",
            related_name="dbtrigger_postdelete_set",
            limit_choices_to={"interface": "IDBPostDelete"},
            blank=True, null=True)
    ## State cache
    _pre_save_triggers = {}     # model.meta.db_table -> [rules]
    _post_save_triggers = {}    # model.meta.db_table -> [rules]
    _pre_delete_triggers = {}   # model.meta.db_table -> [rules]
    _post_delete_triggers = {}  # model.meta.db_table -> [rules]

    def __unicode__(self):
        return u"%s: %s" % (self.model, self.name)

    ##
    ## Refresh triggers cache
    ##
    @classmethod
    def refresh_cache(cls, *args, **kwargs):
        # Clear cache
        cls._pre_save_triggers = {}
        cls._post_save_triggers = {}
        cls._pre_delete_triggers = {}
        cls._post_delete_triggers = {}
        # Add all active triggers
        for t in cls.objects.filter(is_active=True).order_by("order"):
            for r in ["pre_save", "post_save", "pre_delete", "post_delete"]:
                c = getattr(cls, "_%s_triggers" % r)
                rule = getattr(t, "%s_rule" % r)
                if rule:
                    try:
                        c[t.model] += [rule]
                    except KeyError:
                        c[t.model] = [rule]

    ##
    ## Dispatcher for pre-save
    ##
    @classmethod
    def pre_save_dispatch(cls, **kwargs):
        m = kwargs["sender"]._meta.db_table
        if m in cls._pre_save_triggers:
            for t in cls._pre_save_triggers[m]:
                t(model=kwargs["sender"], instance=kwargs["instance"])

    ##
    ## Dispatcher for post-save
    ##
    @classmethod
    def post_save_dispatch(cls, **kwargs):
        m = kwargs["sender"]._meta.db_table
        if m in cls._post_save_triggers:
            for t in cls._post_save_triggers[m]:
                t(model=kwargs["sender"], instance=kwargs["instance"],
                  created=kwargs["created"])

    ##
    ## Dispatcher for pre-delete
    ##
    @classmethod
    def pre_delete_dispatch(cls, **kwargs):
        m = kwargs["sender"]._meta.db_table
        if m in cls._pre_delete_triggers:
            for t in cls._pre_delete_triggers[m]:
                t(model=kwargs["sender"], instance=kwargs["instance"])

    ##
    ## Dispatcher for post-delete
    ##
    @classmethod
    def post_delete_dispatch(cls, **kwargs):
        m = kwargs["sender"]._meta.db_table
        if m in cls._post_delete_triggers:
            for t in cls._post_delete_triggers[m]:
                t(model=kwargs["sender"], instance=kwargs["instance"])

    ##
    ## Called when all models are initialized
    ##
    @classmethod
    def x(cls):
        f = self._meta.get_field_by_name("model")[0]
        f.choices = [(m._meta.db_table, m._meta.db_table)
            for m in models.get_models()]


class Schedule(models.Model):
    class Meta:
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")
        ordering = ["periodic_name"]

    periodic_name = models.CharField(_("Periodic Task"), max_length=64)
    is_enabled = models.BooleanField(_("Enabled?"), default=False)
    time_pattern = models.ForeignKey(TimePattern,
                                     verbose_name=_("Time Pattern"))
    run_every = models.PositiveIntegerField(_("Run Every (secs)"),
                                     default=86400)
    timeout = models.PositiveIntegerField(_("Timeout (secs)"),
                                     null=True, blank=True)
    last_run = models.DateTimeField(_("Last Run"), blank=True, null=True)
    last_status = models.BooleanField(_("Last Status"), default=True)

    def __unicode__(self):
        return u"%s:%s" % (self.periodic_name, self.time_pattern.name)

    @property
    def periodic(self):
        return periodic_registry[self.periodic_name]

    def mark_run(self, start_time, status):
        """Set last run"""
        self.last_run = start_time
        self.last_status = status
        self.save()

    @classmethod
    def get_tasks(cls):
        """Get tasks required to run"""
        now = datetime.datetime.now()
        return [s for s in Schedule.objects.filter(is_enabled=True)
                if (s.time_pattern.match(now) and
                   (s.last_run is None or
                    s.last_run + datetime.timedelta(seconds=s.run_every) <= now))]

    @classmethod
    def reschedule(cls, name, days=0, minutes=0, seconds=0):
        """Reschedule tasks with name to launch immediately"""
        t = Schedule.objects.filter(periodic_name=name)[0]
        t.last_run = (datetime.datetime.now() -
                      datetime.timedelta(days=days, minutes=minutes,
                                         seconds=seconds))
        t.save()


class Shard(models.Model):
    class Meta:
        verbose_name = _("Shard")
        verbose_name_plural = _("Shards")
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=128, unique=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    description = models.TextField(_("Description"), null=True, blank=True)

    def __unicode__(self):
        return self.name


class PrefixTable(models.Model):
    class Meta:
        verbose_name = _("Prefix Table")
        verbose_name_plural = _("Prefix Tables")
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=128, unique=True)
    description = models.TextField(_("Description"), null=True, blank=True)

    def __unicode__(self):
        return self.name

    def match(self, prefix):
        """
        Check the prefix is inside Prefix Table

        :param prefix: Prefix
        :type prefix: Str
        :rtype: Bool
        """
        p = IP.prefix(prefix)
        c = connection.cursor()
        c.execute("""
            SELECT COUNT(*)
            FROM  main_prefixtableprefix
            WHERE table_id = %s
              AND afi = %s
              AND %s <<= prefix
        """, [self.id, p.afi, prefix])
        return c.fetchall()[0][0] > 0

    def __contains__(self, other):
        """
        Usage:
        "prefix" in table
        """
        return self.match(other)


class PrefixTablePrefix(models.Model):
    class Meta:
        verbose_name = _("Prefix")
        verbose_name_plural = _("Prefixes")
        unique_together = [("table", "afi", "prefix")]
        ordering = ["table", "afi", "prefix"]

    table = models.ForeignKey(PrefixTable, verbose_name=_("Prefix Table"))
    afi = models.CharField(_("Address Family"), max_length=1,
            choices=[("4", _("IPv4")), ("6", _("IPv6"))])
    prefix = CIDRField(_("Prefix"))

    def __unicode__(self):
        return u"%s %s" % (self.table.name, self.prefix)

    def save(self, *args, **kwargs):
        # Set AFI
        self.afi = IP.prefix(self.prefix).afi
        return super(PrefixTablePrefix, self).save(*args, **kwargs)


class Template(models.Model):
    class Meta:
        verbose_name = _("Template")
        verbose_name_plural = _("Templates")
        ordering = ["name"]

    name = models.CharField(_("Name"), unique=True, max_length=128)
    subject = models.TextField(_("Subject"))
    body = models.TextField(_("Body"))

    def __unicode__(self):
        return self.name

    def render_subject(self, LANG=None, **kwargs):
        return DjangoTemplate(self.subject).render(Context(kwargs))

    def render_body(self, LANG=None, **kwargs):
        return DjangoTemplate(self.body).render(Context(kwargs))


class SystemTemplate(models.Model):
    class Meta:
        verbose_name = _("System template")
        verbose_name_plural = _("System templates")
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=64, unique=True)
    description = models.TextField(_("Description"), null=True, blank=True)
    template = models.ForeignKey(Template, verbose_name=_("Template"))

    def __unicode__(self):
        return self.name

    def render_subject(self, LANG=None, **kwargs):
        return self.template.render_subject(lang=LANG, **kwargs)

    def render_body(self, LANG=None, **kwargs):
        return self.template.render_body(lang=LANG, **kwargs)

    @classmethod
    def notify_users(cls, name, users, **kwargs):
        """
        Send notifications via template to users
        :param name: System template name
        :param users: List of User instances or id's
        """
        # Find system template by name
        try:
            t = cls.objects.get(name=name)
        except cls.DoesNotExist:
            return
        # Fix users
        u_list = []
        for u in users:
            if type(u) in (types.IntType, types.LongType):
                try:
                    u_list += [User.objects.get(id=u)]
                except User.DoesNotExist:
                    continue
            elif type(u) in (types.StringType, types.UnicodeType):
                u_list += [User.objects.get(username=u)]
            elif isinstance(u, User):
                u_list += [u]
        # Left only active users
        u_list = [u for u in u_list if u.is_active]
        # Send notifications


class Checkpoint(models.Model):
    """
    Checkpoint is a marked moment in time
    """
    class Meta:
        verbose_name = _("Checkpoing")
        verbose_name_plural = _("Checkpoints")

    timestamp = models.DateTimeField(_("Timestamp"))
    user = models.ForeignKey(User, verbose_name=_("User"), blank=True, null=True)
    comment = models.CharField(_("Comment"), max_length=256)
    private = models.BooleanField(_("Private"), default=False)

    def __unicode__(self):
        if self.user:
            return u"%s[%s]: %s" % (self.timestamp, self.user.username,
                                    self.comment)

    @classmethod
    def set_checkpoint(cls, comment, user=None, timestamp=None, private=True):
        if not timestamp:
            timestamp = datetime.datetime.now()
        cp = Checkpoint(timestamp=timestamp, user=user, comment=comment,
                        private=private)
        cp.save()
        return cp


##
## Install triggers
##
if settings.IS_WEB and not settings.IS_TEST:
    DBTrigger.refresh_cache()  # Load existing triggers
    # Trigger cache syncronization
    post_save.connect(DBTrigger.refresh_cache, sender=DBTrigger)
    post_delete.connect(DBTrigger.refresh_cache, sender=DBTrigger)
    # Install signal hooks
    pre_save.connect(DBTrigger.pre_save_dispatch)
    post_save.connect(DBTrigger.post_save_dispatch)
    pre_delete.connect(DBTrigger.pre_delete_dispatch)
    post_delete.connect(DBTrigger.post_delete_dispatch)

##
## Monkeypatch to change User.username.max_length
##
User._meta.get_field("username").max_length = User._meta.get_field("email").max_length
User._meta.get_field("username").validators = [MaxLengthValidator(User._meta.get_field("username").max_length)]
User._meta.ordering = ["username"]


def search_tags(user, query, limit):
    """
    Search by tags
    """
    from noc.lib.search import SearchResult  # Must be inside method to prevent import loops

    # Find tags
    tags = []
    for p in query.split(","):
        p = p.strip()
        try:
            tags += [Tag.objects.get(name=p)]
        except Tag.DoesNotExist:
            return []
    if not tags:
        return []
    # Intersect tags
    r = None
    for t in tags:
        o = [o.object for o in t.items.all()]
        if r is None:
            r = set(o)
        else:
            r &= set(o)
    if not r:
        return []
    rr = []
    for i in r:
        if hasattr(i, "get_absolute_url"):
            rr += [SearchResult(
                    url=i.get_absolute_url(),
                    title=unicode(i),
                    text=i.tags,
                    relevancy=1.0,
                )]
    return rr

search_methods.add(search_tags)
