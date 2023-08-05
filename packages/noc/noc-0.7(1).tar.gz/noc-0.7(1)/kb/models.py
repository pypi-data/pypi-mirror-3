# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Models for KB application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import difflib
import re
## Django modules
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
## NOC modules
from noc.main.models import Language, database_storage
from noc.kb.parsers import parser_registry
from noc.lib.search import SearchResult
from noc.lib.validators import is_int
from noc.lib.app.site import site
from noc.lib.fields import AutoCompleteTagsField

##
## Register all wiki-syntax parsers
##
parser_registry.register_all()
##
## KB Entry
##
class KBEntry(models.Model):
    class Meta:
        verbose_name="KB Entry"
        verbose_name_plural="KB Entries"
        ordering=("id",)
    subject=models.CharField("Subject",max_length=256)
    body=models.TextField("Body")
    language=models.ForeignKey(Language,verbose_name="Language",limit_choices_to={"is_active":True})
    markup_language=models.CharField("Markup Language",max_length="16",choices=parser_registry.choices)
    tags=AutoCompleteTagsField("Tags",null=True,blank=True)
    def __unicode__(self):
        if self.id:
            return u"KB%d: %s"%(self.id,self.subject)
        else:
            return u"New: %s"%self.subject
    ##
    def get_absolute_url(self):
        return site.reverse("kb:view:view",self.id)
    ## Wiki parser class
    def _parser(self):
        return parser_registry[self.markup_language]
    parser=property(_parser)
    ## Returns parsed HTML
    def _html(self):
        return self.parser.to_html(self)
    html=property(_html)
    ##
    ## Search engine
    ##
    @classmethod
    def search(cls,user,query,limit):
        if user.has_perm("kb.change_kbentry"):
            q=Q(subject__icontains=query)|Q(body__icontains=query)
            if is_int(query):
                q|=Q(id=int(query))
            elif query.startswith("KB") and is_int(query[2:]):
                q|=Q(id=int(query[2:]))
            for r in KBEntry.objects.filter(q):
                try:
                    idx=r.body.index(query)
                    text=r.body[idx-100:idx+len(query)+100]
                except ValueError:
                    text=r.body[:100]
                yield SearchResult(
                    url=("kb:view:view",r.id),
                    title="KB%d: %s"%(r.id,r.subject),
                    text=text,
                    relevancy=1.0)
    ##
    ## Returns latest KBEntryHistory record
    ##
    @property
    def last_history(self):
        return self.kbentryhistory_set.order_by("-timestamp")[0]
    
    ##
    ## Returns a list of last modified KB Entries
    ##
    @classmethod
    def last_modified(self,num=20):
        from django.db import connection
        c=connection.cursor()
        c.execute("SELECT kb_entry_id,MAX(timestamp) FROM kb_kbentryhistory GROUP BY 1 ORDER BY 2 DESC LIMIT %d"%num)
        return [KBEntry.objects.get(id=r[0]) for r in c.fetchall()]
    ##
    ## Write article preview log
    ##
    def log_preview(self,user):
        KBEntryPreviewLog(kb_entry=self,user=user).save()
    ##
    ## Returns preview count
    ##
    @property
    def preview_count(self):
        return self.kbentrypreviewlog_set.count()
    
    ##
    ## Returns most popular articles
    ##
    @classmethod
    def most_popular(self,num=20):
        from django.db import connection
        c=connection.cursor()
        c.execute("SELECT kb_entry_id,COUNT(*) FROM kb_kbentrypreviewlog GROUP BY 1 ORDER BY 2 DESC LIMIT %d"%num)
        return [KBEntry.objects.get(id=r[0]) for r in c.fetchall()]
    ##
    ## Callable for KBEntryAttachment.file.upload_to
    ##
    @classmethod
    def upload_to(cls,instance,filename):
        return "/kb/%d/%s"%(instance.kb_entry.id,filename)
    ##
    ## Returns a list of visible attachments
    ##
    @property
    def visible_attachments(self):
        return [{"name":x.name,"size":x.size,"mtime":x.mtime,"description":x.description}
            for x in self.kbentryattachment_set.filter(is_hidden=False).order_by("name")]
    ##
    ##
    ##
    @property
    def has_visible_attachments(self):
        return self.kbentryattachment_set.filter(is_hidden=False).exists()
    ##
    ## save model, compute body's diff and save event history
    ##
    def save(self,user=None,timestamp=None):
        if self.id:
            old_body=KBEntry.objects.get(id=self.id).body
        else:
            old_body=""
        super(KBEntry,self).save()
        if old_body!=self.body:
            diff="\n".join(difflib.unified_diff(self.body.splitlines(),old_body.splitlines()))
            KBEntryHistory(kb_entry=self,user=user,diff=diff,timestamp=timestamp).save()
    ##
    ## Check has KBEntry any bookmarks
    ##
    def is_bookmarked(self,user=None):
        # Check Global bookmarks
        if KBGlobalBookmark.objects.filter(kb_entry=self).count()>0:
            return True
        if user and KBUserBookmark.objects.filter(kb_entry=self,user=user).exists():
            return True
        return False
    ##
    ## Set user bookmark
    ##
    def set_user_bookmark(self,user):
        if KBUserBookmark.objects.filter(kb_entry=self,user=user).count()==0:
            KBUserBookmark(kb_entry=self,user=user).save()
    ##
    ## Uset user bookmark
    ##
    def unset_user_bookmark(self,user):
        for b in  KBUserBookmark.objects.filter(kb_entry=self,user=user):
            b.delete()

##
## Attachments
##
class KBEntryAttachment(models.Model):
    class Meta:
        verbose_name="KB Entry Attachment"
        verbose_name_plural="KB Entry Attachments"
        unique_together=[("kb_entry","name")]
    kb_entry=models.ForeignKey(KBEntry,verbose_name="KB Entry")
    name=models.CharField("Name",max_length=256)
    description=models.CharField("Description",max_length=256,null=True,blank=True)
    is_hidden=models.BooleanField("Is Hidden",default=False)
    file=models.FileField("File",upload_to=KBEntry.upload_to,storage=database_storage)
    def __unicode__(self):
        return u"%d: %s"%(self.kb_entry.id,self.name)
    ##
    ## Delete object on database storage too
    ##
    def delete(self):
        super(KBEntryAttachment,self).delete()
        self.file.storage.delete(self.file.name)
    ##
    ## File size
    ##
    def _size(self):
        s=self.file.storage.stat(self.file.name)
        if s:
            return s["size"]
        else:
            return None
    size=property(_size)
    ##
    ## File mtime
    ##
    def _mtime(self):
        s=self.file.storage.stat(self.file.name)
        if s:
            return s["mtime"]
        else:
            return None
    mtime=property(_mtime)
    ##
    ## Search engine
    ##
    @classmethod
    def search(cls,user,query,limit):
        if user.has_perm("kb.change_kbentry"):
            q=Q(name__icontains=query)|Q(description__icontains=query)
            for r in KBEntryAttachment.objects.filter(q):
                yield SearchResult(
                    url=("kb:view:view",r.kb_entry.id),
                    title="KB%d: %s"%(r.kb_entry.id,r.kb_entry.subject),
                    text="Attachement: %s (%s)"%(r.name,r.description),
                    relevancy=1.0)

##
## Modification History
##
class KBEntryHistory(models.Model):
    class Meta:
        verbose_name="KB Entry History"
        verbose_name_plural="KB Entry Histories"
        ordering=("kb_entry","timestamp")
    kb_entry=models.ForeignKey(KBEntry,verbose_name="KB Entry")
    timestamp=models.DateTimeField("Timestamp",auto_now_add=True)
    user=models.ForeignKey(User,verbose_name="User")
    diff=models.TextField("Diff")
##
## Preview Log
##
class KBEntryPreviewLog(models.Model):
    class Meta:
        verbose_name="KB Entry Preview Log"
        verbose_name_plural="KB Entry Preview Log"
    kb_entry=models.ForeignKey(KBEntry,verbose_name="KB Entry")
    timestamp=models.DateTimeField("Timestamp",auto_now_add=True)
    user=models.ForeignKey(User,verbose_name="User")
##
## Global Bookmarks
##
class KBGlobalBookmark(models.Model):
    class Meta:
        verbose_name="KB Global Bookmark"
        verbose_name_plural="KB Global Bookmarks"
    kb_entry=models.ForeignKey(KBEntry,verbose_name="KBEntry",unique=True)
    def __unicode__(self):
        return unicode(self.kb_entry)
##
## User Bookmarks
##
class KBUserBookmark(models.Model):
    class Meta:
        verbose_name="KB User Bookmark"
        verbose_name_plural="KB User Bookmarks"
        unique_together=[("user","kb_entry")]
    user=models.ForeignKey(User,verbose_name="User")
    kb_entry=models.ForeignKey(KBEntry,verbose_name="KBEntry")
    def __unicode__(self):
        return u"%s: %s"%(unicode(self.user),unicode(self.kb_entry))

## Regular expression to match template variable
rx_template_var=re.compile("{{([^}]+)}}",re.MULTILINE)
##
## KB Entry Template
##
class KBEntryTemplate(models.Model):
    class Meta:
        verbose_name="KB Entry Template"
        verbose_name_plural="KB Entry Templates"
        ordering=("id",)
    name=models.CharField("Name",max_length=128,unique=True)
    subject=models.CharField("Subject",max_length=256)
    body=models.TextField("Body")
    language=models.ForeignKey(Language,verbose_name="Language",limit_choices_to={"is_active":True})
    markup_language=models.CharField("Markup Language",max_length="16",choices=parser_registry.choices)
    tags=AutoCompleteTagsField("Tags",null=True,blank=True)
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return site.reverse("kb:kbentrytemplate:change",self.id)
    ##
    ## Returns template variables list
    ##
    def _var_list(self):
        var_set=set(rx_template_var.findall(self.subject))
        var_set.update(rx_template_var.findall(self.body))
        return sorted(var_set)
    var_list=property(_var_list)
