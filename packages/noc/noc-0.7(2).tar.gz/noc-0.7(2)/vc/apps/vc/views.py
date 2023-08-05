# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VC Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
from django import forms
## NOC modules
from noc.lib.app import ModelApplication, view
from noc.vc.models import VC, VCDomain
from noc.sa.models import ManagedObject, ReduceTask
from noc.sa.models import profile_registry


def vc_prefixes(obj):
    """
    Prefixes bind to VC
    """
    return ", ".join([p.prefix for p in
                      obj.prefix_set.order_by("vrf__name", "afi", "prefix")])

vc_prefixes.short_description = "Prefixes"


class VCAdmin(admin.ModelAdmin):
    """
    VC Admin
    """
    list_display = ["vc_domain", "name", "l1", "l2",
                    "description", vc_prefixes]
    search_fields = ["name", "l1", "l2", "description"]
    list_filter = ["vc_domain"]


def reduce_vlan_import(task, vc_domain):
    """
    Reduce task for VLAN import.
    Create vlans which not exist in database
    """
    from noc.vc.models import VC

    mt = task.maptask_set.all()[0]
    if mt.status != "C":
        return 0
    count = 0
    max_name_len = VC._meta.get_field_by_name("name")[0].max_length
    for v in mt.script_result:
        vlan_id = v["vlan_id"]
        name = v.get("name", "VLAN%d" % vlan_id)
        try:
            VC.objects.get(vc_domain=vc_domain, l1=vlan_id)
        except VC.DoesNotExist:
            # Generate unique name
            n = 0
            nm = VC.convert_name(name)
            while VC.objects.filter(vc_domain=vc_domain, name=nm).exists():
                n += 1
                nm = "_%d" % n
                nm = name[:max_name_len - len(nm)] + nm
            # Save
            vc = VC(vc_domain=vc_domain, l1=vlan_id, l2=0, name=nm,
                    description=name)
            vc.save()
            count += 1
    return count


class VCApplication(ModelApplication):
    """
    VC application
    """
    model = VC
    model_admin = VCAdmin
    menu = "Virtual Circuits"

    class SAImportVLANsForm(forms.Form):
        """
        Import VLANs Form
        """
        vc_domain = forms.ModelChoiceField(label="VC Domain",
                                           queryset=VCDomain.objects)
        managed_object = forms.ModelChoiceField(label="Managed Object",
            queryset=ManagedObject.objects.filter(profile_name__in=[
                p.name for p in profile_registry.classes.values()
                if "get_vlans" in p.scripts]).order_by("name"))

    @view(url=r"^import_sa/$", url_name="import_sa", access="import")
    def view_import_sa(self, request):
        """
        Import VLANs via service activation
        """
        if request.POST:
            form = self.SAImportVLANsForm(request.POST)
            if form.is_valid():
                task = ReduceTask.create_task(
                    [form.cleaned_data["managed_object"]],
                                                         reduce_vlan_import,
                        {"vc_domain": form.cleaned_data["vc_domain"]},
                                                         "get_vlans", None, 60)
                return self.response_redirect("vc:vc:import_sa_task", task.id)
        else:
            form = self.SAImportVLANsForm()
        return self.render(request, "import_vlans.html", {"form": form})

    @view(url=r"^import_sa/(?P<task_id>\d+)/$", url_name="import_sa_task",
          access="import")
    def view_import_sa_task(self, request, task_id):
        """
        Wait for import task to complete
        """
        task = self.get_object_or_404(ReduceTask, id=int(task_id))
        try:
            result = task.get_result(block=False)
        except ReduceTask.NotReady:
            return self.render_wait(request, subject="Vlan import",
                                    text="Import in progress. Please wait ...")
        self.message_user(request, "%d VLANs are imported" % result)
        return self.response_redirect("vc:vc:changelist")
