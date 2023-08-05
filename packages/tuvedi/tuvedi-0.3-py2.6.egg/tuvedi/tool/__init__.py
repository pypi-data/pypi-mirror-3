#
# TuVedi - Interactive Information System
#
# Copyright (c) 2011 Philipp Seidel
#
# Licensed under the GPLv3 (LICENSE-GPLv3)
#

"""
This is the TuVedi PyPoly tool. It provides some use full function that are
used in the Admin interface.
"""

import datetime
import time
import os
import shutil
from xml.dom.minidom import parse
from xml.dom import minidom

import sqlalchemy as sa

import pypoly


class Main(object):
    def init(self):
        pypoly.config.add('template.path', 'tpl_test')
        pypoly.config.add('component.path', 'cmp_test')

    def start(self):
        pypoly.tool.register('tuvedi', TuVedi())


class TuVedi(object):
    def __init__(self):
        self.component_handlers = dict()
        # default device prefs
        self.device_prefs = dict(
            animation_speed="fast",
            animation_type="fade"
        )

    def delete_component(self, component_id):
        """
        Remove a component.

        - Delete component folder
        - Delete component from database

        :param component_id: Component ID
        :type component_id: Integer
        """
        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_component = pypoly.tool.db_sa.meta.tables['component']

        cmp_path = pypoly.config.get('component.path')

        path = os.path.join(
            cmp_path,
            str(component_id)
        )

        shutil.rmtree(path)

        db_delete = sa.sql.expression.delete(
            db_component,
            db_component.c.id == component_id
        )

        db_conn.execute(db_delete)

    def delete_template(self, template_id):
        """
        Remove a template.

        - Delete template folder
        - Delete template from database

        :param template_id: Template ID
        :type template_id: Integer
        """
        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_template = pypoly.tool.db_sa.meta.tables['template']

        tpl_path = pypoly.config.get('template.path')

        path = os.path.join(
            tpl_path,
            str(template_id)
        )

        shutil.rmtree(path)

        db_delete = sa.sql.expression.delete(
            db_template,
            db_template.c.id == template_id
        )

        db_conn.execute(db_delete)

    def extract_component(self, component_id, tar_fp):
        """
        Extract a component file.

        :param component_id: The component ID
        :type component_id: Integer
        :param tar_fp: File pointer of the tar file
        :type tar_fp: file pointer
        """
        cmp_path = pypoly.config.get('component.path')

        path = os.path.join(
            cmp_path,
            str(component_id)
        )

        if not os.path.exists(path):
            os.mkdir(path)
        tar_fp.extractall(path=path)
        # ToDo: check for errors
        return True

    def extract_template(self, template_id, tar_fp):
        """
        Extract the files from the template archive.

        :param template_id: Template id
        :type template_id: Integer
        :param tar_fp: File pointer of the template archive
        :type tar_fp: file pointer
        """
        tpl_path = pypoly.config.get('template.path')

        path = os.path.join(
            tpl_path,
            str(template_id)
        )
        if not os.path.exists(path):
            os.mkdir(path)
        tar_fp.extractall(path=path)
        # ToDo: check for errors
        return True

    def get_component_information(self, component_id):
        """
        Get information for a component by its ID.

        :see: tuvedi_tool.get_xml_information

        :param component_id: The ID of the component
        :type component_id: Integer
        :return: Dict with information
        :rtype: Dict
        :ToDo: check for errors
        """
        cmp_path = pypoly.config.get('component.path')

        filename = os.path.join(
            cmp_path,
            str(component_id),
            "info.xml"
        )

        xml_fp = open(filename)
        if xml_fp:
            # ToDo: check for errors
            xml_file = minidom.parse(xml_fp)
            doc = xml_file.documentElement
            return pypoly.tool.tuvedi.get_xml_information(doc)

    def get_component_with_prefs(self, component_id, prefs):
        """
        Load a component and add the given preferences

        :param component_id: Component ID
        :type component_id: Integer
        :param prefs: Preferences
        :type prefs: Dict
        :return: Configuration
        :rtype: Dict
        """
        cmp_path = pypoly.config.get('component.path')

        filename = os.path.join(
            cmp_path,
            str(component_id),
            "info.xml"
        )

        xml_file = parse(filename)

        params = dict()

        component = dict(
            id=component_id
        )

        doc_element = xml_file.documentElement
        for child in doc_element.childNodes:
            if child.nodeName == "content":
                component['type'] = child.getAttribute("type")
                component['target'] = child.getAttribute("target")
                if component['type'] == "url":
                    for param_node in child.getElementsByTagName("param"):
                        if param_node.hasAttribute("name"):
                            param_name = param_node.getAttribute("name")
                        if param_node.hasAttribute("value"):
                            param_value = param_node.getAttribute("value")
                        if param_name == "url":
                            if param_value[:5] == "pref:":
                                params["url"] = prefs[param_value[5:]]
                            else:
                                params["url"] = param_value
                elif component['type'] == "jquery":
                    params = prefs
                    component['js_name'] = child.getAttribute("js_name")

        component['prefs'] = params

        info = self.get_component_information(component_id)

        if info['name'] in self.component_handlers:
            func = self.component_handlers[info['name']]
            # ToDo: more checks
            component = func(component)

        return component

    def get_component_preferences(self, component_id):
        """
        Get available preferences from component file.

        :param component_id: A component ID
        :type component_id: Integer
        :return: List of prefs
        :rtype: List
        """
        def _parse_prefs(pref_node):
            pref = dict()
            if pref_node.hasAttribute("name"):
                pref['name'] = pref_node.getAttribute("name")
            else:
                #ToDo: error handling
                return None
            if pref_node.hasAttribute("type"):
                pref['type'] = pref_node.getAttribute("type")
            else:
                #ToDo: error handling
                return None
            if pref_node.hasAttribute("title"):
                pref['title'] = pref_node.getAttribute("title")
            else:
                #ToDo: error handling
                return None
            if pref_node.hasAttribute("value"):
                value = pref_node.getAttribute("value")
            else:
                value = ''
            if pref_node.hasAttribute("list"):
                tmp = pref_node.getAttribute("list")
                if tmp.lower() == "true" or tmp == "0":
                    pref['list'] = True
                else:
                    pref['list'] = False
            else:
                pref['list'] = False

            if pref_node.hasAttribute("multiline"):
                tmp = pref_node.getAttribute("multiline")
                if tmp.lower() == "true" or tmp == "0":
                    pref['multiline'] = True
                else:
                    pref['multiline'] = False
            else:
                pref['multiline'] = False

            if pref['list'] == True:
                pref['value'] = []
            else:
                if pref['type'] == "string":
                    pref['value'] = value
                elif pref['type'] == "integer":
                    try:
                        pref['value'] = int(value)
                    except:
                        pref['value'] = 0
                elif pref['type'] == "boolean":
                    if value == "1":
                        pref['value'] = True
                    else:
                        pref['value'] = False

            return pref

        cmp_path = pypoly.config.get('component.path')

        filename = os.path.join(
            cmp_path,
            str(component_id),
            "info.xml"
        )

        xml_file = parse(filename)

        prefs = []
        doc_element = xml_file.documentElement
        for child in doc_element.childNodes:
            if child.nodeName == "preferences":
                for pref_node in child.childNodes:
                    if pref_node.nodeName == "pref":
                        pref = _parse_prefs(pref_node)
                        if pref != None:
                            prefs.append(pref)
                    elif pref_node.nodeName == "pref-group":
                        pref = dict()
                        if pref_node.hasAttribute("name"):
                            pref['name'] = pref_node.getAttribute("name")
                        else:
                            #ToDo: error handling
                            continue
                        if pref_node.hasAttribute("title"):
                            pref['title'] = pref_node.getAttribute("title")
                        else:
                            #ToDo: error handling
                            continue
                        pref['type'] = 'group'
                        pref['prefs'] = []
                        pref['value'] = []
                        for sub_node in pref_node.getElementsByTagName("pref"):
                            sub_pref = _parse_prefs(sub_node)
                            if sub_pref != None:
                                pref['prefs'].append(sub_pref)

                        prefs.append(pref)

        return prefs

    def get_device_preferences(self, device_id):
        """
        Get preferences for a device.

        :param device_id: A device ID
        :type device_id: Integer
        :return: Dict of prefs
        :rtype: Dict
        """
        prefs = {}

        db_conn = pypoly.tool.db_sa.connect()
        db_device_conf = pypoly.tool.db_sa.meta.tables['device_config']

        db_sel = sa.sql.select(
            [
                db_device_conf.c.name,
                db_device_conf.c.value
            ],
            db_device_conf.c.device_id == device_id,
        )

        db_res = db_conn.execute(db_sel)

        for row in db_res:
            prefs[row[db_device_conf.c.name]] = row[db_device_conf.c.value]

        for name, value in self.device_prefs.items():
            if not name in prefs:
                prefs[name] = value

        return prefs

    def get_javascript(self, component_id):
        """
        Get the javascript from the plugin.

        :param component_id: The component ID
        :type component_id: Integer
        :return: Return the JavaScript
        :rtype: String
        :ToDo: Check if file exists
        """
        cmp_path = pypoly.config.get('component.path')

        filename = os.path.join(
            cmp_path,
            str(component_id),
            "content.js"
        )

        fp = open(filename)
        data = fp.read().decode("utf-8")

        return data

    def get_layouts(self, template_id):
        """
        Get all layouts from a template.

        :param template_id: ID of the template to get the layouts from
        :type template_id: Integer
        :return: Layout list
        :rtype: List
        """
        tpl_path = pypoly.config.get('template.path')

        filename = os.path.join(
            tpl_path,
            str(template_id),
            "info.xml"
        )

        xml_file = parse(filename)

        layouts = []
        doc_element = xml_file.documentElement
        for child in doc_element.childNodes:
            if child.nodeName == "layouts":
                for layout_node in child.getElementsByTagName("layout"):
                    layouts.append(
                        {
                            "name": layout_node.getAttribute("name"),
                            "title": layout_node.getAttribute("title")
                        }
                    )

        return layouts

    def get_presentation_areas(self, presentation_id):
        """
        Gat all available areas of a presentation.

        :param presentation_id: ID of the presentation
        :type presentation_id: Integer
        :return: List of areas
        :rtype: List
        """
        # check param type
        if type(presentation_id) != int:
            try:
                presentation_id = int(presentation_id)
            except:
                return None

        db_conn = pypoly.tool.db_sa.connect()
        db_pres_areas = pypoly.tool.db_sa.meta.tables['presentation_areas']
        db_presentation = pypoly.tool.db_sa.meta.tables['presentation']
        db_layout = pypoly.tool.db_sa.meta.tables['layout']

        db_sel = sa.sql.select(
            [
                db_layout.c.template_id,
                db_layout.c.class_name
            ],
            sa.sql.expression.and_(
                db_presentation.c.id == presentation_id,
                db_presentation.c.layout_id == db_layout.c.id
            )
        )

        db_res = db_conn.execute(db_sel)
        # ToDo: error handling
        db_data = db_res.fetchone()

        areas_available = self.get_template_areas_available(
            db_data[db_layout.c.template_id],
            db_data[db_layout.c.class_name]
        )
        tpl_path = pypoly.config.get('template.path')

        filename = os.path.join(
            tpl_path,
            str(db_data[db_layout.c.template_id]),
            "info.xml"
        )

        xml_file = parse(filename)

        areas = []
        doc_element = xml_file.documentElement

        for child in doc_element.childNodes:
            if child.nodeName == "areas":
                for area_node in child.getElementsByTagName("area"):
                    name = area_node.getAttribute("name")
                    if name in areas_available:
                        title = area_node.getAttribute("title")
                        description = area_node.getAttribute("description")
                        areas.append(
                            dict(
                                name=name,
                                title=title,
                                description=description
                            )
                        )

        return areas

    def get_presentation_areas_config(self, presentation_id):
        """
        Get configuration for all areas of a presentation.

        :param presentation_id: ID of the presentation
        :type presentation_id: Integer
        :return: List of areas with configuration
        :rtype: List
        """
        # check param type
        if type(presentation_id) != int:
            try:
                presentation_id = int(presentation_id)
            except:
                return None

        db_conn = pypoly.tool.db_sa.connect()
        db_pres_areas = pypoly.tool.db_sa.meta.tables['presentation_areas']
        db_presentation = pypoly.tool.db_sa.meta.tables['presentation']
        db_layout = pypoly.tool.db_sa.meta.tables['layout']
        db_widget = pypoly.tool.db_sa.meta.tables['widget']

        db_sel = sa.sql.select(
            [
                db_layout.c.template_id,
                db_layout.c.class_name
            ],
            sa.sql.expression.and_(
                db_presentation.c.id == presentation_id,
                db_presentation.c.layout_id == db_layout.c.id
            )
        )

        db_res = db_conn.execute(db_sel)
        # ToDo: error handling
        db_data = db_res.fetchone()

        areas_available = self.get_template_areas_available(
            db_data[db_layout.c.template_id],
            db_data[db_layout.c.class_name]
        )

        db_sel = sa.sql.select(
            [
                db_pres_areas.c.name,
                db_pres_areas.c.widget_id,
                db_widget.c.last_modified
            ],
            sa.sql.expression.and_(
                db_pres_areas.c.presentation_id == presentation_id,
                db_pres_areas.c.widget_id == db_widget.c.id
            )
        )

        db_res = db_conn.execute(db_sel)

        tmp_areas = dict()

        for row in db_res:
            tmp_name = row[db_pres_areas.c.name]
            tmp_areas[tmp_name] = dict(
                name=tmp_name,
                widget_id=row[db_pres_areas.c.widget_id],
                last_modified=row[db_widget.c.last_modified]
            )

        areas = []
        for area in areas_available:
            if area in tmp_areas:
                areas.append(tmp_areas[area])
            else:
                areas.append(
                    dict(
                        name=area,
                        widget_id=None,
                        last_modified=datetime.datetime.now()
                    )
                )

        return areas

    def get_presentation_by_device(
        self,
        device_id=None,
        device_name=None,
        presentation=None
    ):
        """
        Get a complete presentation for a device.

        :param device_id: The device ID
        :type device_id: Integer
        :param device_name: Name of the device
        :type device_name: String
        :param presentation: An existing presentation
        :type presentation: Dict
        :return: A complete presentation configuration
        :rtype: Dict
        """
        # check param type
        if device_id != None and type(device_id) != int:
            try:
                device_id = int(device_id)
            except:
                return None

        if device_name != None and type(device_name) != str:
            try:
                device_name = str(device_name)
            except:
                return None

        db_conn = pypoly.tool.db_sa.connect()
        db_timetable = pypoly.tool.db_sa.meta.tables['timetable']
        db_device = pypoly.tool.db_sa.meta.tables['device']
        db_layout = pypoly.tool.db_sa.meta.tables['layout']
        db_presentation = pypoly.tool.db_sa.meta.tables['presentation']
        db_areas = pypoly.tool.db_sa.meta.tables['presentation_areas']
        db_widget = pypoly.tool.db_sa.meta.tables['widget']

        date_cur = datetime.datetime.now()

        where = [
            db_timetable.c.start <= date_cur,
            db_timetable.c.end > date_cur,
            db_timetable.c.presentation_id == db_presentation.c.id,
            db_presentation.c.layout_id == db_layout.c.id
        ]

        if device_id != None:
            where.append(db_timetable.c.device_id == device_id)
        elif device_name != None:
            where.append(db_timetable.c.device_id == db_device.c.id)
            where.append(db_device.c.name == device_name)

        db_sel = sa.sql.select(
            [
                db_timetable.c.presentation_id,
                db_layout.c.template_id,
                db_layout.c.class_name
            ],
            sa.sql.and_(*where)
        ).order_by(
            sa.sql.desc(db_timetable.c.start)
        ).limit(1)

        db_res = db_conn.execute(db_sel)
        # ToDo: check if data is available
        db_data = db_res.fetchone()
        presentation_id = db_data[db_timetable.c.presentation_id]
        template_id = db_data[db_layout.c.template_id]
        class_name = db_data[db_layout.c.class_name]

        areas_config = self.get_presentation_areas_config(presentation_id)

        pres_areas = {}

        if 'areas' in presentation and \
           type(presentation['areas']) == dict:
            areas_cur = presentation['areas']
        else:
            areas_cur = dict()

        for area in areas_config:
            # no widget selected for this area
            if area['widget_id'] == None:
                continue

            area_name = area['name']
            if area_name in areas_cur:
                try:
                    last_modified = int(
                        time.mktime(
                            area['last_modified'].timetuple()
                        )
                    )

                    last_cur = int(areas_cur[area_name]['last_modified'])

                    # widget not modified, set some vars, but don't send
                    # preferences
                    if last_modified <= last_cur and \
                       areas_cur[area_name]['widget_id'] == area['widget_id']:
                        pres_areas[area['name']] = areas_cur[area_name]
                        pres_areas[area['name']]['modified'] = False
                        continue
                except:
                    pypoly.log.error("Error parsing the submitted data")

            widget_prefs = self.get_widget_preferences(area['widget_id'])
            prefs = dict()
            for pref in widget_prefs:
                if "list" in pref and \
                   pref['list'] == True:
                    prefs[pref['name']] = []
                    for v in pref['value']:
                        prefs[pref['name']].append(v[1])
                else:
                    prefs[pref['name']] = pref['value']
            db_sel = sa.sql.select(
                [
                    db_widget.c.component_id
                ],
                db_widget.c.id == area['widget_id']
            )
            db_res = db_conn.execute(db_sel)
            db_data = db_res.fetchone()
            pres_areas[area['name']] = self.get_component_with_prefs(
                db_data[db_widget.c.component_id],
                prefs
            )
            pres_areas[area['name']]['widget_id'] = area['widget_id']
            pres_areas[area['name']]['last_modified'] = int(
                time.mktime(
                    area['last_modified'].timetuple()
                )
            )
            pres_areas[area['name']]['modified'] = True

        all_areas = self.get_template_areas(template_id)

        for area in all_areas:
            if not area in pres_areas.keys():
                pres_areas[area] = None

        # ids of all components that appear or will appear in the presentation
        component_ids = []

        where = [
            db_timetable.c.start <= date_cur,
            db_timetable.c.end > date_cur,
            db_timetable.c.presentation_id == db_areas.c.presentation_id,
            db_widget.c.id == db_areas.c.widget_id
        ]

        if device_id != None:
            where.append(db_timetable.c.device_id == device_id)
        elif device_name != None:
            where.append(db_timetable.c.device_id == db_device.c.id)
            where.append(db_device.c.name == device_name)

        db_sel = sa.sql.select(
            [
                db_widget.c.component_id
            ],
            sa.sql.and_(*where)
        ).group_by(
            db_widget.c.component_id
        )

        db_res = db_conn.execute(db_sel)

        for db_row in db_res:
            cmp_id = db_row[db_widget.c.component_id]
            cmp_info = self.get_component_information(cmp_id)
            if cmp_info['type'] == "jquery":
                component_ids.append(cmp_id)

        return dict(
            template={
                "id": template_id,
                "class": class_name
            },
            areas=pres_areas,
            component_ids=component_ids
        )

    def get_widget_preferences(self, widget_id):
        """
        Get preferences for a widget

        :param widget_id: The widget ID
        :type widget_id: Integer
        :return: List of prefs
        :rtype: List
        """
        # check param type
        if type(widget_id) != int:
            try:
                widget_id = int(widget_id)
            except:
                return None

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_widget = pypoly.tool.db_sa.meta.tables['widget']
        db_widget_conf = pypoly.tool.db_sa.meta.tables['widget_config']

        db_sel = sa.sql.select(
            [
                db_widget.c.component_id
            ],
            db_widget.c.id == widget_id
        )

        db_res = db_conn.execute(db_sel)
        # ToDo: error handling
        db_data = db_res.fetchone()
        component_id = db_data[db_widget.c.component_id]

        prefs = self.get_component_preferences(component_id)

        db_sel = sa.sql.select(
            [
                db_widget_conf.c.id,
                db_widget_conf.c.name,
                db_widget_conf.c.value
            ],
            db_widget_conf.c.widget_id == widget_id
        )

        db_res = db_conn.execute(db_sel)
        for row in db_res:
            for pref in prefs:
                if pref['name'] == row[db_widget_conf.c.name]:
                    value = None
                    if pref['type'] == "string":
                        value = row[db_widget_conf.c.value]
                    elif pref['type'] == "integer":
                        value = int(row[db_widget_conf.c.value])
                    elif pref['type'] == "boolean":
                        tmp = row[db_widget_conf.c.value]
                        if tmp == None:
                            value = False
                        else:
                            value = True
                    if pref['list'] == True:
                        pref['value'].append(
                            (
                                row[db_widget_conf.c.id],
                                value
                            )
                        )
                    else:
                        pref['value'] = value

        return prefs

    def get_style(self, template_id):
        """
        Get stylesheet data for a template by loading the style.css

        :param template_id: The template ID
        :type template_id: Integer
        :return: The stylesheet data
        :rtype: String
        :ToDo: Check if file exists
        """
        tpl_path = pypoly.config.get('template.path')

        filename = os.path.join(
            tpl_path,
            str(template_id),
            "style.css"
        )

        fp = open(filename)
        data = fp.read().decode("utf-8")

        return data

    def get_template(self, template_id):
        """
        Get the content of a template by loading the content.html file.

        :param template_id: The template ID
        :type template_id: Integer
        :return: Return the HTML template
        :rtype: String
        :ToDo: Check if file exists
        """
        tpl_path = pypoly.config.get('template.path')

        filename = os.path.join(
            tpl_path,
            str(template_id),
            "content.html"
        )

        fp = open(filename)
        data = fp.read().decode("utf-8")

        return data

    def get_template_areas(self, template_id):
        """
        Get a list of all area names.

        :param template_id: The template ID
        :type template_id: Integer
        :return: List of area names
        :rtype: List
        """
        tpl_path = pypoly.config.get('template.path')

        filename = os.path.join(
            tpl_path,
            str(template_id),
            "info.xml"
        )

        xml_file = parse(filename)

        areas = []
        doc_element = xml_file.documentElement
        for child in doc_element.childNodes:
            if child.nodeName == "areas":
                for area_node in child.getElementsByTagName("area"):
                    name = area_node.getAttribute("name")
                    areas.append(name)

        return areas

    def get_template_areas_available(self, template_id, layout_name):
        """
        Get a list of all areas available in template in the specified layout.

        :param template_id: The template ID
        :type template_id: Integer
        :param layout_name: The name of the layout
        :type layout_name: String
        :return: List of names
        :rtype: List
        :ToDo: check if file exists
        """
        tpl_path = pypoly.config.get('template.path')

        filename = os.path.join(
            tpl_path,
            str(template_id),
            "info.xml"
        )

        xml_file = parse(filename)

        areas = []
        doc_element = xml_file.documentElement
        for child in doc_element.childNodes:
            if child.nodeName == "layouts":
                for layout_node in child.getElementsByTagName("layout"):
                    if layout_name == layout_node.getAttribute("name"):
                        area_nodes = layout_node.getElementsByTagName("area")
                        for area_node in area_nodes:
                            name = area_node.getAttribute("name")
                            areas.append(name)
        return areas

    def get_template_areas_with_infos(self, template_id):
        """
        Get all areas from a template file with extra information.

        :param template_id: The template ID
        :type template_id: Integer
        :return: List of all areas with extra information
        :rtype: List
        """
        tpl_path = pypoly.config.get('template.path')

        filename = os.path.join(
            tpl_path,
            str(template_id),
            "info.xml"
        )

        xml_file = parse(filename)

        areas = dict()
        doc_element = xml_file.documentElement
        for child in doc_element.childNodes:
            if child.nodeName == "areas":
                for area_node in child.getElementsByTagName("area"):
                    name = area_node.getAttribute("name")
                    title = area_node.getAttribute("title")
                    description = area_node.getAttribute("description")
                    areas.append(
                        dict(
                            name=name,
                            title=title,
                            description=description
                        )
                    )

        return areas

    def get_template_information(self, template_id):
        """
        Get information for a template by its ID.

        :see: tuvedi_tool.get_xml_information

        :param template_id: The ID of the template
        :type template_id: Integer
        :return: Dict with information
        :rtype: Dict
        :ToDo: check for errors
        """
        tpl_path = pypoly.config.get('template.path')

        filename = os.path.join(
            tpl_path,
            str(template_id),
            "info.xml"
        )

        xml_fp = open(filename)
        if xml_fp:
            # ToDo: check for errors
            xml_file = minidom.parse(xml_fp)
            doc = xml_file.documentElement
            return pypoly.tool.tuvedi.get_xml_information(doc)

    def get_templates_with_layouts(self):
        """
        Get all Template with layouts.

        :return: List of templates
        :rtype: List
        """
        db_conn = pypoly.tool.db_sa.connect()
        db_template = pypoly.tool.db_sa.meta.tables['template']

        db_sel = sa.sql.select(
            [
                db_template.c.id,
                db_template.c.title
            ],
        )

        db_res = db_conn.execute(db_sel)

        templates = []

        for row in db_res:
            template_id = row[db_template.c.id]
            layouts = self.get_layouts(template_id)
            templates.append(
                dict(
                    id=template_id,
                    title=row[db_template.c.title],
                    layouts=layouts
                )
            )

        return templates

    def get_xml_information(self, elem_doc):
        """
        Get all information from the information element in a info.xml file.

        :param elem_doc: The document element
        :type elem_doc: XML-Element
        :return: A dictionary with all information found
        :rtype: Dict
        :ToDo: raise an exception on errors
        """
        info = dict(
            name="",
            title="",
            authors=[],
            version="",
            description="",
            type=""
        )
        elem_info = elem_doc.getElementsByTagName("information").item(0)

        for elem in elem_info.childNodes:
            if elem.nodeName == "name":
                info['name'] = elem.getAttribute("value")
            if elem.nodeName == "title":
                info['title'] = elem.getAttribute("value")
            if elem.nodeName == "author":
                info['authors'].append(elem.getAttribute("value"))
            if elem.nodeName == "version":
                info['version'] = elem.getAttribute("value")
            if elem.nodeName == "description":
                info['description'] = elem.getAttribute("value")

        try:
            elem_content = elem_doc.getElementsByTagName("content").item(0)
            info['type'] = elem_content.getAttribute("type")
        except:
            pass

        return info

    def register_component_handler(self, component_name, handler):
        """
        Register a handler function for a component.

        :param component_name: The name of the component.
        :type component_name: String
        :param handler: The handler.
        :type handler: function
        """
        self.component_handlers[component_name] = handler

    def set_device_preferences(self, device_id, device_prefs):
        """
        Set all preferences for a device.

        :param device_id: ID of the widget
        :type device_id: Integer
        :param device_prefs: The preferences
        :type device_prefs: Dict
        :return: True = everything ok | False = an error occurs
        :rtype: Boolean
        """
        # check param type
        if type(device_id) != int:
            try:
                devicet_id = int(device_id)
            except:
                return False

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_device = pypoly.tool.db_sa.meta.tables['device']
        db_device_conf = pypoly.tool.db_sa.meta.tables['device_config']

        db_sel = sa.sql.select(
            [
                db_device_conf.c.id,
                db_device_conf.c.name,
                db_device_conf.c.value
            ],
            db_device_conf.c.device_id == device_id
        )

        prefs_update = []
        prefs_insert = []
        prefs_processed = []

        db_res = db_conn.execute(db_sel)

        for row in db_res:
            name = row[db_device_conf.c.name]
            if name in self.device_prefs:
                value = row[db_device_conf.c.value]
                if device_prefs[name] == value:
                    continue
                prefs_update.append(
                    dict(
                        vname=name,
                        value=device_prefs[name]
                    )
                )
                prefs_processed.append(name)

        for name in self.device_prefs.keys():
            if name in prefs_processed:
                continue
            prefs_insert.append(
                dict(
                    device_id=device_id,
                    name=name,
                    value=device_prefs[name]
                )
            )

        if len(prefs_update) > 0:
            db_update = db_device_conf.update().where(
                sa.sql.expression.and_(
                    db_device_conf.c.device_id == device_id,
                    db_device_conf.c.name == sa.sql.bindparam('vname')
                )
            ).values(
                value=sa.sql.bindparam('value')
            )

            db_conn.execute(
                db_update,
                prefs_update
            )

        if len(prefs_insert) > 0:
            db_conn.execute(
                db_device_conf.insert(),
                prefs_insert
            )

        db_update = db_device.update(
            values={
                "last_modified": sa.sql.expression.func.NOW()
            }
        ).where(
            db_device.c.id == device_id
        )

        db_conn.execute(db_update)

        return True

    def set_presentation_areas_config(self, presentation_id, area_config):
        """
        Set the config for all areas of a presentation.

        :param presentation_id: ID of the presentation
        :type presentation_id: Integer
        :param area_config: List of areas and the configuration params
        :type area_config: Dict
        :return: True = everything ok | False = an error occurs
        :rtype: Boolean
        """
        # check param type
        if type(presentation_id) != int:
            try:
                presentation_id = int(presentation_id)
            except:
                return False

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_presentation = pypoly.tool.db_sa.meta.tables['presentation']
        db_pres_areas = pypoly.tool.db_sa.meta.tables['presentation_areas']

        db_sel = sa.sql.select(
            [
                db_pres_areas.c.name
            ],
            db_pres_areas.c.presentation_id == presentation_id
        )

        db_res = db_conn.execute(db_sel)
        # ToDo: error handling

        areas_update = []
        areas_insert = []
        areas_processed = []

        for row in db_res:
            if row[db_pres_areas.c.name] in area_config:
                tmp_name = row[db_pres_areas.c.name]
                areas_update.append(
                    dict(
                        vname=tmp_name,
                        widget_id=area_config[tmp_name]
                    )
                )
                areas_processed.append(tmp_name)

        for area in self.get_presentation_areas(presentation_id):
            if not area['name'] in areas_processed and \
               area['name'] in area_config:
                areas_insert.append(
                    dict(
                        presentation_id=presentation_id,
                        name=area['name'],
                        widget_id=area_config[area['name']]
                    )
                )
                areas_processed.append(area['name'])

        if len(areas_update) > 0:
            db_update = db_pres_areas.update().where(
                sa.sql.expression.and_(
                    db_pres_areas.c.presentation_id == presentation_id,
                    db_pres_areas.c.name == sa.sql.bindparam('vname')
                )
            ).values(
                widget_id=sa.sql.bindparam('widget_id')
            )

            db_conn.execute(
                db_update,
                areas_update
            )

        if len(areas_insert) > 0:
            db_conn.execute(
                db_pres_areas.insert(),
                areas_insert
            )

        db_update = db_presentation.update(
            values={
                "last_modified": sa.sql.expression.func.NOW()
            }
        ).where(
            db_presentation.c.id == presentation_id
        )

        db_conn.execute(db_update)

        return True

    def set_widget_preferences(self, widget_id, widget_prefs):
        """
        Set all preferences for a widget.

        :param widget_id: ID of the widget
        :type widget_id: Integer
        :param widget_prefs: The preferences
        :type widget_prefs: Dict
        :return: True = everything ok | False = an error occurs
        :rtype: Boolean
        """
        # check param type
        if type(widget_id) != int:
            try:
                widget_id = int(widget_id)
            except:
                return False

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_widget = pypoly.tool.db_sa.meta.tables['widget']
        db_widget_conf = pypoly.tool.db_sa.meta.tables['widget_config']

        db_sel = sa.sql.select(
            [
                db_widget.c.component_id
            ],
            db_widget.c.id == widget_id
        )

        db_res = db_conn.execute(db_sel)
        # ToDo: error handling
        db_data = db_res.fetchone()
        component_id = db_data[db_widget.c.component_id]

        prefs = self.get_component_preferences(component_id)

        db_sel = sa.sql.select(
            [
                db_widget_conf.c.id,
                db_widget_conf.c.name,
                db_widget_conf.c.value
            ],
            db_widget_conf.c.widget_id == widget_id
        )

        prefs_update = []
        prefs_insert = []
        prefs_processed = []

        db_res = db_conn.execute(db_sel)

        for row in db_res:
            for pref in prefs:
                if pref['list'] == True:
                    continue
                elif pref['name'] == row[db_widget_conf.c.name]:
                    if pref['name'] in widget_prefs:
                        pref['value'] = widget_prefs[pref['name']]
                    else:
                        pref['value'] = row[db_widget_conf.c.value]
                    prefs_update.append(
                        dict(
                            vname=pref['name'],
                            value=pref['value']
                        )
                    )
                    prefs_processed.append(pref['name'])

        for pref in prefs:
            if pref['list'] == True:
                continue
            elif not pref['name'] in prefs_processed:
                if pref['name'] in widget_prefs:
                    prefs_insert.append(
                        dict(
                            widget_id=widget_id,
                            name=pref['name'],
                            value=widget_prefs[pref['name']]
                        )
                    )

        if len(prefs_update) > 0:
            db_update = db_widget_conf.update().where(
                sa.sql.expression.and_(
                    db_widget_conf.c.widget_id == widget_id,
                    db_widget_conf.c.name == sa.sql.bindparam('vname')
                )
            ).values(
                value=sa.sql.bindparam('value')
            )

            db_conn.execute(
                db_update,
                prefs_update
            )

        if len(prefs_insert) > 0:
            db_conn.execute(
                db_widget_conf.insert(),
                prefs_insert
            )

        db_update = db_widget.update(
            values={
                "last_modified": sa.sql.expression.func.NOW()
            }
        ).where(
            db_widget.c.id == widget_id
        )

        db_conn.execute(db_update)

        return True

    def set_widget_preference_list(self, widget_id, pref_name, pref_values):
        """
        Set all preferences for a widget.

        :param widget_id: ID of the widget
        :type widget_id: Integer
        :param widget_prefs: The preferences
        :type widget_prefs: Dict
        :return: True = everything ok | False = an error occurs
        :rtype: Boolean
        """
        # check param type
        if type(widget_id) != int:
            try:
                widget_id = int(widget_id)
            except:
                return False

        # get db stuff
        db_conn = pypoly.tool.db_sa.connect()
        db_widget = pypoly.tool.db_sa.meta.tables['widget']
        db_widget_conf = pypoly.tool.db_sa.meta.tables['widget_config']

        db_sel = sa.sql.select(
            [
                db_widget.c.component_id
            ],
            db_widget.c.id == widget_id
        )

        db_res = db_conn.execute(db_sel)
        # ToDo: error handling
        db_data = db_res.fetchone()
        component_id = db_data[db_widget.c.component_id]

        prefs = self.get_component_preferences(component_id)

        pref = None

        for p in prefs:
            if p['name'] == pref_name:
                pref = p

        if pref == None:
            return False

        db_sel = sa.sql.select(
            [
                db_widget_conf.c.id,
                db_widget_conf.c.name,
                db_widget_conf.c.value
            ],
            sa.sql.expression.and_(
                db_widget_conf.c.widget_id == widget_id,
                db_widget_conf.c.name == pref_name
            )
        )

        prefs_update = []
        prefs_insert = []
        prefs_processed = []

        db_res = db_conn.execute(db_sel)

        for row in db_res:
            for pref in pref_values:
                if pref[0] == row[db_widget_conf.c.id]:
                    prefs_update.append(
                        dict(
                            pref_id=pref[0],
                            value=pref[1]
                        )
                    )

        for pref in pref_values:
            if pref[0] == None:
                prefs_insert.append(
                    dict(
                        widget_id=widget_id,
                        name=pref_name,
                        value=pref[1]
                    )
                )

        if len(prefs_update) > 0:
            db_update = db_widget_conf.update().where(
                sa.sql.expression.and_(
                    db_widget_conf.c.widget_id == widget_id,
                    db_widget_conf.c.id == sa.sql.bindparam('pref_id')
                )
            ).values(
                value=sa.sql.bindparam('value')
            )

            db_conn.execute(
                db_update,
                prefs_update
            )

        if len(prefs_insert) > 0:
            db_conn.execute(
                db_widget_conf.insert(),
                prefs_insert
            )

        db_update = db_widget.update(
            values={
                "last_modified": sa.sql.expression.func.NOW()
            }
        ).where(
            db_widget.c.id == widget_id
        )

        db_conn.execute(db_update)

        return True
