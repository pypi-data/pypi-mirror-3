# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.desktop application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY
## NOC modules
from noc.settings import config
from noc.lib.app import ExtApplication, ModelApplication, view, PermitLogged
from noc.lib.version import get_version
from noc.lib.middleware import set_user
from noc.settings import LANGUAGE_CODE
from noc.main.auth.backends import backend as auth_backend


class DesktopAppplication(ExtApplication):
    """
    main.desktop application
    """
    @view(method=["GET"], url="^$", url_name="desktop", access=True)
    def view_desktop(self, request):
        """
        Render application root template
        """
        ext_apps = [a for a in self.site.apps
                    if isinstance(self.site.apps[a], ExtApplication) or\
                    isinstance(self.site.apps[a], ModelApplication)]
        apps = [a.split(".") for a in sorted(ext_apps)]
        # Prepare settings
        favicon_url = config.get("customization", "favicon_url")
        if favicon_url.endswith(".png"):
            favicon_mime = "image/png"
        elif favicon_url.endswith(".jpg") or favicon_url.endswith(".jpeg"):
            favicon_mime = "image/jpeg"
        else:
            favicon_mime = None

        setup = {
            "installation_name": config.get("customization",
                                            "installation_name"),
            "logo_url": config.get("customization", "logo_url"),
            "logo_width": config.get("customization", "logo_width"),
            "logo_height": config.get("customization", "logo_height"),
            "favicon_url": favicon_url,
            "favicon_mime": favicon_mime
        }
        return self.render(request, "desktop.html", apps=apps, setup=setup)

    ##
    ## Exposed Public API
    ##
    @view(method=["GET"], url="^version/$", access=True, api=True)
    def api_version(self, request):
        """
        Return current NOC version

        :returns: version string
        :rtype: Str
        """
        return get_version()

    @view(method=["GET"], url="^is_logged/$", access=True, api=True)
    def api_is_logged(self, request):
        """
        Check wrether the session is authenticated.

        :returns: True if session authenticated, False otherwise
        :rtype: Bool
        """
        return request.user.is_authenticated()

    @view(method=["POST"], url="^login/$", access=True, api=True)
    def api_login(self, request):
        """
        Authenticate session

        :returns: True or False depending on login status
        :rtype: Bool
        """
        user = auth_backend.authenticate(**dict([(str(k), v) for k, v in request.POST.items()]))
        if not user:
            return False
        if SESSION_KEY in request.session:
            if request.session[SESSION_KEY] != user.id:
                # User changed. Flush session
                request.session.flush()
        else:
            request.session.cycle_key()
        user.backend = "%s.%s" % (auth_backend.__module__,
                                  auth_backend.__class__.__name__)
        request.session[SESSION_KEY] = user.id
        request.session[BACKEND_SESSION_KEY] = user.backend
        request.user = user
        r = request.user.is_authenticated()
        if r:
            # Write actual user to TLS cache
            set_user(request.user)
            # Set up session language
            lang = LANGUAGE_CODE
            profile = request.user.get_profile()
            if profile and profile.preferred_language:
                lang = profile.preferred_language
            request.session["django_language"] = lang
        return r

    @view(method=["POST"], url="^logout/$", access=PermitLogged(), api=True)
    def api_logout(self, request):
        """
        Deauthenticate session

        :returns: Logout status: True or False
        :rtype: Bool
        """
        if request.user.is_authenticated():
            request.session.flush()
            from django.contrib.auth.models import AnonymousUser
            request.user = AnonymousUser()
        return True

    @view(method=["GET"], url="^user_settings/$",
          access=PermitLogged(), api=True)
    def api_user_settings(self, request):
        """
        Get user settings
        """
        user = request.user
        return {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "theme": "gray",
            "can_change_credentials": auth_backend.can_change_credentials
        }

    @view(method=["GET"], url="^navigation/$", access=True, api=True)
    def api_navigation(self, request):
        """
        Return user's navigation menu tree

        :param node:
        :returns:
        """
        def get_children(node, user):
            c = []
            for r in node:
                n = {
                    "id": r["id"],
                    "text": r["title"]
                }
                if "iconCls" in r:
                    n["iconCls"] = r["iconCls"]
                if "children" in r:
                    cld = get_children(r["children"], user)
                    if not cld:
                        continue
                    n["leaf"] = False
                    n["children"] = cld
                    c += [n]
                elif r["access"](user):
                    n["leaf"] = True
                    c += [n]
            return c

        # Return empty list for unauthenticated user
        if not request.user.is_authenticated():
            return []
        node = request.GET.get("node", "root")
        # For root nodes - show all modules user has access
        if node == "root":
            root = self.site.menu
        else:
            try:
                root = self.site.menu_index[node]["children"]
            except KeyError:
                return self.response_not_found()
        return get_children(root, request.user)

    @view(method=["GET"], url="^launch_info/$", access=PermitLogged(),
          api=True)
    def api_launch_info(self, request):
        """
        Get application launch information
        :param node: Menu node id
        :returns: Dict with: 'class' - application class name
        """
        try:
            menu = self.site.menu_index[request.GET["node"]]
            if "children" in menu:
                raise KeyError
        except KeyError:
            return self.response_not_found()
        return menu["app"].launch_info

    @view(method=["GET"], url="^login_fields/$", access=True, api=True)
    def api_login_fields(self, request):
        """
        Returns a list of login form form fields, suitable to use as
        ExtJS Ext.form.Panel items
        """
        return auth_backend.get_login_fields()

    @view(method=["GET"], url="^change_credentials_fields/$",
          access=PermitLogged(), api=True)
    def api_change_credentials_fields(self, request):
        """
        Returns a list of change credentials field, suitable to use as
        ExtJS Ext.form.Panel items
        """
        return auth_backend.get_change_credentials_fields()

    @view(method=["POST"], url="^change_credentials/$",
          access=PermitLogged(), api=True)
    def api_change_credentials(self, request):
        """
        Change user's credentials if allowed by current backend
        """
        if not auth_backend.can_change_credentials:
            return self.render_json({
                "status": False,
                "error": "Cannot change credentials with selected auth method"},
                status=401)
        try:
            auth_backend.change_credentials(request.user,
                        **dict([(str(k), v) for k, v in request.POST.items()]))
        except ValueError, why:
            return self.render_json({
                "status": False,
                "error": str(why)},
                status=401)
