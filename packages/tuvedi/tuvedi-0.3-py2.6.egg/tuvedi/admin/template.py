import os
import tarfile
from xml.dom import minidom

import sqlalchemy as sa

import pypoly
import pypoly.session

from pypoly.content import Webpage
from pypoly.content.webpage import tab, table, message
from pypoly.content.webpage.form import text, Form, button, input, TableForm
from pypoly.content.webpage import table
from pypoly.http import auth

class TemplateTable(table.Table):
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

class DeleteForm(TableForm):
    def __init__(self, *args, **kwargs):
        TableForm.__init__(self, *args, **kwargs)

        self.header.append(
            [
                _(u"Name"),
                _(u"Value"),
            ]
        )

        self.cols.append(table.TextCell())
        self.cols.append(table.TextCell())

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

class InfoTable(table.Table):
    def __init__(self, *args, **kwargs):
        table.Table.__init__(self, *args, **kwargs)

        self.header.append(
            [
                _(u"Name"),
                _(u"Value"),
            ]
        )

        self.cols.append(table.TextCell())
        self.cols.append(table.TextCell())

class UploadTemplate(Form):
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.enctype = "multipart/form-data"
        self.append(
            input.FileInput(
                'file',
                label=_('File'),
                required = True
            )
        )

        self.append(
            button.Checkbox(
                'overwrite',
                label=_(u"Overwrite")
            )
        )

        self.add_button(
            button.SubmitButton(
                'submit',
                label=_('Upload'),
            )
        )

class Controller(object):
    _pypoly_config = {
        "session.mode": pypoly.session.MODE_READONLY
    }

    @pypoly.http.expose(
        auth = auth.group("tuvedi.admin")
    )
    def index(self, **values):
        pypoly.log.debug(values)

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_template = pypoly.tool.db_sa.meta.tables['template']

        form = UploadTemplate(
            'upload',
            method='POST',
            title=_('Upload Template'),
            action=pypoly.url(
                action='index',
                scheme='template'
            )
        )

        form.prepare(values)
        if form.is_submit() and form.validate():
            tar_fp = tarfile.open(fileobj = form.get_element_by_name("file").file)
            if tar_fp == None:
                raise pypoly.http.HTTPRedirect(
                    url=pypoly.url(
                        action='index',
                        values={
                            "status": "error-extracting"
                        },
                        scheme='template'
                    ),
                )
            xml_fp = tar_fp.extractfile("info.xml")
            if xml_fp:
                # ToDo: check for errors
                xml_file = minidom.parse(xml_fp)
                doc = xml_file.documentElement
                info = pypoly.tool.tuvedi.get_xml_information(doc)

                db_sel = sa.sql.select(
                    [
                        db_template.c.id
                    ],
                    db_template.c.name == info['name']
                )

                db_res = db_conn.execute(db_sel)

                db_data = db_res.fetchone()
                if db_data == None:
                    db_ins = db_template.insert().values(
                        name=info['name'],
                        title=info['title'],
                        description=info['description']
                    )
                    db_conn.execute(db_ins)

                    # ToDo: Change this, it only works with sqlite
                    db_sel = sa.sql.select([sa.sql.func.last_insert_rowid()])
                    db_res = db_conn.execute(db_sel)
                    last_id = db_res.fetchone()[0]

                    pypoly.tool.tuvedi.extract_template(
                        last_id,
                        tar_fp
                    )
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "created"
                            },
                            scheme='template'
                        ),
                    )
                elif db_data[0] > 0 and form.get_value('overwrite') != None:
                    pypoly.tool.tuvedi.extract_template(
                        db_data[db_template.c.id],
                        tar_fp
                    )
                    raise pypoly.http.HTTPRedirect(
                        url=pypoly.url(
                            action='index',
                            values={
                                "status": "overwritten"
                            },
                            scheme='template'
                        )
                    )

                raise pypoly.http.HTTPRedirect(
                    url=pypoly.url(
                        action='index',
                        values={
                            "status": "exists"
                        },
                        scheme='template'
                    )
                )

        page = Webpage()

        if "status" in values:
            if values['status'] == "created":
                page.append(
                    message.Success(
                        text=_(u"Template successfully created.")
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
                        text=_(u"Something went wrong while deleting the template.")
                    )
                )
            if values['status'] == "delete-success":
                page.append(
                    message.Success(
                        text=_(u"Template successfully deleted.")
                    )
                )
            if values['status'] == "error-extracting":
                page.append(
                    message.Error(
                        text=_(u"There was an error extracting the template")
                    )
                )

        template_tabs = tab.DynamicTabs(
            'tabs-template',
            title = _(u"Manage Templates")
        )

        template_tab = tab.TabItem(
            'tab-list',
            title = _(u"Templates")
        )

        template_table = TemplateTable()

        db_sel = sa.sql.select([
            db_template.c.id,
            db_template.c.name,
            db_template.c.title,
            db_template.c.description
        ])

        db_res = db_conn.execute(db_sel)

        # we don't want to make an extra sql request to count the rows, so we
        # catch them and check if the table is empty or not
        table_empty = True
        for row in db_res:
            table_empty = False
            template_name=row[db_template.c.name]
            if template_name == None:
                template_name = ""

            template_title=row[db_template.c.title]
            if template_title == None:
                template_title = ""

            template_description=row[db_template.c.description]
            if template_description == None:
                template_description = ""

            template_table.append(
                [
                    "%s (%s)" % (
                        template_title,
                        template_name
                    ),
                    template_description,
                    table.LinkCell(
                        value = _(u"Info"),
                        url = pypoly.url(
                            action="info",
                            values={
                                "id": row[db_template.c.id]
                            },
                            scheme="template"
                        )
                    ),
                    table.LinkCell(
                        value = _(u"Delete"),
                        url = pypoly.url(
                            action="delete",
                            values={
                                "id": row[db_template.c.id]
                            },
                            scheme="template"
                        )
                    )
                ]
            )

        if table_empty == True:
            template_table.append(
                [
                    table.TextCell(
                        colspan=4,
                        value=_(u"No template found.")
                    )
                ]
            )

        template_tab.append(template_table)

        template_tabs.append(template_tab)

        form_tab = tab.TabItem(
            'tab2',
            title = u"Upload"
        )

        form_tab.append(form)

        template_tabs.append(form_tab)

        page.append(template_tabs)

        return page

    def _append_info_to_table(self, info, info_table):
        info_table.append(
            [
                _(u"Title"),
                info['title']
            ]
        )

        info_table.append(
            [
                _(u"Version"),
                info['version']
            ]
        )

        info_table.append(
            [
                _(u"Description"),
                info['description']
            ]
        )

        info_table.append(
            [
                _(u"Author(s)"),
                ", ".join(
                    info['authors']
                )
            ]
        )

        return info_table

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
        auth = auth.group("tuvedi.admin")
    )
    def delete(self, **values):
        template_id = values['id']

        info = pypoly.tool.tuvedi.get_template_information(template_id)

        delete_form = DeleteForm(
            'delete',
            action=pypoly.url(
                action="delete",
                scheme="template",
                values={
                    "id": template_id
                }
            ),
            title=("Delete Template: %(title)s (%(name)s)") % dict(
                title=info['title'],
                name=info['name']
            )
        )

        delete_form = self._append_info_to_table(
            info,
            delete_form
        )

        delete_form.prepare(values)

        if delete_form.is_submit() and delete_form.validate():
            if delete_form.is_clicked('yes'):
                pypoly.tool.tuvedi.delete_template(template_id)

                # ToDo: check for errors
                raise pypoly.http.HTTPRedirect(
                    url=pypoly.url(
                        action='index',
                        values={
                            "status": "delete-success"
                        },
                        scheme='template'
                    ),
                )
            else:
                raise pypoly.http.HTTPRedirect(
                    url=pypoly.url(
                        action='index',
                        values={
                            "status": "delete-canceled"
                        },
                        scheme='template'
                    ),
                )

        page = Webpage()
        page.append(delete_form)

        return page



    @pypoly.http.expose(
        routes = [
            dict(
                action = "info",
                path = "info/{id}",
                requirements = {
                    "id": "\d+"
                },
                types = {
                    "id": int
                }
            )
        ],
        auth = auth.group("tuvedi.admin")
    )
    def info(self, **values):
        template_id = values['id']

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_template = pypoly.tool.db_sa.meta.tables['template']


        info = pypoly.tool.tuvedi.get_template_information(template_id)

        info_table = InfoTable(
            title=_("Template Info: %(title)s (%(name)s)") % dict(
                title=info['title'],
                name=info['name']
            )
        )

        info_table = self._append_info_to_table(
            info,
            info_table
        )

        page = Webpage()
        page.append(info_table)

        return page
