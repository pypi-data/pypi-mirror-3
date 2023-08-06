//---------------------------------------------------------------------
// vc.vc application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vc.Application");

Ext.define("NOC.vc.vc.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.vc.vc.Model",
        "NOC.core.TagsField",
        "NOC.main.style.LookupField",
        "NOC.vc.vcdomain.LookupField"
    ],
    model: "NOC.vc.vc.Model",
    search: true,
    rowClassField: "row_class",

    columns: [
        {
            text: "VC Domain",
            dataIndex: "vc_domain",
            renderer: NOC.render.Lookup("vc_domain")
        },
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Label",
            dataIndex: "label",
            width: 50,
            sortable: false
        },
        {
            text: "L1",
            dataIndex: "l1",
            width: 25,
            hidden: true
        },
        {
            text: "L2",
            dataIndex: "l2",
            width: 25,
            hidden: true
        },
        {
            text: "Int.",
            dataIndex: "interfaces_count",
            width: 50,
            sortable: false
        },
        {
            text: "Prefixes",
            dataIndex: "prefixes",
            width: 100,
            sortable: false
        },
        {
            text: "Description",
            dataIndex: "description",
            flex: 1
        },
        {
            text: "Tags",
            dataIndex: "tags",
            renderer: NOC.render.Tags
        }
    ],
    fields: [
        {
            name: "vc_domain",
            xtype: "vc.vcdomain.LookupField",
            fieldLabel: "VC Domain",
            allowBlank: false
        },
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "Name",
            allowBlank: false,
            regex: /^[a-zA-Z0-9_\-]+$/
        },
        {
            name: "l1",
            xtype: "numberfield",
            fieldLabel: "L1",
            allowBlank: false
        },
        { // @todo: Auto-hide when VC domain does not support l2
            name: "l2",
            xtype: "numberfield",
            fieldLabel: "L2",
            allowBlank: true
        },
        {
            name: "description",
            xtype: "textfield",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "style",
            xtype: "main.style.LookupField",
            fieldLabel: "Style",
            allowBlank: true
        },
        {
            name: "tags",
            xtype: "tagsfield",
            fieldLabel: "Tags",
            allowBlank: true
        }
    ],
    filters: [
        {
            title: "By VC Domain",
            name: "vc_domain",
            ftype: "lookup",
            lookup: "vc.vcdomain"
        },
        {
            title: "By VC Filter",
            name: "l1",
            ftype: "vcfilter"
        },
        {
            title: "By Tags",
            name: "tags",
            ftype: "tag"
        },
        {
            title: "By Style",
            name: "style",
            ftype: "lookup",
            lookup: "main.style"
        }
    ],
    //
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            gridToolbar: [
                {
                    itemId: "create_first",
                    text: "Add First Free",
                    iconCls: "icon_application_form_add",
                    tooltip: "Add first free VC",
                    checkAccess: NOC.hasPermission("create"),
                    scope: me,
                    handler: me.onFirstNewRecord
                },
                {
                    itemId: "import",
                    text: "Import",
                    iconCls: "icon_door_in",
                    tooltip: "Import VCs",
                    checkAccess: NOC.hasPermission("import"),
                    menu: {
                        xtype: "menu",
                        plain: true,
                        items: [
                            {
                                text: "VLANs From Switch",
                                itemId: "vlans_from_switch",
                                iconCls: "icon_arrow_right"
                            }
                        ],
                        listeners: {
                            click: {
                                scope: me,
                                fn: me.onImportVLANSFromSwitch
                            }
                        }
                    }
                }
            ],
            formToolbar: [
                {
                    itemId: "interfaces",
                    text: "VC Interfaces",
                    iconCls: "icon_page_link",
                    tooltip: "Show VC interfaces",
                    checkAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onVCInterfaces
                },
                {
                    itemId: "add_interfaces",
                    text: "Add Interfaces",
                    iconCls: "icon_page_add",
                    tooltip: "Add interfaces to VC",
                    checkAccess: NOC.hasPermission("set_untagged"),
                    scope: me,
                    handler: me.onAddVCInterfaces
                }
            ]
        });

        me.callParent();
    },
    onFirstNewRecord: function() {
        var me = this;
        Ext.create("NOC.vc.vc.AddFirstFreeForm", {app: me});
    },
    //
    onImportVLANSFromSwitch: function() {
        Ext.create("NOC.vc.vc.MOSelectForm", {app: this});
    },
    //
    runImportFromSwitch: function(vc_domain, managed_object, vc_filter) {
        var me = this;

        me.vc_domain = vc_domain;
        me.vc_filter = vc_filter;
        // Get VC filter expression
        Ext.Ajax.request({
            url: "/vc/vcfilter/" + me.vc_filter + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                // Run MRT
                var me = this,
                    r = Ext.decode(response.responseText);
                me.vc_filter_expression = r.expression;
                NOC.mrt({
                    url: "/vc/vc/mrt/get_vlans/",
                    selector: managed_object,
                    scope: me,
                    success: me.processImportFromSwitch,
                    failure: function() {
                        NOC.error("Failed to import VLANs")
                    }
                });
            },
            failure: function() {
                NOC.error("Failed to get VC Filter");
            }
        });
    },
    //
    processImportFromSwitch: function(result) {
        var me = this,
            r = result[0];
        console.log("R", result, r);
        if(!Ext.isDefined(r)) {
            NOC.error("Failed to import VLANs.<br/>No result returned");
            return;
        }
        if(r.status) {
            // VLANS Fetched
            // r.code
            var w = Ext.create("NOC.vc.vc.VCImportForm", {
                app: me,
                vc_domain: me.vc_domain,
                vc_filter: me.vc_filter,
                vc_filter_expression: me.vc_filter_expression
            });
            w.loadVLANsFromSwitch(r.result);
        } else {
            // Failed to fetch
            NOC.error("Failed to import VLANs from {0}:<br>{1}",
                      r.object_name, r.result.text);
        }
    },
    // Called when import complete
    onImportSuccess: function(result) {
        var me = this;
        me.reloadStore();
    },
    // Show interfaces window
    onVCInterfaces: function() {
        var me = this,
            vc = me.currentRecord.data;
        Ext.Ajax.request({
            url: "/vc/vc/" + vc.id + "/interfaces/",
            method: "GET",
            scope: me,
            success: function(response) {
                var r = Ext.decode(response.responseText);
                if(!r.tagged && !r.untagged && !r.l3) {
                    NOC.info("No interfaces found");
                } else {
                    Ext.create("NOC.vc.vc.VCInterfaces", {
                        app: me,
                        vc: vc,
                        interfaces: r
                    });
                }
            },
            failure: function() {
                NOC.error("Failed to get interfaces");
            }
        });
    },
    //
    onAddVCInterfaces: function() {
        var me = this,
            vc = me.currentRecord.data;
        Ext.create("NOC.vc.vc.AddInterfacesForm", {
            app: me,
            vc: vc
        });
    }
});
