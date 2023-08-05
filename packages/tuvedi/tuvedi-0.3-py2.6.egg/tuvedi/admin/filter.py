import sqlalchemy as sa

import pypoly
import pypoly.session
from pypoly.content.webpage import Webpage, tab, table
from pypoly.content.webpage.form import text, Form, button, input
from pypoly.content.webpage.form import list as form_list

class FilterTable(table.Table):
    def __init__(self, *args, **kwargs):
        table.Table.__init__(self, *args, **kwargs)

        self.cols.append(table.LinkCell())
        self.cols.append(table.TextCell())


class FilterForm(Form):
    def __init__(self, *args, **kwargs):
        devices = kwargs['devices']
        Form.__init__(self, *args, **kwargs)

        name = input.TextInput(
            'name',
            label=_('Name'),
            required = True
        )
        self.append(name)

        description = text.Textarea(
            'description',
            label=_('Description')
        )
        self.append(description)

        rule = input.TextInput(
            'rule',
            label=_('Rule'),
            required = True
        )
        self.append(rule)

        sel = form_list.DropdownList(
            'device',
            required = True
        )
        for device in devices:
            sel.append(
                form_list.ListItem(
                    None,
                    label=device['name'],
                    value=device['id']
                )
            )
        self.append(sel)


class AddFilter(FilterForm):
    def __init__(self, *args, **kwargs):
        FilterForm.__init__(self, *args, **kwargs)
        self.add_button(
            button.SubmitButton(
                'submit',
                label=_('Create'),
            )
        )

class EditFilter(FilterForm):
    def __init__(self, *args, **kwargs):
        FilterForm.__init__(self, *args, **kwargs)

        device_id = input.TextInput(
            'device_id',
            hidden=True
        )
        form.append(device_id)

        self.add_button(
            button.SubmitButton(
                'submit',
                label=_('Save'),
            )
        )

class Controller(object):
    _pypoly_config = {
        "session.mode": pypoly.session.MODE_READONLY
    }

    @pypoly.http.expose()
    def index(self, **values):
        pypoly.log.debug(values)

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_filter = pypoly.tool.db_sa.meta.tables['filter']
        db_device = pypoly.tool.db_sa.meta.tables['device']

        db_sel = sa.sql.select([
            db_device.c.id,
            db_device.c.name,
        ])

        db_res = db_conn.execute(db_sel)

        devices = []

        for row in db_res:
            devices.append(
                dict(
                    id = row[db_device.c.id],
                    name = row[db_device.c.name]
                )
            )

        form = AddFilter(
            'test',
            method='POST',
            title=_('All texts bjects.'),
            action=pypoly.url(
                action='index',
                scheme='filter'
            ),
            devices = devices
        )

        form.prepare(values)
        if form.is_submit() and form.validate():
            db_ins = db_filter.insert().values(
                name=form.get_value("name"),
                description=form.get_value("description"),
                rule=form.get_value("rule"),
                device_id=form.get_value("device")
            )
            db_conn.execute(db_ins)

        page = Webpage()

        filter_tabs = tab.DynamicTabs(
            'tabs1',
            title = u'foo'
        )

        filter_tab = tab.TabItem(
            'tab1',
            title = u'test'
        )

        filter_table = FilterTable()

        db_sel = sa.sql.select([
            db_filter.c.id,
            db_filter.c.name,
            db_filter.c.description
        ])

        db_res = db_conn.execute(db_sel)

        for row in db_res:
            filter_table.append([
                table.LinkCell(
                    value = row[db_filter.c.name],
                    url = pypoly.url(
                        action="datecell",
                        scheme='table_cells'
                    )
                ),
                row[db_filter.c.description]
            ])

        filter_tab.append(filter_table)

        filter_tabs.append(filter_tab)

        form_tab = tab.TabItem(
            'tab2',
            title = u'test'
        )

        form_tab.append(form)

        filter_tabs.append(form_tab)

        page.append(filter_tabs)

        return page
