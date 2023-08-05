import sqlalchemy as sa

import pypoly
import pypoly.session

from pypoly.content.webpage import Webpage
from pypoly.content.webpage import tab, table, message
from pypoly.content.webpage.form import text, Form, button, input, Fieldset
from pypoly.content.webpage import table
from pypoly.content.webpage.form import list as form_list, static, TableForm
from pypoly.http import auth

class WidgetTable(table.Table):
    def __init__(self, *args, **kwargs):
        table.Table.__init__(self, *args, **kwargs)

        self.header.append(
            [
                _(u"Title"),
                _(u"Component"),
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

class EditPrefList(TableForm):
    def __init__(self, *args, **kwargs):
        data = kwargs['_data']
        pref_name = kwargs['_pref_name']

        del kwargs['_data']
        del kwargs['_pref_name']

        TableForm.__init__(self, *args, **kwargs)

        self.header.append(
            [
                _(u"S"),
                _(u"Value"),
            ]
        )

        self.cols.append(table.ContentCell())
        self.cols.append(table.ContentCell())

        for pref in data['prefs']:
            if pref['name'] == pref_name:
                if pref['type'] == "integer":
                    for value in pref['value']:
                        self.append(
                            [
                                button.Checkbox(
                                    'delete-%d' % (
                                        value[0]
                                    ),
                                ),
                                input.TextInput(
                                    'pref-%d' % (
                                        value[0]
                                    ),
                                    value=value[1]
                                )
                            ]
                        )

                if pref['type'] == "string":
                    if pref['multiline'] == True:
                        for value in pref['value']:
                            self.append(
                                [
                                    button.Checkbox(
                                        'delete-%d' % (
                                            value[0]
                                        ),
                                        value=False
                                    ),
                                    text.WYSIWYG(
                                        'pref-%d' % (
                                            value[0]
                                        ),
                                        value=value[1]
                                    )
                                ]
                            )
                    else:
                        for value in pref['value']:
                            self.append(
                                [
                                    button.Checkbox(
                                        'delete-%d' % (
                                            value[0]
                                        ),
                                        value=False
                                    ),
                                    input.TextInput(
                                        'pref-%d' % (
                                            value[0]
                                        ),
                                        value=value[1]
                                    )
                                ]
                            )

        self.add_button(
            button.SubmitButton(
                'save',
                label=_(u"Save"),
            )
        )

        self.add_button(
            button.SubmitButton(
                'cancel',
                label=_(u"Cancel"),
            )
        )

        self.add_button(
            button.SubmitButton(
                'delete',
                label=_(u"Delete selected"),
            )
        )

class EditPrefListAddNew(Form):
    def __init__(self, *args, **kwargs):
        data = kwargs['_data']
        pref_name = kwargs['_pref_name']

        del kwargs['_data']
        del kwargs['_pref_name']

        Form.__init__(self, *args, **kwargs)

        for pref in data['prefs']:
            if pref['name'] == pref_name:
                if pref['type'] == "string":
                    if pref['multiline'] == True:
                        self.append(
                            text.WYSIWYG(
                                'pref-new',
                                value=u""
                            )
                        )
                    else:
                        self.append(
                            input.TextInput(
                                'pref-new',
                                value=u""
                            )
                        )
                if pref['type'] == "integer":
                    self.append(
                        input.TextInput(
                            'pref-new',
                            value=u""
                        )
                    )

        self.add_button(
            button.SubmitButton(
                'add',
                label=_(u"Add"),
            )
        )


class CreateWidget(Form):
    def __init__(self, *args, **kwargs):
        components = kwargs['components']
        Form.__init__(self, *args, **kwargs)

        name = input.TextInput(
            'title',
            label=_('Title'),
            required = True
        )
        self.append(name)

        description = text.Textarea(
            'description',
            label=_('Description')
        )
        self.append(description)

        sel = form_list.DropdownList(
            'component_id',
            required = True
        )
        for component in components:
            sel.append(
                form_list.ListItem(
                    None,
                    label=component['title'],
                    value=component['id']
                )
            )
        self.append(sel)

        self.add_button(
            button.SubmitButton(
                'submit',
                label=_('Create'),
            )
        )

class DeleteWidget(Form):
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
            text.Textarea(
                'description',
                label=_(u"Description"),
                value=data['description']
            )
        )

        self.add_button(
            button.SubmitButton(
                'ok',
                label=_(u"Yes, delete it"),
            )
        )

        self.add_button(
            button.SubmitButton(
                'no',
                label=_(u"NO, don't delete it"),
            )
        )

class EditWidget(Form):
    def __init__(self, *args, **kwargs):
        data = kwargs['_data']
        widget_id = kwargs['_widget_id']
        del kwargs['_data']
        del kwargs['_widget_id']

        Form.__init__(self, *args, **kwargs)
        fieldset = Fieldset(
            title=_(u"Widget")
        )
        fieldset.append(
            input.TextInput(
                'title',
                label=_(u"Title"),
                required = True,
                value=data['title']
            )
        )

        fieldset.append(
            text.Textarea(
                'description',
                label=_(u"Description"),
                value=data['description']
            )
        )

        self.append(fieldset)

        if len(data['prefs']) > 0:
            fieldset = Fieldset(
                title=_(u"Preferences")
            )
            for pref in data['prefs']:
                if pref['type'] == 'string':
                    if pref['list'] == True:
                        fieldset.append(
                            static.LinkLabel(
                                None,
                                label=pref['title'],
                                value=_(u"Edit List"),
                                url=str(pypoly.url(
                                    action="edit_list",
                                    values={
                                        "id": widget_id,
                                        "pref_name": pref['name']
                                    },
                                    scheme="widget"
                                ))
                            )
                        )
                    else:
                        fieldset.append(
                            input.TextInput(
                                'pref-%s' % pref['name'],
                                label=pref['title'],
                                value=pref['value']
                            )
                        )
                elif pref['type'] == 'integer':
                    if pref['list'] == True:
                        fieldset.append(
                            static.LinkLabel(
                                None,
                                label=pref['title'],
                                value=_(u"Edit List"),
                                url=str(pypoly.url(
                                    action="edit_list",
                                    values={
                                        "id": widget_id,
                                        "pref_name": pref['name']
                                    },
                                    scheme="widget"
                                ))
                            )
                        )
                    else:
                        fieldset.append(
                            input.NumberInput(
                                'pref-%s' % pref['name'],
                                label=pref['title'],
                                value=pref['value']
                            )
                        )
                elif pref['type'] == 'boolean':
                    fieldset.append(
                        button.Checkbox(
                            'pref-%s' % pref['name'],
                            label=pref['title'],
                            checked=pref['value'],
                            value="checked"
                        )
                    )
                elif pref['type'] == "group":
                    fieldset.append(
                        static.LinkLabel(
                            'group',
                            label=pref['title'],
                            value=_(u"Edit List"),
                            url=pypoly.url(
                                action="edit-group",
                                scheme="widget"
                            )
                        )
                    )



            self.append(fieldset)

        self.add_button(
            button.SubmitButton(
                'save',
                label=_(u"Save"),
            )
        )

        self.add_button(
            button.SubmitButton(
                'cancel',
                label=_(u"Cancel"),
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
        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_component = pypoly.tool.db_sa.meta.tables['component']
        db_widget = pypoly.tool.db_sa.meta.tables['widget']

        db_sel = sa.sql.select([
            db_component.c.id,
            db_component.c.title,
        ])

        db_res = db_conn.execute(db_sel)

        components = []

        for row in db_res:
            components.append(
                dict(
                    id = row[db_component.c.id],
                    title = row[db_component.c.title]
                )
            )

        form = CreateWidget(
            'widget',
            method='POST',
            title=_('Create widget'),
            action=pypoly.url(
                action='index',
                scheme='widget'
            ),
            components = components
        )

        form.prepare(values)
        if form.is_submit() and form.validate():
            component_id=int(form.get_value("component_id"))
            db_ins = db_widget.insert().values(
                title=form.get_value("title"),
                description=form.get_value("description"),
                component_id=component_id,
                last_modified=sa.sql.expression.func.NOW()
            )
            db_conn.execute(db_ins)

            # ToDo: check for errors

            raise pypoly.http.HTTPRedirect(
                url=pypoly.url(
                    action='index',
                    values={
                        "status": "created"
                    },
                    scheme='widget'
                ),
            )

        page = Webpage()

        if "status" in values:
            if values['status'] == "created":
                page.append(
                    message.Success(
                        text=_(u"Widget successfully created.")
                    )
                )
            if values['status'] == "delete-canceled":
                page.append(
                    message.Info(
                        text=_(u"Deletion canceled.")
                    )
                )
            if values['status'] == "delete-failed":
                page.append(
                    message.Error(
                        text=_(u"Something went wrong while deleting the widget.")
                    )
                )
            if values['status'] == "delete-success":
                page.append(
                    message.Success(
                        text=_(u"Widget successfully deleted.")
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
                        text=_(u"Something went wrong while saving the widget.")
                    )
                )
            if values['status'] == "edit-success":
                page.append(
                    message.Success(
                        text=_(u"Settings are successfully saved.")
                    )
                )

        widget_tabs = tab.DynamicTabs(
            'tabs-widget',
            title = _(u"Manage Widgets")
        )

        widget_tab = tab.TabItem(
            'tab-list',
            title = _(u"Widgets")
        )

        widget_table = WidgetTable()

        db_sel = sa.sql.select(
            [
                db_widget.c.id,
                db_widget.c.title,
                db_widget.c.description,
                sa.sql.expression.label(
                    'cmp_title',
                    db_component.c.title
                )
            ],
            db_widget.c.component_id == db_component.c.id
        )

        db_res = db_conn.execute(db_sel)

        # we don't want to make an extra sql request to count the rows, so we
        # catch them and check if the table is empty or not
        table_empty = True
        for row in db_res:
            table_empty = False
            widget_title=row[db_widget.c.title]
            if widget_title == None:
                widget_title = ""

            widget_description=row[db_widget.c.description]
            if widget_description == None:
                widget_description = ""

            component_title=row[db_component.c.title]
            if component_title == None:
                component_title = ""

            widget_table.append(
                [
                    widget_title,
                    component_title,
                    widget_description,
                    table.LinkCell(
                        value = _(u"Edit"),
                        url = pypoly.url(
                            action="edit",
                            values={
                                "id": row[db_widget.c.id]
                            },
                            scheme='widget'
                        )
                    ),
                    table.LinkCell(
                        value = _(u"Delete"),
                        url = pypoly.url(
                            action="delete",
                            values={
                                "id": row[db_widget.c.id]
                            },
                            scheme='widget'
                        )
                    )
                ]
            )

        if table_empty == True:
            widget_table.append(
                [
                    table.TextCell(
                        colspan=4,
                        value=_(u"No widgets found.")
                    )
                ]
            )

        widget_tab.append(widget_table)

        widget_tabs.append(widget_tab)

        form_tab = tab.TabItem(
            'tab-create',
            title = _(u"Create")
        )

        form_tab.append(form)

        widget_tabs.append(form_tab)

        page.append(widget_tabs)

        return page

    @pypoly.http.expose(
        routes = [
            dict(
                action = "delete",
                path = "delete/{id}",
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
    def delete(self, **values):
        widget_id = values['id']

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_widget = pypoly.tool.db_sa.meta.tables['widget']
        db_widget_config = pypoly.tool.db_sa.meta.tables['widget_config']

        db_sel = sa.sql.select(
            [
                db_widget.c.id,
                db_widget.c.title,
                db_widget.c.description
            ],
            db_widget.c.id == widget_id
        )

        db_res = db_conn.execute(db_sel)
        # ToDo: error handling
        db_data = db_res.fetchone()

        data = dict()
        data['title'] = db_data[db_widget.c.title]
        if db_data[db_widget.c.description] == None:
            data['description'] = ''
        else:
            data['description'] = db_data[db_widget.c.description]

        form = DeleteWidget(
            "delete",
            title=_(u"Delete widget"),
            action=pypoly.url(
                action='delete',
                values={
                    "id": widget_id
                },
                scheme='widget'
            ),
            _data=data
        )

        form.prepare(values)
        if form.is_submit() and form.validate():
            if form.is_clicked('ok'):
                #ToDo: use a session for rollback

                # delete widget
                db_delete = sa.sql.expression.delete(
                    db_widget,
                    db_widget.c.id == widget_id
                )

                db_res = db_conn.execute(db_delete)

                # delete widget preferences
                db_delete = sa.sql.expression.delete(
                    db_widget_config,
                    db_widget_config.c.widget_id == widget_id
                )

                db_conn.execute(db_delete)

                # Todo: better error checks
                if db_res.rowcount > 0:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "delete-success"
                            },
                            scheme='widget'
                        )
                    )
                else:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "delete-failed"
                            },
                            scheme='widget'
                        )
                    )

            else:
                # cancel delete
                raise pypoly.http.HTTPRedirect(
                    url=pypoly.url(
                        action='index',
                        values={
                            "status": "delete-canceled"
                        },
                        scheme='widget'
                    )
                )

        page = Webpage()
        page.append(form)

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
        widget_id = values['id']

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_widget = pypoly.tool.db_sa.meta.tables['widget']

        db_sel = sa.sql.select(
            [
                db_widget.c.id,
                db_widget.c.title,
                db_widget.c.description
            ],
            db_widget.c.id == widget_id
        )

        db_res = db_conn.execute(db_sel)
        # ToDo: error handling
        db_data = db_res.fetchone()

        prefs = pypoly.tool.tuvedi.get_widget_preferences(widget_id)

        data = dict(
            prefs=prefs
        )
        data['title'] = db_data[db_widget.c.title]
        if db_data[db_widget.c.description] == None:
            data['description'] = ''
        else:
            data['description'] = db_data[db_widget.c.description]

        form = EditWidget(
            "edit",
            title=_(u"Edit widget"),
            action=pypoly.url(
                action='edit',
                values={
                    "id": widget_id
                },
                scheme='widget'
            ),
            _data=data,
            _widget_id=widget_id
        )

        form.prepare(values)
        if form.is_submit() and form.validate():
            if form.is_clicked('save'):
                # save widget data
                db_update = db_widget.update().where(
                    db_widget.c.id==widget_id
                ).values(
                    title=form.get_value("title"),
                    description=form.get_value("description")
                )
                db_res = db_conn.execute(db_update)

                # save widget preferences
                prefs = {}
                for elem_name in form.get_element_names():
                    if elem_name != None:
                        if elem_name[:5] == "pref-":
                            prefs[elem_name[5:]] = form.get_value(elem_name)
                pypoly.tool.tuvedi.set_widget_preferences(
                    widget_id,
                    prefs
                )

                # ToDo: check for errors

                if db_res.rowcount > 0:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "edit-success"
                            },
                            scheme='widget'
                        )
                    )
                else:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "edit-failed"
                            },
                            scheme='widget'
                        )
                    )

            else:
                # cancel edit
                raise pypoly.http.HTTPRedirect(
                    url=pypoly.url(
                        action='index',
                        values={
                            "status": "edit-canceled"
                        },
                        scheme='widget'
                    )
                )

        page = Webpage()
        page.append(form)

        return page

    @pypoly.http.expose(
        routes = [
            dict(
                action = "edit_list",
                path = "edit-list/{id}/{pref_name}",
                requirements = {
                    "id": "\d+",
                    "pref_name": "\S+"
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
    def edit_list(self, **values):
        # convert params
        widget_id = values['id']
        pref_name = values['pref_name']

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_widget = pypoly.tool.db_sa.meta.tables['widget']
        db_widget_config = pypoly.tool.db_sa.meta.tables['widget_config']

        db_sel = sa.sql.select(
            [
                db_widget.c.id,
                db_widget.c.title,
                db_widget.c.description
            ],
            db_widget.c.id == widget_id
        )

        db_res = db_conn.execute(db_sel)
        # ToDo: error handling
        db_data = db_res.fetchone()

        prefs = pypoly.tool.tuvedi.get_widget_preferences(widget_id)

        data = dict(
            prefs=prefs
        )
        data['title'] = db_data[db_widget.c.title]
        if db_data[db_widget.c.description] == None:
            data['description'] = ''
        else:
            data['description'] = db_data[db_widget.c.description]

        form = EditPrefList(
            "edit",
            title=_(u"Edit widget"),
            action=pypoly.url(
                action='edit_list',
                values={
                    "id": widget_id,
                    "pref_name": pref_name
                },
                scheme='widget'
            ),
            _data=data,
            _pref_name=pref_name
        )

        form.prepare(values)
        if form.is_submit() and form.validate():
            if form.is_clicked('save'):
                # save widget preferences
                prefs = []
                for elem_name in form.get_element_names():
                    if elem_name[:5] == "pref-":
                        try:
                            if elem_name[5:8] != "new":
                                pref_id = int(elem_name[5:])
                                prefs.append(
                                    (
                                        pref_id,
                                        form.get_value(elem_name)
                                    )
                                )
                        except:
                            continue


                pypoly.tool.tuvedi.set_widget_preference_list(
                    widget_id,
                    pref_name,
                    prefs
                )

                # ToDo: check for errors

                if db_res.rowcount > 0:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='edit_list',
                            values={
                                "id": widget_id,
                                "pref_name": pref_name,
                                "status": "edit-success"
                            },
                            scheme='widget'
                        )
                    )
                else:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='edit_list',
                            values={
                                "id": widget_id,
                                "pref_name": pref_name,
                                "status": "edit-failed"
                            },
                            scheme='widget'
                        )
                    )
            elif form.is_clicked('delete'):
                pref_ids = []
                for elem_name in form.get_element_names():
                    if elem_name[:7] == "delete-" and \
                       form.get_value(elem_name) != None:
                        try:
                            if elem_name[7:] != "new":
                                # eid = entry id
                                pref_ids.append(
                                    dict(
                                        eid=int(elem_name[7:])
                                    )
                                )
                        except:
                            continue

                db_delete = db_widget_config.delete().where(
                    sa.sql.expression.and_(
                        db_widget_config.c.id == sa.sql.bindparam('eid'),
                        db_widget_config.c.name == pref_name,
                        db_widget_config.c.widget_id == widget_id
                    )
                )
                db_conn.execute(
                    db_delete,
                    pref_ids
                )

                raise pypoly.http.HTTPRedirect(
                    url=pypoly.url(
                        action='edit_list',
                        values={
                            "id": widget_id,
                            "pref_name": pref_name,
                            "status": "edit-failed"
                        },
                        scheme='widget'
                    )
                )


            else:
                # cancel edit
                raise pypoly.http.HTTPRedirect(
                    url=pypoly.url(
                        action='edit',
                        values={
                            "id": widget_id,
                            "status": "edit-canceled"
                        },
                        scheme='widget'
                    )
                )

        form_add = EditPrefListAddNew(
            "form-add",
            title=_(u"Add item"),
            action=pypoly.url(
                action='edit_list',
                values={
                    "id": widget_id,
                    "pref_name": pref_name
                },
                scheme='widget'
            ),
            _data=data,
            _pref_name=pref_name
        )

        form_add.prepare(values)
        if form_add.is_submit() and form_add.validate():
            if form_add.is_clicked('add'):
                prefs = []
                for elem_name in form_add.get_element_names():
                    if elem_name[:8] == "pref-new":
                        try:
                            prefs.append(
                                (
                                    None,
                                    form_add.get_value(elem_name)
                                )
                            )
                        except:
                            continue

                pypoly.tool.tuvedi.set_widget_preference_list(
                    widget_id,
                    pref_name,
                    prefs
                )

                raise pypoly.http.HTTPRedirect(
                    url=pypoly.url(
                        action='edit_list',
                        values={
                            "id": widget_id,
                            "pref_name": pref_name,
                            "status": "edit-success"
                        },
                        scheme='widget'
                    )
                )

        page = Webpage()
        page.append(form)
        page.append(form_add)

        return page
