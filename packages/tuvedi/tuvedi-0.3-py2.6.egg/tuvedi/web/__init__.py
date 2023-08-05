#
# TuVedi - Interactive Information System
#
# Copyright (c) 2011 Philipp Seidel
#
# Licensed under the GPLv3 (LICENSE-GPLv3)
#

import pypoly
import pypoly.http
import pypoly.session
from pypoly.content.extra import JSON, PlainText


class Main(object):
    def init(self):
        pass

    def start(self):
        pypoly.url.connect(
            "",
            controller=Controller(),
            action="index",
        )

    def unload(self):
        pass


class Controller(object):
    _pypoly_config = {
                "session.mode": pypoly.session.MODE_READONLY
    }

    @pypoly.http.expose(
        routes=[
            {
                "action": "index",
                "path": "index/{device_id}",
                "types": {
                    "device_id": int
                }
            }
        ]
    )
    def index(self, *args, **values):
        try:
            command_path = pypoly.url(
                action="index",
                values={
                    "device_id": 1
                }
            )
            command_path = str(command_path).rsplit("/", 2)[0] + "/"
        except Exception, inst:
            pypoly.log.warning("Can't generate command path: %s" % str(inst))
            command_path = "/tuvedi/"
        prefs = pypoly.tool.tuvedi.get_device_preferences(
            values.get("device_id")
        )
        data = """
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>TuVedi</title>
        <script type="text/javascript" src="%(js_jquery)s"></script>
        <script type="text/javascript" src="%(js_tuvedi)s"></script>
        <script type="text/javascript">
            jQuery(document).ready(function($) {
                TuVedi.start({
                    "animation.speed": "%(animation_speed)s",
                    "animation.type": "%(animation_type)s",
                    "command_path": "%(command_path)s",
                    "device": "%(device)s",
                    "static_path": "%(static_path)s"
                });
            });
        </script>
    </head>
    <body>

    </body>
</html>
        """ % dict(
            animation_speed=prefs.get("animation_speed"),
            animation_type=prefs.get("animation_type"),
            js_jquery=pypoly.url("jquery/jquery.js"),
            js_tuvedi=pypoly.url("tuvedi.js"),
            command_path=command_path,
            device=values["device_id"],
            static_path=pypoly.url("")
        )
        content = PlainText(
            mime_type="text/html",
            data=data
        )
        return content

    @pypoly.http.expose(
        routes=[
            {
                "action": "update",
                "path": "update/{device_id}",
                "requirements": {
                    "device_id": "\d+"
                },
                "types": {
                    "device_id": int
                }
            },
            {
                "action": "update",
                "path": "update/{device_name}",
                "requirements": {
                    "device_name": "[a-z]*"
                }
            }
        ]
    )
    def update(self, **values):
        try:
            import json
            data = json.loads(
                values['data']
            )
        except:
            data = {}

        if "device_name" in values:
            presentation = pypoly.tool.tuvedi.get_presentation_by_device(
                device_name=values['device_name'],
                presentation=data
            )
        elif "device_id" in values:
            presentation = pypoly.tool.tuvedi.get_presentation_by_device(
                device_id=values['device_id'],
                presentation=data
            )

        return JSON(presentation)

    @pypoly.http.expose(
        routes=[
            {
                "action": "get_template",
                "path": "get-template/{id}",
                "requirements": {
                    "id": "\d+"
                },
                "types": {
                    "id": int
                }
            }
        ]
    )
    def get_template(self, **values):
        data = pypoly.tool.tuvedi.get_template(values.get("id"))

        content = PlainText(
            mime_type="text/html",
            data=data
        )

        return content

    @pypoly.http.expose(
        routes=[
            {
                "action": "get_component",
                "path": "get-component/{id}",
                "requirements": {
                    "id": "\d+"
                },
                "types": {
                    "id": int
                }
            }
        ]
    )
    def get_component(self, **values):
        data = pypoly.tool.tuvedi.get_javascript(values.get("id"))

        content = PlainText(
            mime_type="text/javascript",
            data=data
        )

        return content

    @pypoly.http.expose(
        routes=[
            {
                "action": "get_style",
                "path": "get-style/{id}",
                "requirements": {
                    "id": "\d+"
                },
                "types": {
                    "id": int
                }
            }
        ]
    )
    def get_style(self, **values):
        data = pypoly.tool.tuvedi.get_style(values.get("id"))

        content = PlainText(
            mime_type="text/css",
            data=data
        )

        return content
