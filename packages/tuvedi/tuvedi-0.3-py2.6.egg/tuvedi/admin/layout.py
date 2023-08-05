import sqlalchemy as sa

import pypoly
import pypoly.session

from pypoly.content.webpage import Webpage
from pypoly.content.webpage import tab, table, message
from pypoly.content.webpage.form import text, Form, button, input
from pypoly.content.webpage import table
from pypoly.content.webpage.form import list as form_list
from pypoly.http import auth

class LayoutTable(table.Table):
    def __init__(self, *args, **kwargs):
        table.Table.__init__(self, *args, **kwargs)

        self.header.append(
            [
                _(u"Title"),
                _(u"Template(Class name)"),
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

class CreateLayout(Form):
    def __init__(self, *args, **kwargs):
        data = kwargs['_data']
        del kwargs['_data']

        Form.__init__(self, *args, **kwargs)

        self.append(
            input.TextInput(
                'title',
                label=_(u"Title"),
                required = True
            )
        )

        self.append(
            text.Textarea(
                'description',
                label=_(u"Description")
            )
        )

        sel = form_list.DropdownList(
            'template_id',
            label=_(u"Template"),
            required = True
        )
        for template in data['templates']:
            sel_list = form_list.ListGroup(
                None,
                label=template['title']
            )
            for layout in template['layouts']:
                sel_list.append(
                    form_list.ListItem(
                        None,
                        label=layout['title'],
                        value="%d_%s" % (
                            template['id'],
                            layout['name']
                        )
                    )
                )
            sel.append(sel_list)

        self.append(sel)

        self.add_button(
            button.SubmitButton(
                'submit',
                label=_('Create'),
            )
        )

class DeleteLayout(Form):
    def __init__(self, *args, **kwargs):
        data = kwargs['_data']
        del kwargs['_data']

        Form.__init__(self, *args, **kwargs)

        self.append(
            input.TextInput(
                'title',
                label=_(u"Title"),
                readonly=True,
                value=data['title']
            )
        )

        self.append(
            text.Textarea(
                'description',
                label=_(u"Description"),
                readonly=True,
                value=data['description']
            )
        )

        self.add_button(
            button.SubmitButton(
                'yes',
                label=_(u"Yes, delete it"),
            )
        )

        self.add_button(
            button.SubmitButton(
                'no',
                label=_(u"NO, don't delete it"),
            )
        )

class EditLayout(Form):
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
        db_template = pypoly.tool.db_sa.meta.tables['template']
        db_layout = pypoly.tool.db_sa.meta.tables['layout']

        db_sel = sa.sql.select([
            db_template.c.id,
            db_template.c.title,
        ])

        db_res = db_conn.execute(db_sel)

        templates = []

        for row in db_res:
            templates.append(
                dict(
                    id = row[db_template.c.id],
                    name = row[db_template.c.title]
                )
            )

        data = dict(
            templates=pypoly.tool.tuvedi.get_templates_with_layouts()
        )

        form = CreateLayout(
            'layout',
            method='POST',
            title=_('Create layout'),
            action=pypoly.url(
                action='index',
                scheme='layout'
            ),
            _data=data
        )

        form.prepare(values)
        if form.is_submit() and form.validate():
            tmp = form.get_value("template_id").split("_",1)
            template_id = int(tmp[0])
            layout_name = tmp[1]

            db_ins = db_layout.insert().values(
                title=form.get_value("title"),
                description=form.get_value("description"),
                template_id=template_id,
                class_name=layout_name
            )
            db_conn.execute(db_ins)

            # ToDo: check for errors
            raise pypoly.http.HTTPRedirect(
                url=pypoly.url(
                    action='index',
                    values={
                        "status": "created"
                    },
                    scheme='layout'
                ),
            )


        page = Webpage()

        if "status" in values:
            if values['status'] == "created":
                page.append(
                    message.Success(
                        text=_(u"Layout successfully created.")
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
                        text=_(u"Something went wrong while deleting the Layout.")
                    )
                )
            if values['status'] == "delete-success":
                page.append(
                    message.Success(
                        text=_(u"Layout successfully deleted.")
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
                        text=_(u"Something went wrong while saving the layout.")
                    )
                )
            if values['status'] == "edit-success":
                page.append(
                    message.Success(
                        text=_(u"Settings are successfully saved.")
                    )
                )

        layout_tabs = tab.DynamicTabs(
            'tabs-layout',
            title = _(u"Manage Layouts")
        )

        layout_tab = tab.TabItem(
            'tab-list',
            title = _(u"Layouts")
        )

        layout_table = LayoutTable()

        db_sel = sa.sql.select(
            [
                db_layout.c.id,
                db_layout.c.title,
                db_layout.c.description,
                db_layout.c.class_name,
                sa.sql.expression.label(
                    'tpl_title',
                    db_template.c.title
                )
            ],
            db_layout.c.template_id == db_template.c.id
        )

        db_res = db_conn.execute(db_sel)

        # we don't want to make an extra sql request to count the rows, so we
        # catch them and check if the table is empty or not
        table_empty = True
        for row in db_res:
            table_empty = False
            layout_title=row[db_layout.c.title]
            if layout_title == None:
                layout_title = ""

            layout_description=row[db_layout.c.description]
            if layout_description == None:
                layout_description = ""

            layout_class_name=row[db_layout.c.class_name]
            if layout_class_name == None:
                layout_class_name = ""

            template_title=row[db_template.c.title]
            if template_title == None:
                template_title = ""

            layout_table.append(
                [
                    layout_title,
                    "%s (%s)" % (
                        template_title,
                        layout_class_name
                    ),
                    layout_description,
                    table.LinkCell(
                        value = _(u"Edit"),
                        url = pypoly.url(
                            action="edit",
                            values={
                                "id": row[db_layout.c.id]
                            },
                            scheme='layout'
                        )
                    ),
                    table.LinkCell(
                        value = _(u"Delete"),
                        url = pypoly.url(
                            action="delete",
                            values={
                                "id": row[db_layout.c.id]
                            },
                            scheme='layout'
                        )
                    )
                ]
            )

        if table_empty == True:
            layout_table.append(
                [
                    table.TextCell(
                        colspan=5,
                        value=_(u"No layouts found.")
                    )
                ]
            )

        layout_tab.append(layout_table)

        layout_tabs.append(layout_tab)

        form_tab = tab.TabItem(
            'tab-create',
            title = _(u"Create")
        )

        form_tab.append(form)

        layout_tabs.append(form_tab)

        page.append(layout_tabs)

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
        # convert params
        layout_id = values['id']

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_layout = pypoly.tool.db_sa.meta.tables['layout']

        db_sel = sa.sql.select(
            [
                db_layout.c.id,
                db_layout.c.title,
                db_layout.c.description
            ],
            db_layout.c.id == layout_id
        )

        db_res = db_conn.execute(db_sel)

        db_data = db_res.fetchone()

        data = dict()
        data['title'] = db_data[db_layout.c.title]
        if db_data[db_layout.c.description] == None:
            data['description'] = ''
        else:
            data['description'] = db_data[db_layout.c.description]

        form = DeleteLayout(
            'layout',
            method='POST',
            title=_(u"Delete Layout"),
            action=pypoly.url(
                action='delete',
                values={
                    "id": layout_id
                },
                scheme='layout'
            ),
            _data = data
        )

        form.prepare(values)
        if form.is_submit() and form.validate():
            if form.is_clicked("yes"):
                db_delete = sa.sql.expression.delete(
                    db_layout,
                    db_layout.c.id == layout_id
                )

                db_res = db_conn.execute(db_delete)

                if db_res.rowcount > 0:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "delete-success"
                            },
                            scheme='layout'
                        ),
                    )
                else:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "delete-failed"
                            },
                            scheme='layout'
                        ),
                    )
            else:
                raise pypoly.http.HTTPRedirect(
                    url=pypoly.url(
                        action='index',
                        values={
                            "status": "delete-canceled"
                        },
                        scheme='layout'
                    ),
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
        # convert params
        layout_id = values['id']

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_layout = pypoly.tool.db_sa.meta.tables['layout']

        db_sel = sa.sql.select(
            [
                db_layout.c.id,
                db_layout.c.title,
                db_layout.c.description
            ],
            db_layout.c.id == layout_id
        )

        db_res = db_conn.execute(db_sel)

        db_data = db_res.fetchone()

        data = dict()

        data['title'] = db_data[db_layout.c.title]
        if db_data[db_layout.c.description] == None:
            data['description'] = ''
        else:
            data['description'] = db_data[db_layout.c.description]

        form = EditLayout(
            'layout-edit',
            method='POST',
            title=_('Edit Layout'),
            action=pypoly.url(
                action='edit',
                values={
                    "id": layout_id
                },
                scheme='layout'
            ),
            _data=data
        )

        form.prepare(values)
        if form.is_submit() and form.validate():
            if form.is_clicked('save'):
                # update layout
                db_update = db_layout.update().where(
                    db_layout.c.id == layout_id
                ).values(
                    title=form.get_value("title"),
                    description=form.get_value("description")
                )
                db_res = db_conn.execute(db_update)

                if db_res.rowcount > 0:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "edit-success"
                            },
                            scheme='layout'
                        ),
                    )
                else:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "edit-failed"
                            },
                            scheme='layout'
                        ),
                    )
            else:
                # cancel
                raise pypoly.http.HTTPRedirect(
                    url=pypoly.url(
                        action='index',
                        values={
                            "status": "edit-canceled"
                        },
                        scheme='layout'
                    ),
                )

        page = Webpage()

        page.append(form)

        return page
