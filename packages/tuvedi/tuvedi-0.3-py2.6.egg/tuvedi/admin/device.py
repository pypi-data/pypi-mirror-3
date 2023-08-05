# -*- coding: utf-8 -*-
import datetime

import sqlalchemy as sa

import pypoly
import pypoly.session
from pypoly.content.webpage import Webpage, tab, table, message
from pypoly.content.webpage.form import text, Form, button, input
from pypoly.content.webpage.form import list as form_list
from pypoly.http import auth

class DeviceTable(table.Table):
    def __init__(self, *args, **kwargs):
        table.Table.__init__(self, *args, **kwargs)

        self.header.append(
            [
                _(u"Name"),
                _(u"Title"),
                _(u"Description"),
                table.LabelCell(
                    value=_(u"Actions"),
                    colspan=2
                )
            ]
        )

        self.cols.append(table.TextCell())
        self.cols.append(table.TextCell())
        self.cols.append(table.TextCell())
        self.cols.append(table.LinkCell())
        self.cols.append(table.LinkCell())

class DeviceForm(Form):
    def __init__(self, *args, **kwargs):
        data = kwargs['_data']
        del kwargs['_data']
        Form.__init__(self, *args, **kwargs)

        self.append(
            input.TextInput(
                'title',
                label=_(u"Title"),
                required = True,
                value=data['title']
            )
        )

        self.append(
            input.CustomInput(
                'name',
                label=_(u"Name"),
                regex="^[a-zA-Z0-9_-]*$",
                value=data['name']
            )
        )

        self.append(
            text.Textarea(
                'description',
                label=_('Description'),
                value=data['description']
            )
        )

class AddDevice(DeviceForm):
    def __init__(self, *args, **kwargs):
        # add empty data so we can use one form to add and to edit a device
        kwargs['_data'] = dict(
            title=u"",
            name=u"",
            description=u""
        )

        DeviceForm.__init__(self, *args, **kwargs)

        self.add_button(
            button.SubmitButton(
                'submit',
                label=_('Create'),
            )
        )

class EditDevice(DeviceForm):
    def __init__(self, *args, **kwargs):
        prefs = kwargs["_data"]["prefs"]
        del kwargs["_data"]["prefs"]

        DeviceForm.__init__(self, *args, **kwargs)

        anims = [
            ("none", _("None")),
            ("----", "----"),
            ("fade", _("Fade"))
        ]

        dd_anim = form_list.DropdownList(
            "pref-animation_type",
            label=_(u"Animation")
        )

        for value, label in anims:
            if label == "----":
                dd_anim.append(
                    form_list.EmptyItem(
                        None,
                        label="-----------"
                    )
                )
                continue

            dd_anim.append(
                form_list.ListItem(
                    None,
                    label=label,
                    value=value,
                    selected=(value == prefs.get("animation_type", ""))
                )
            )

        speeds = [
            ("slow", _(u"Slow")),
            ("fast", _(u"Fast"))
        ]

        self.append(dd_anim)

        dd_speed = form_list.DropdownList(
            "pref-animation_speed",
            label=_(u"Speed")
        )

        for value, label in speeds:
            dd_speed.append(
                form_list.ListItem(
                    None,
                    label=label,
                    selected=(value == prefs.get("animation_speed", "")),
                    value=value
                )
            )

        self.append(dd_speed)

        self.add_button(
            button.SubmitButton(
                'save',
                label=_('Save'),
            )
        )

        self.add_button(
            button.SubmitButton(
                'cancel',
                label=_('Cancel'),
            )
        )

class Controller(object):
    _pypoly_config = {
        "session.mode": pypoly.session.MODE_READONLY
    }

    @pypoly.http.expose(
        auth = auth.any(
            auth.group("tuvedi.user"),
            auth.group("tuvedi.admin")
        )
    )
    def index(self, **values):
        pypoly.log.debug(values)

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_table = pypoly.tool.db_sa.meta.tables['device']

        form = AddDevice(
            'test',
            method='POST',
            title=_('Create Device'),
            action=pypoly.url(
                action='index',
                scheme='device'
            )
        )

        form.prepare(values)
        if form.is_submit() and form.validate():
            db_ins = db_table.insert().values(
                name=form.get_value("name"),
                title=form.get_value("title"),
                description=form.get_value("description")
            )
            db_conn.execute(db_ins)

            # ToDo: check if insert was successful
            raise pypoly.http.HTTPRedirect(
                url=pypoly.url(
                    action='index',
                    scheme='device'
                ),
            )

        page = Webpage()

        if "status" in values:
            if values['status'] == "created":
                page.append(
                    message.Success(
                        text=_(u"Device successfully created.")
                    )
                )
            if values['status'] == "delete-canceled":
                page.append(
                    message.Info(
                        text=_(u"Deletion canceled.")
                    )
                )
            if values['status'] == "delete-success":
                page.append(
                    message.Success(
                        text=_(u"Device successfully deleted.")
                    )
                )
            if values['status'] == "edit-canceled":
                page.append(
                    message.Info(
                        text=_(u"Editing canceled and changes not saved.")
                    )
                )
            if values['status'] == "edit-failed":
                page.append(
                    message.Error(
                        text=_(u"Something went wrong while saving the device.")
                    )
                )
            if values['status'] == "edit-success":
                page.append(
                    message.Success(
                        text=_(u"Settings are successfully saved.")
                    )
                )

        device_tabs = tab.DynamicTabs(
            'tabs1',
            title = u"Mange Devices"
        )

        device_tab = tab.TabItem(
            'tab1',
            title = u"Devices"
        )

        device_table = DeviceTable()

        db_sel = sa.sql.select([
            db_table.c.id,
            db_table.c.name,
            db_table.c.title,
            db_table.c.description
        ])

        db_res = db_conn.execute(db_sel)

        # show rows
        # we don't want to make an extra sql request to count the rows, so we
        # catch them and check if the table is empty or not
        table_empty = True
        for row in db_res:
            table_empty = False
            device_name=row[db_table.c.name]
            if device_name == None:
                device_name = ""

            device_title=row[db_table.c.title]
            if device_title == None:
                device_title = ""

            device_description=row[db_table.c.description]
            if device_description == None:
                device_description = ""

            device_table.append(
                [
                    device_name,
                    device_title,
                    device_description,
                    table.LinkCell(
                        value = _(u"Edit"),
                        url = pypoly.url(
                            action="edit",
                            values={
                                "id": row[db_table.c.id]
                            },
                            scheme='device'
                        )
                    ),
                    table.LinkCell(
                        value = _(u"Timetable"),
                        url = pypoly.url(
                            action="timetable_edit",
                            values={
                                "id": row[db_table.c.id]
                            },
                            scheme='device'
                        )
                    ),
                ]
            )

        if table_empty == True:
            device_table.append(
                [
                    table.TextCell(
                        colspan=5,
                        value=_(u"No devices available")
                    )
                ]
            )

        device_tab.append(device_table)

        device_tabs.append(device_tab)

        form_tab = tab.TabItem(
            'tab2',
            title = u"Create"
        )

        form_tab.append(form)

        device_tabs.append(form_tab)

        page.append(device_tabs)

        return page

    @pypoly.http.expose(
        routes = [
            dict(
                action = "edit",
                path = "edit/{id}",
                requirements = {
                    "id": "\d+"
                },
                types = {
                    "id": int
                }
            )
        ],
        auth = auth.any(
            auth.group("tuvedi.user"),
            auth.group("tuvedi.admin")
        )
    )
    def edit(self, **values):
        pypoly.log.debug(values)

        device_id = values['id']

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_device = pypoly.tool.db_sa.meta.tables['device']

        db_sel = sa.sql.select(
            [
                db_device.c.id,
                db_device.c.name,
                db_device.c.title,
                db_device.c.description
            ],
            db_device.c.id == device_id
        )

        db_res = db_conn.execute(db_sel)

        db_data = db_res.fetchone()

        data = dict()
        data['title'] = db_data[db_device.c.title]
        if db_data[db_device.c.name] == None:
            data['name'] = ''
        else:
            data['name'] = db_data[db_device.c.name]

        if db_data[db_device.c.description] == None:
            data['description'] = ''
        else:
            data['description'] = db_data[db_device.c.description]

        data["prefs"] = pypoly.tool.tuvedi.get_device_preferences(device_id)

        form = EditDevice(
            'edit-device',
            method='POST',
            title=_('Edit Device: %(device_title)s') % dict(
                device_title=db_data[db_device.c.title]
            ),
            action=pypoly.url(
                action='edit',
                values={
                    "id": device_id,
                },
                scheme='device'
            ),
            _data=data
        )

        form.prepare(values)
        if form.is_submit() and form.validate():
            if form.is_clicked("save"):
                db_update = db_device.update().where(
                    db_device.c.id==device_id
                ).values(
                    name=form.get_value("name"),
                    title=form.get_value("title"),
                    description=form.get_value("description")
                )
                db_res = db_conn.execute(db_update)
                if db_res.rowcount > 0:
                    # save device preferences
                    prefs = {}
                    for elem_name in form.get_element_names():
                        if elem_name != None:
                            if elem_name[:5] == "pref-":
                                prefs[elem_name[5:]] = form.get_value(elem_name)
                    pypoly.tool.tuvedi.set_device_preferences(
                        device_id,
                        prefs
                    )
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "edit-success"
                            },
                            scheme='device'
                        ),
                    )
                else:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "edit-failed"
                            },
                            scheme='device'
                        ),
                    )
            else:
                raise pypoly.http.HTTPRedirect(
                    url=pypoly.url(
                        action='index',
                        values={
                            "status": "edit-canceled"
                        },
                        scheme='device'
                    ),
                )

        page = Webpage()

        page.append(form)

        return page

    @pypoly.http.expose(
        routes = [
            dict(
                action = "timetable_edit",
                path = "timetable-edit/{id}",
                requirements = {
                    "id": "\d+"
                },
                types = {
                    "id": int
                }
            )
        ],
        auth = auth.any(
            auth.group("tuvedi.user"),
            auth.group("tuvedi.admin")
        )
    )
    def timetable_edit(self, **values):
        device_id = values['id']
        from pypoly.content.extra import PlainText
        try:
            command_path = pypoly.url(
                action="timetable_edit",
                scheme="device",
                values={
                    "id": 1
                }
            )
            command_path = str(command_path).rsplit("/", 2)[0] + "/"
        except Exception, inst:
            pypoly.log.warning("Can't generate command path: %s" % str(inst))
            command_path = "/admin/device/"
        data = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<link rel="stylesheet" type="text/css" href="%(url_fc_css)s" />
<link rel="stylesheet" type="text/css" href="%(url_calendar_css)s" />
<script type="text/javascript" src="%(url_jquery_js)s"></script>
<script type="text/javascript" src="%(url_jquery_ui_js)s"></script>
<script type="text/javascript" src="%(url_fc_js)s"></script>
<script type="text/javascript" src="%(url_jquery_json_js)s"></script>
<script type="text/javascript" src="%(url_calendar_js)s"></script>
<script type="text/javascript"">
var device_id = %(device_id)d;
var tuvedi_cmd_url = "%(url_cmd)s";
</script>
</head>
<body>
<div id='wrap'>

<div id='external-events'>
<h4>Draggable Events</h4>
</div>

<div id='calendar'></div>

<div style='clear:both'></div>
<input type="button" onclick="test();" value="save"/>
</div>
</body>
</html>
        """ % dict(
            device_id=device_id,
            url_calendar_css=pypoly.url(
                "/calendar.css"
            ),
            url_calendar_js=pypoly.url(
                "/calendar.js"
            ),
            url_cmd=command_path,
            url_fc_css=pypoly.url(
                "/fullcalendar/fullcalendar/fullcalendar.css"
            ),
            url_jquery_js=pypoly.url(
                "/fullcalendar/jquery/jquery-1.4.4.min.js"
            ),
            url_jquery_ui_js=pypoly.url(
                "/fullcalendar/jquery/jquery-ui-1.8.6.custom.min.js"
            ),
            url_fc_js=pypoly.url(
                "/fullcalendar/fullcalendar/fullcalendar.min.js"
            ),
            url_jquery_json_js=pypoly.url(
                "/fullcalendar/jquery/json.js"
            )
        )
        content = PlainText(
            mime_type='text/html',
            data=data
        )
        return content

    @pypoly.http.expose(
        routes = [
            dict(
                action = "get_presentations",
                path = "get-presentations"
            )
        ],
        auth = auth.any(
            auth.group("tuvedi.user"),
            auth.group("tuvedi.admin")
        )
    )
    def get_presentations(self, **values):
        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_presentation = pypoly.tool.db_sa.meta.tables['presentation']

        db_sel = sa.sql.select([
            db_presentation.c.id,
            db_presentation.c.title,
        ])

        db_res = db_conn.execute(db_sel)

        data = []

        for row in db_res:
            data.append(
                dict(
                    id=row[db_presentation.c.id],
                    title=row[db_presentation.c.title]
                )
            )

        from pypoly.content.extra import JSON
        return JSON(data)

    @pypoly.http.expose(
        routes = [
            dict(
                action = "get_timetable",
                path = "get-timetable/{id}",
                requirements = {
                    "id": "\d+"
                },
                types = {
                    "id": int
                }
            )
        ],
        auth = auth.any(
            auth.group("tuvedi.user"),
            auth.group("tuvedi.admin")
        )
    )
    def get_timetable(self, **values):
        device_id = values['id']
        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_timetable = pypoly.tool.db_sa.meta.tables['timetable']
        db_presentation = pypoly.tool.db_sa.meta.tables['presentation']

        db_sel = sa.sql.select(
            [
                db_timetable.c.id,
                db_timetable.c.presentation_id,
                db_timetable.c.start,
                db_timetable.c.end,
                db_timetable.c.all_day,
                db_presentation.c.title
            ],
            sa.sql.expression.and_(
                db_timetable.c.presentation_id == db_presentation.c.id,
                db_timetable.c.device_id == device_id
            )
        )

        db_res = db_conn.execute(db_sel)

        data = []

        for row in db_res:
            try:
                start = row[db_timetable.c.start].strftime("%s")
            except:
                start = None
            try:
                end = row[db_timetable.c.end].strftime("%s")
            except:
                end = None
            data.append(
                dict(
                    id=row[db_timetable.c.id],
                    presentation_id=row[db_timetable.c.presentation_id],
                    start=start,
                    end=end,
                    title=row[db_presentation.c.title],
                    allDay=row[db_timetable.c.all_day]
                )
            )

        from pypoly.content.extra import JSON
        return JSON(data)

    @pypoly.http.expose(
        routes = [
            dict(
                action = "set_timetable",
                path = "set-timetable/{id}",
                requirements = {
                    "id": "\d+"
                },
                types = {
                    "id": int
                }
            )
        ],
        auth = auth.any(
            auth.group("tuvedi.user"),
            auth.group("tuvedi.admin")
        )
    )
    def set_timetable(self, **values):
        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_timetable = pypoly.tool.db_sa.meta.tables['timetable']
        db_presentation = pypoly.tool.db_sa.meta.tables['presentation']

        update = []
        insert = []

        import json

        tmp = json.loads(values['d'])

        if 'insert' in tmp:
            for item in tmp['insert']:
                try:
                    start = datetime.datetime.strptime(item['start'], "%Y-%m-%d %H:%M")
                except:
                    start = None
                try:
                    end = datetime.datetime.strptime(item['end'], "%Y-%m-%d %H:%M")
                except:
                    end = None
                insert.append(
                    dict(
                        device_id=values['id'],
                        presentation_id=item['presentation_id'],
                        start=start,
                        end=end,
                        all_day=item['allDay']
                    )
                )
            if len(insert) > 0:
                db_conn.execute(
                    db_timetable.insert(),
                    insert
                )

        if 'update' in tmp:
            for item in tmp['update']:
                try:
                    start = datetime.datetime.strptime(item['start'], "%Y-%m-%d %H:%M")
                except:
                    start = None
                try:
                    end = datetime.datetime.strptime(item['end'], "%Y-%m-%d %H:%M")
                except:
                    end = None
                # tid = timetable id
                update.append(
                    dict(
                        tid=item['id'],
                        #presentation_id=item['presentation_id'],
                        start=start,
                        end=end,
                        all_day=item['allDay']
                    )
                )
            if len(update) > 0:
                db_update = db_timetable.update().where(
                    db_timetable.c.id == sa.sql.bindparam('tid')
                ).values(
                    #presentation_id=sa.sql.bindparam('presentation_id'),
                    start=sa.sql.bindparam('start'),
                    end=sa.sql.bindparam('end'),
                    all_day=sa.sql.bindparam('all_day'),
                )

                db_conn.execute(
                    db_update,
                    update
                )

        from pypoly.content.extra import JSON
        return JSON([])
