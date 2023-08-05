import sqlalchemy as sa

import pypoly
import pypoly.session

from pypoly.content.webpage import Webpage
from pypoly.content.webpage import tab, table, message
from pypoly.content.webpage.form import text, Form, Fieldset, button, input
from pypoly.content.webpage import table
from pypoly.content.webpage.form import list as form_list
from pypoly.http import auth

class PresentationTable(table.Table):
    def __init__(self, *args, **kwargs):
        table.Table.__init__(self, *args, **kwargs)

        self.header.append(
            [
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
        self.cols.append(table.LinkCell())
        self.cols.append(table.LinkCell())

class CreatePresentation(Form):
    def __init__(self, *args, **kwargs):
        layouts = kwargs['layouts']
        Form.__init__(self, *args, **kwargs)

        self.append(
            input.TextInput(
                'title',
                label=_('Title'),
                required = True
            )
        )

        self.append(
            text.Textarea(
                'description',
                label=_('Description')
            )
        )

        sel = form_list.DropdownList(
            'layout_id',
            required = True,
            label=_("Layout")
        )
        for layout in layouts:
            sel.append(
                form_list.ListItem(
                    None,
                    label=layout['title'],
                    value=layout['id']
                )
            )
        self.append(sel)

        self.add_button(
            button.SubmitButton(
                'submit',
                label=_('Create'),
            )
        )

class DeletePresentation(Form):
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
                label=_(u"NO, do not delete it"),
            )
        )

class EditPresentation(Form):
    def __init__(self, *args, **kwargs):
        data = kwargs['_data']
        del kwargs['_data']

        Form.__init__(self, *args, **kwargs)

        fieldset = Fieldset(
            title=_(u"Presentation")
        )

        fieldset.append(
            input.TextInput(
                'title',
                label=_(u"Title"),
                required=True,
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

        fieldset = Fieldset(
            title=_(u"Areas")
        )
        for area in data['areas']:
            sel = form_list.DropdownList(
                'area-%s' % area['name'],
                label=area['title']
            )
            sel.append(
                form_list.ListItem(
                    None,
                    label=_(u"No Widget"),
                    value="-1"
                )
            )
            sel.append(
                form_list.ListItem(
                    None,
                    label=u"---------------"
                )
            )
            for widget in data['widgets']:
                item = form_list.ListItem(
                    None,
                    label=widget['title'],
                    value=widget['id']
                )
                for tarea in data['areas_config']:
                    if tarea['name'] == area['name'] and \
                       widget['id'] == tarea['widget_id']:
                        item.selected = True
                sel.append(item)
            fieldset.append(sel)

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
        db_presentation = pypoly.tool.db_sa.meta.tables['presentation']
        db_layout = pypoly.tool.db_sa.meta.tables['layout']

        db_sel = sa.sql.select([
            db_layout.c.id,
            db_layout.c.title,
        ])

        db_res = db_conn.execute(db_sel)

        layouts = []

        for row in db_res:
            layouts.append(
                dict(
                    id = row[db_layout.c.id],
                    title = row[db_layout.c.title]
                )
            )

        form = CreatePresentation(
            'presentation',
            method='POST',
            title=_('Create Presentation'),
            action=pypoly.url(
                action='index',
                scheme='presentation'
            ),
            layouts = layouts
        )

        form.prepare(values)
        if form.is_submit() and form.validate():
            try:
                layout_id=int(
                    form.get_value("layout_id")
                )
            except:
                #ToDo: check for errors
                pass

            db_ins = db_presentation.insert().values(
                title=form.get_value("title"),
                description=form.get_value("description"),
                layout_id=layout_id,
                last_modified=sa.sql.expression.func.NOW()
            )
            db_conn.execute(db_ins)

            # ToDo: check if insert was successful
            raise pypoly.http.HTTPRedirect(
                url=pypoly.url(
                    action='index',
                    values={
                        "status": "created"
                    },
                    scheme='presentation'
                ),
            )

        page = Webpage()

        if "status" in values:
            if values['status'] == "created":
                page.append(
                    message.Success(
                        text=_(u"Presentation successfully created.")
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
                        text=_(u"Something went wrong while deleting the presentation.")
                    )
                )
            if values['status'] == "delete-success":
                page.append(
                    message.Success(
                        text=_(u"Presentation successfully deleted.")
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
                        text=_(u"Something went wrong while saving the presentation.")
                    )
                )
            if values['status'] == "edit-success":
                page.append(
                    message.Success(
                        text=_(u"Settings are successfully saved.")
                    )
                )

        presentation_tabs = tab.DynamicTabs(
            'tabs-main',
            title = _(u"Manage Presentations")
        )

        presentation_tab = tab.TabItem(
            'tab-list',
            title = _(u"Presentations")
        )

        presentation_table = PresentationTable()

        db_sel = sa.sql.select([
            db_presentation.c.id,
            db_presentation.c.title,
            db_presentation.c.description
        ])

        db_res = db_conn.execute(db_sel)

        # we don't want to make an extra sql request to count the rows, so we
        # catch them and check if the table is empty or not
        table_empty = True
        for row in db_res:
            table_empty = False
            presentation_title=row[db_presentation.c.title]
            if presentation_title == None:
                presentation_title = ""

            presentation_description=row[db_presentation.c.description]
            if presentation_description == None:
                presentation_description = ""
            presentation_table.append(
                [
                    presentation_title,
                    presentation_description,
                    table.LinkCell(
                        value = _(u"Edit"),
                        url = pypoly.url(
                            action = "edit",
                            scheme = 'presentation',
                            values={
                                "id": row[db_presentation.c.id]
                            }
                        )
                    ),
                    table.LinkCell(
                        value = _(u"Delete"),
                        url = pypoly.url(
                            action = "delete",
                            scheme = 'presentation',
                            values={
                                "id": row[db_presentation.c.id]
                            }
                        )
                    ),
            ])

        if table_empty == True:
            presentation_table.append(
                [
                    table.TextCell(
                        colspan=4,
                        value=_(u"No presentations found.")
                    )
                ]
            )

        presentation_tab.append(presentation_table)

        presentation_tabs.append(presentation_tab)

        form_tab = tab.TabItem(
            'tab-create',
            title = _(u"Create")
        )

        form_tab.append(form)

        presentation_tabs.append(form_tab)

        page.append(presentation_tabs)

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
        presentation_id = values['id']

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_presentation = pypoly.tool.db_sa.meta.tables['presentation']

        db_sel = sa.sql.select(
            [
                db_presentation.c.id,
                db_presentation.c.title,
                db_presentation.c.description
            ],
            db_presentation.c.id == presentation_id
        )

        db_res = db_conn.execute(db_sel)

        db_data = db_res.fetchone()

        data = dict()
        data['title'] = db_data[db_presentation.c.title]
        if db_data[db_presentation.c.description] == None:
            data['description'] = ''
        else:
            data['description'] = db_data[db_presentation.c.description]

        form = DeletePresentation(
            'presentation',
            method='POST',
            title=_(u"Delete Presentation"),
            action=pypoly.url(
                action='delete',
                values={
                    "id": presentation_id
                },
                scheme='presentation'
            ),
            _data = data
        )

        form.prepare(values)
        if form.is_submit() and form.validate():
            if form.is_clicked("yes"):
                db_delete = sa.sql.expression.delete(
                    db_presentation,
                    db_presentation.c.id == presentation_id
                )

                db_res = db_conn.execute(db_delete)

                if db_res.rowcount > 0:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "delete-success"
                            },
                            scheme='presentation'
                        ),
                    )

                else:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "delete-failed"
                            },
                            scheme='presentation'
                        ),
                    )
            else:
                raise pypoly.http.HTTPRedirect(
                    url=pypoly.url(
                        action='index',
                        values={
                            "status": "delete-canceled"
                        },
                        scheme='presentation'
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
        presentation_id = values['id']

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_presentation = pypoly.tool.db_sa.meta.tables['presentation']
        db_widget = pypoly.tool.db_sa.meta.tables['widget']

        db_sel = sa.sql.select([
            db_widget.c.id,
            db_widget.c.title
        ])

        db_res = db_conn.execute(db_sel)

        widgets = []

        for row in db_res:
            widgets.append(
                dict(
                    id = row[db_widget.c.id],
                    title = row[db_widget.c.title]
                )
            )

        areas = pypoly.tool.tuvedi.get_presentation_areas(
            presentation_id
        )
        areas_config = pypoly.tool.tuvedi.get_presentation_areas_config(
            presentation_id
        )

        #get_template_areas_with_infos
        db_sel = sa.sql.select(
            [
                db_presentation.c.id,
                db_presentation.c.title,
                db_presentation.c.description
            ],
            db_presentation.c.id == presentation_id
        )

        db_res = db_conn.execute(db_sel)

        db_data = db_res.fetchone()

        data = dict(
            widgets=widgets,
            areas=areas,
            areas_config=areas_config
        )

        data['title'] = db_data[db_presentation.c.title]
        if db_data[db_presentation.c.description] == None:
            data['description'] = ''
        else:
            data['description'] = db_data[db_presentation.c.description]

        form = EditPresentation(
            'presentation',
            method='POST',
            title=_('Edit Presentation'),
            action=pypoly.url(
                action='edit',
                values={
                    "id": presentation_id
                },
                scheme='presentation'
            ),
            _data=data
        )

        form.prepare(values)
        if form.is_submit() and form.validate():
            if form.is_clicked('save'):
                # update presentation
                db_update = db_presentation.update().where(
                    db_presentation.c.id==presentation_id
                ).values(
                    title=form.get_value("title"),
                    description=form.get_value("description")
                )
                db_res = db_conn.execute(db_update)

                # update areas
                conf = {}
                for elem_name in form.get_element_names():
                    if elem_name[:5] == "area-":
                        value = form.get_value(elem_name)
                        if value < 0:
                            conf[elem_name[5:]] = None
                        else:
                            conf[elem_name[5:]] = form.get_value(elem_name)

                pypoly.tool.tuvedi.set_presentation_areas_config(
                    presentation_id,
                    conf
                )

                #ToDo: use sessions
                if db_res.rowcount > 0:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "edit-success"
                            },
                            scheme='presentation'
                        ),
                    )
                else:
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "edit-failed"
                            },
                            scheme='presentation'
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
                        scheme='presentation'
                    ),
                )

        page = Webpage()

        page.append(form)

        return page
