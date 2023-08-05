#
# TuVedi - Interactive Information System
#
# Copyright (c) 2011 Philipp Seidel
#
# Licensed under the GPLv3 (LICENSE-GPLv3)
#

import pypoly
from pypoly.content.webpage import Webpage, TemplateContent
from pypoly.content.webpage.menu import Menu, MenuItem

import tuvedi
from tuvedi.admin.device import Controller as DeviceController
from tuvedi.admin.filter import Controller as FilterController
from tuvedi.admin.component import Controller as ComponentController
from tuvedi.admin.widget import Controller as WidgetController
from tuvedi.admin.layout import Controller as LayoutController
from tuvedi.admin.template import Controller as TemplateController
from tuvedi.admin.presentation import Controller as PresentationController

class Main(object):
    def init(self):
        pass

    def start(self):
        pypoly.url.connect(
            "",
            controller=MainController(),
            action="index"
        )
        pypoly.url.connect(
            "device/",
            controller = DeviceController(),
            action = "index",
            scheme = "device"
        )
        pypoly.url.connect(
            "filter/",
            controller = FilterController(),
            action = "index",
            scheme = "filter"
        )
        pypoly.url.connect(
            "component/",
            controller = ComponentController(),
            action = "index",
            scheme = "component"
        )
        pypoly.url.connect(
            "widget/",
            controller = WidgetController(),
            action = "index",
            scheme = "widget"
        )
        pypoly.url.connect(
            "layout/",
            controller = LayoutController(),
            action = "index",
            scheme = "layout"
        )
        pypoly.url.connect(
            "template/",
            controller = TemplateController(),
            action = "index",
            scheme = "template"
        )
        pypoly.url.connect(
            "presentation/",
            controller = PresentationController(),
            action = "index",
            scheme = "presentation"
        )
        pypoly.module.register_menu(get_menu)

    def unload(self):
        pass


def get_menu():

    menu = Menu("manage",
                title = _("Manage")
               )
    menu.append(MenuItem("home",
                         title = _("Home"),
                         url = pypoly.url(
                             action = "index"
                         )
                        )
               )
    menu.append(MenuItem("device",
                         title = _("Devices"),
                         url = pypoly.url(
                             action = "index",
                             scheme = "device"
                         )
                        )
               )
#we will use this in a future version
#    menu.append(MenuItem("filter",
#                         title = _("Filter"),
#                         url = pypoly.url(
#                             action = "index",
#                             scheme = "filter"
#                         )
#                        )
#               )
    menu.append(MenuItem("presentation",
                         title = _("Presentation"),
                         url = pypoly.url(
                             action = "index",
                             scheme = "presentation"
                         )
                        )
               )
    menu.append(MenuItem("Widget",
                         title = _("Widget"),
                         url = pypoly.url(
                             action = "index",
                             scheme = "widget"
                         )
                        )
               )
    menu.append(MenuItem("Layout",
                         title = _("Layout"),
                         url = pypoly.url(
                             action = "index",
                             scheme = "layout"
                         )
                        )
               )
    menu.append(MenuItem("component",
                         title = _("Component"),
                         url = pypoly.url(
                             action = "index",
                             scheme = "component"
                         )
                        )
               )
    menu.append(MenuItem("template",
                         title = _("Template"),
                         url = pypoly.url(
                             action = "index",
                             scheme = "template"
                         )
                        )
               )
    return [menu]

class MainController(object):
    @pypoly.http.expose(
        routes = [
            dict(
                action = "index",
                path = ""
            )
        ]
    )
    def index(self, **values):
        pypoly.log.debug(values)

        page = Webpage()

        tpl = """
        <div>
        %(text)s
        </div>
        """ % dict(
            text = _(u"""
                     <h2>Introduction</h2>
                     TuVedi helps you to manage presentations on all your
                     displays. It can be used on nearly every device that"s
                     able to display a web-page.
                     <h2>Device</h2>
                     Every display you want to manage is a device. You can edit
                     device settings and define a timetable for every device.
                     <h2>Presentation</h2>
                     A presentation is the arrangement of widgets.
                     <h2>Widget</h2>
                     To setup a widget you need at least one component.
                     A component in combination with preferences is a widget.
                     It"s possible to create multiple widgets and only use one
                     component.
                     <h2>Layout</h2>
                     To setup a presentation you need at least one layout and to
                     create a layout you need at least one template. A layout is
                     very similar to a widget. It's a template with preferences.
                     <h2>Component</h2>
                     You can upload new components to extend TuVedi.
                     <h2>Template</h2>
                     Customize your presentations with new templates.
                     """
                    )
        )

        c = TemplateContent(
            title=_(u"Welcome to TuVedi v%(version)s" % dict(
                version=tuvedi.__version__
            ))

        )
        c.template = pypoly.template.load_web_from_string(tpl)
        page.append(c)

        return page
