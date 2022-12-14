##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

#!/usr/bin/python3

import sys
import sip
import six
import os

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QHBoxLayout, \
    QLabel, QLineEdit, QGroupBox, QFileDialog, QMessageBox, QToolButton, QDialog, QDialogButtonBox, QApplication

from matplotlib.backends.qt_compat import QtWidgets
from functools import partial

from traits.api import TraitListObject, List, Undefined, TraitError

from soma.controller import trait_ids

from DataBrowser.AdvancedSearch import AdvancedSearch
from DataBrowser.DataBrowser import TableDataBrowser
from PopUps.Ui_Select_Tag_Count_Table import Ui_Select_Tag_Count_Table

from PopUps.Ui_Visualized_Tags import Ui_Visualized_Tags
from Project.Project import TAG_FILENAME, COLLECTION_CURRENT
from Project.Filter import Filter
from PipelineManager.Process_mia import Process_mia

if sys.version_info[0] >= 3:
    unicode = str
    def values(d):
        return list(d.values())
else:
    def values(d):
        return d.values()


class NodeController(QWidget):
    """
    Controller that allows to change the input and output values of a pipeline node

    Attributes:
        - node_name: name of the selected node
        - project: current project in the software
        - scan_list: list of the selected database files

    Methods:
        - display_parameters: displays the parameters of the selected node
        - get_index_from_plug_name: returns the index of the plug label
        - update_node_name: updates the name of the selected node
        - update_plug_value: updates the value of a node plug
        - display_filter: displays a filter widget
        - update_plug_value_from_filter: updates the plug value from a filter result
        - clearLayout: clears the layouts of the widget
    """

    value_changed = pyqtSignal(list)

    def __init__(self, project, scan_list, pipeline_manager_tab, main_window):
        """
        Initialization of the Node Controller

        :param project: current project in the software
        :param scan_list: list of the selected database files
        :param pipeline_manager_tab: parent widget
        :param main_window: main window of the software
        """

        super(NodeController, self).__init__(pipeline_manager_tab)

        self.project = project
        self.scan_list = scan_list
        self.main_window = main_window
        self.node_name = ""

        # Layouts
        self.v_box_final = QVBoxLayout()
        self.h_box_node_name = QHBoxLayout()

    def display_parameters(self, node_name, process, pipeline):
        """
        Displays the parameters of the selected node

        The node parameters are read and line labels/line edits/push buttons are
        created for each of them. This methods consists mainly in widget and layout
        organization.

        :param node_name: name of the node
        :param process: process of the node
        :param pipeline: current pipeline
        :return:
        """

        self.node_name = node_name

        self.line_edit_input = []
        self.line_edit_output = []
        self.labels_input = []
        self.labels_output = []
        if len(self.children()) > 0:
            self.clearLayout(self)

        self.v_box_final = QVBoxLayout()

        # Node name
        label_node_name = QLabel()
        label_node_name.setText('Node name:')

        self.line_edit_node_name = QLineEdit()

        # The pipeline global inputs and outputs node name cannot be modified
        if self.node_name not in ('inputs', 'outputs'):
            self.line_edit_node_name.setText(self.node_name)
            self.line_edit_node_name.returnPressed.connect(partial(self.update_node_name, pipeline))
        else:
            self.line_edit_node_name.setText('Pipeline inputs/outputs')
            self.line_edit_node_name.setReadOnly(True)

        self.h_box_node_name = QHBoxLayout()
        self.h_box_node_name.addWidget(label_node_name)
        self.h_box_node_name.addWidget(self.line_edit_node_name)

        # Inputs
        self.button_group_inputs = QGroupBox('Inputs')
        self.v_box_inputs = QVBoxLayout()
        idx = 0

        for name, trait in process.user_traits().items():
            if name == 'nodes_activation':
                continue
            if not trait.output:
                label_input = QLabel()
                label_input.setText(str(name))
                self.labels_input.insert(idx, label_input)
                try:
                    value = getattr(process, name)
                except TraitError:
                    value = Undefined
                trait_type = trait_ids(process.trait(name))

                self.line_edit_input.insert(idx, QLineEdit())
                self.line_edit_input[idx].setText(str(value))
                self.line_edit_input[idx].returnPressed.connect(partial(self.update_plug_value, 'in',
                                                                        name, pipeline, type(value)))

                h_box = QHBoxLayout()
                h_box.addWidget(label_input)
                h_box.addWidget(self.line_edit_input[idx])

                # Adding the possibility to filter pipeline global inputs except if the input is "database_scans"
                # which means that the scans will be filtered with InputFilter
                if self.node_name == "inputs" and name != "database_scans":
                    parameters = (idx, pipeline, type(value))
                    push_button = QPushButton('Filter')
                    push_button.clicked.connect(partial(self.display_filter, self.node_name, name, parameters, process))
                    h_box.addWidget(push_button)

                self.v_box_inputs.addLayout(h_box)

                idx += 1

        self.button_group_inputs.setLayout(self.v_box_inputs)

        # Outputs
        self.button_group_outputs = QGroupBox('Outputs')
        self.v_box_outputs = QVBoxLayout()
        idx = 0

        for name, trait in process.traits(output=True).items():
            label_output = QLabel()
            label_output.setText(str(name))
            self.labels_output.insert(idx, label_output)

            value = getattr(process, name)
            trait_type = trait_ids(process.trait(name))

            self.line_edit_output.insert(idx, QLineEdit())
            self.line_edit_output[idx].setText(str(value))
            self.line_edit_output[idx].returnPressed.connect(partial(self.update_plug_value, 'out',
                                                                     name, pipeline, type(value)))

            h_box = QHBoxLayout()
            h_box.addWidget(label_output)
            h_box.addWidget(self.line_edit_output[idx])

            self.v_box_outputs.addLayout(h_box)

            idx += 1

        self.button_group_outputs.setLayout(self.v_box_outputs)

        self.v_box_final.addLayout(self.h_box_node_name)
        self.v_box_final.addWidget(self.button_group_inputs)
        self.v_box_final.addWidget(self.button_group_outputs)

        self.setLayout(self.v_box_final)

    def get_index_from_plug_name(self, plug_name, in_or_out):
        """
        Returns the index of the plug label.

        :param plug_name: name of the plug
        :param in_or_out: "in" if the plug is an input plug, "out" else
        :return:
        """
        if in_or_out == "in":
            for idx, label in enumerate(self.labels_input):
                if label.text() == plug_name:
                    return idx

        else:
            for idx, label in enumerate(self.labels_output):
                if label.text() == plug_name:
                    return idx

    def update_node_name(self, pipeline, new_node_name=None):
        """
        Changes the name of the selected node and updates the pipeline.

        Because the nodes are stored in a dictionary, we have to create
        a new node that has the same traits as the selected one and create
        new links that are the same than the selected node.

        :param pipeline: current pipeline
        :param new_node_name: new node name (is None except when this method
        is called from an undo/redo)
        :return:
        """

        # Copying the old node
        old_node = pipeline.nodes[self.node_name]
        old_node_name = self.node_name

        if not new_node_name:
            new_node_name = self.line_edit_node_name.text()

        if new_node_name in list(pipeline.nodes.keys()):
            print("Node name already in pipeline")

        else:
            # Removing links of the selected node and copy the origin/destination
            links_to_copy = []
            for source_parameter, source_plug \
                    in six.iteritems(old_node.plugs):
                for (dest_node_name, dest_parameter, dest_node, dest_plug,
                     weak_link) in source_plug.links_to.copy():
                    pipeline.remove_link(self.node_name + "." + source_parameter + "->"
                                         + dest_node_name + "." + dest_parameter)
                    links_to_copy.append(("to", source_parameter, dest_node_name, dest_parameter))

                for (dest_node_name, dest_parameter, dest_node, dest_plug,
                     weak_link) in source_plug.links_from.copy():
                    pipeline.remove_link(dest_node_name + "." + dest_parameter + "->"
                                         + self.node_name + "." + source_parameter)
                    links_to_copy.append(("from", source_parameter, dest_node_name, dest_parameter))

            # Creating a new node with the new name and deleting the previous one
            pipeline.nodes[new_node_name] = pipeline.nodes[self.node_name]
            del pipeline.nodes[self.node_name]

            # Updating the node_name attribute
            self.node_name = new_node_name

            # Setting the same links as the original node
            for link in links_to_copy:

                if link[0] == "to":
                    pipeline.add_link(self.node_name + "." + link[1] + "->"
                                      + link[2] + "." + link[3])
                elif link[0] == "from":
                    pipeline.add_link(link[2] + "." + link[3] + "->"
                                      + self.node_name + "." + link[1])

            # Updating the pipeline
            pipeline.update_nodes_and_plugs_activation()

            self.display_parameters(new_node_name, pipeline.nodes[new_node_name].process, pipeline)

            # To undo/redo
            self.value_changed.emit(["node_name", pipeline.nodes[new_node_name], new_node_name, old_node_name])

    def update_plug_value(self, in_or_out, plug_name, pipeline, value_type, new_value=None):
        """
        Updates the value of a node plug

        :param in_or_out: "in" if the plug is an input plug, "out" else
        :param plug_name: name of the plug
        :param pipeline: current pipeline
        :param value_type: type of the plug value
        :param new_value: new value for the plug (is None except when this method is
        called from an undo/redo)
        :return:
        """

        index = self.get_index_from_plug_name(plug_name, in_or_out)

        # Reading the value from the plug's line edit
        if not new_value:

            if in_or_out == 'in':
                new_value = self.line_edit_input[index].text()   
            elif in_or_out == 'out':
                new_value = self.line_edit_output[index].text()  
            else:
                new_value = None

            try:
                new_value = eval(new_value)
            except NameError:
                pass
            except Exception as err:
                print("{0}: {1}.".format(err.__class__, err))
                
            #except NameError:
            #    print("NameError for value {0}".format(new_value))
            #except SyntaxError:
            #    pass
            #    print("SynthaxError for value {0}".format(new_value))            
                
            if value_type not in [float, int, str, list]:
                value_type = str
        
        if self.node_name in ['inputs', 'outputs']:
            node_name = ''
        else:
            node_name = self.node_name
              
        old_value = pipeline.nodes[node_name].get_plug_value(plug_name)

        try:
            pipeline.nodes[node_name].set_plug_value(plug_name, new_value)
        except TraitError as err:
            msg = QMessageBox()
            msg.setText("{0}: {1}.".format(err.__class__, err))
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

            if in_or_out == 'in':
                self.line_edit_input[index].setText(str(old_value))
            elif in_or_out == 'out':
                self.line_edit_output[index].setText(str(old_value))
            return

        # Update pipeline to "propagate" the node value
        pipeline.update_nodes_and_plugs_activation()

        if in_or_out == 'in':
            self.line_edit_input[index].setText(str(new_value))
        elif in_or_out == 'out':
            self.line_edit_output[index].setText(str(new_value))

        # self.display_parameters(node_name, pipeline.nodes[node_name].process, pipeline)

        # To undo/redo
        self.value_changed.emit(["plug_value", self.node_name, old_value, plug_name, value_type, new_value])

    def display_filter(self, node_name, plug_name, parameters, process):
        """
        Displays a filter widget

        :param node_name: name of the node
        :param plug_name: name of the plug
        :param parameters: tuple containing the index of the plug, the current
        pipeline instance and the type of the plug value
        :param process: process of the node
        :return:
        """
        self.pop_up = PlugFilter(self.project, self.scan_list, process, node_name, plug_name, self, self.main_window)
        self.pop_up.show()
        self.pop_up.plug_value_changed.connect(partial(self.update_plug_value_from_filter, plug_name, parameters))

    def update_plug_value_from_filter(self, plug_name, parameters, filter_res_list):
        """
        Updates the plug value from a filter result

        :param plug_name: name of the plug
        :param parameters: tuple containing the index of the plug, the current
        pipeline instance and the type of the plug value
        :param filter_res_list: list of the filtered files
        :return:
        """

        index = parameters[0]
        pipeline = parameters[1]
        value_type = parameters[2]

        # If the list contains only one element, setting this element as the plug value
        len_list = len(filter_res_list)
        if len_list > 1:
            res = filter_res_list
        elif len_list == 1:
            res = filter_res_list[0]
        else:
            res = []

        self.update_plug_value("in", plug_name, pipeline, value_type, res)

    def clearLayout(self, layout):
        """
        Clears the layouts of the widget

        :param layout: widget with a layout
        :return:
        """
        for i in reversed(range(len(layout.children()))):
            if type(layout.layout().itemAt(i)) == QtWidgets.QWidgetItem:
                layout.layout().itemAt(i).widget().setParent(None)
            if type(layout.layout().itemAt(i)) == QtWidgets.QHBoxLayout or type(
                    layout.layout().itemAt(i)) == QtWidgets.QVBoxLayout:
                layout.layout().itemAt(i).deleteLater()
                for j in reversed(range(len(layout.layout().itemAt(i)))):
                    layout.layout().itemAt(i).itemAt(j).widget().setParent(None)

        if layout.layout() is not None:
            sip.delete(layout.layout())


class PlugFilter(QWidget):
    """
    Filter widget used on a node plug

    The widget displays a browser with the selected files of the database,
    a rapid search and an advanced search to filter these files. Once the
    filtering is done, the result (as a list of files) is set to the plug.

    Attributes:
        - advanced_search: advanced search widget to build a complex filter
        - main_window: parent main window
        - plug_name: name of the selected node plug
        - plug_value_changed: event emitted when the filtering has been done
        - process: process instance of the selected node
        - project: current project in the software
        - node_controller: parent node controller
        - rapid_search: rapid search widget to build a simple filter
        - scans_list: list of database files to filter
        - table_data: browser that displays the database files to filter

    Methods:
        - update_tag_to_filter: updates the tag to Filter
        - update_tags: updates the list of visualized tags
        - reset_search_bar: reset the search bar of the rapid search
        - search_str: updates the files to display in the browser
        - ok_clicked: sets the new value to the node plug and closes the widget
        - set_plug_value: emits a signal to set the file names to the node plug
    """

    plug_value_changed = pyqtSignal(list)

    def __init__(self, project, scans_list, process, node_name, plug_name, node_controller, main_window):
        """
        Initialization of the PlugFilter widget

        :param project: current project in the software
        :param scans_list: list of database files to filter
        :param process: process instance of the selected node
        :param node_name: name of the current node
        :param plug_name: name of the selected node plug
        :param node_controller: parent node controller
        :param main_window: parent main window
        """

        super(PlugFilter, self).__init__(None)

        from DataBrowser.RapidSearch import RapidSearch
        from Project.Project import COLLECTION_CURRENT

        self.project = project
        self.node_controller = node_controller
        self.main_window = main_window
        self.process = process
        self.plug_name = plug_name

        """
        # If the filter is saved in the node plug (not the case now)
        if hasattr(self.process, 'filters'):
            if self.plug_name in self.process.filters.keys():
                print("Already a filter for {0} plug of {1} process".format(self.plug_name, self.process.name))
                # TODO: fill the advanced search with the corresponding filter
        """

        # Verifying that the scan names begin not with a "/" or a "\"
        if scans_list:
            scans_list_copy = []
            for scan in scans_list:
                scan_no_pfolder = scan.replace(self.project.folder, "")
                if scan_no_pfolder[0] in ["\\", "/"]:
                    scan_no_pfolder = scan_no_pfolder[1:]
                scans_list_copy.append(scan_no_pfolder)

            self.scans_list = scans_list_copy

        # If there is no element in scans_list, this means that all the scans
        # of the database needs to be taken into account
        else:
            self.scans_list = self.project.session.get_documents_names(COLLECTION_CURRENT)

        self.setWindowTitle("Filter - " + node_name + " - " + plug_name)

        # Graphical components
        self.table_data = TableDataBrowser(self.project, self, self.node_controller.visibles_tags, False, False)

        # Reducing the list of scans to selection
        all_scans = self.table_data.scans_to_visualize
        self.table_data.scans_to_visualize = self.scans_list
        self.table_data.scans_to_search = self.scans_list
        self.table_data.update_visualized_rows(all_scans)

        search_bar_layout = QHBoxLayout()

        self.rapid_search = RapidSearch(self)
        self.rapid_search.textChanged.connect(partial(self.search_str))

        self.button_cross = QToolButton()
        self.button_cross.setStyleSheet('background-color:rgb(255, 255, 255);')
        self.button_cross.setIcon(QIcon(os.path.join('..', 'sources_images', 'gray_cross.png')))
        self.button_cross.clicked.connect(self.reset_search_bar)

        search_bar_layout.addWidget(self.rapid_search)
        search_bar_layout.addWidget(self.button_cross)

        self.advanced_search = AdvancedSearch(self.project, self, self.scans_list, self.node_controller.visibles_tags,
                                              from_pipeline=True)
        self.advanced_search.show_search()

        push_button_tags = QPushButton("Visualized tags")
        push_button_tags.clicked.connect(self.update_tags)

        self.push_button_tag_filter = QPushButton(TAG_FILENAME)
        self.push_button_tag_filter.clicked.connect(self.update_tag_to_filter)

        push_button_ok = QPushButton("OK")
        push_button_ok.clicked.connect(self.ok_clicked)

        push_button_cancel = QPushButton("Cancel")
        push_button_cancel.clicked.connect(self.close)

        # Layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(push_button_tags)
        buttons_layout.addWidget(self.push_button_tag_filter)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(push_button_ok)
        buttons_layout.addWidget(push_button_cancel)

        main_layout = QVBoxLayout()
        main_layout.addLayout(search_bar_layout)
        main_layout.addWidget(self.advanced_search)
        main_layout.addWidget(self.table_data)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        screen_resolution = QApplication.instance().desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        self.setMinimumWidth(0.6 * width)
        self.setMinimumHeight(0.8 * height)

    def update_tag_to_filter(self):
        """
        Updates the tag to Filter

        :return:
        """

        popUp = Ui_Select_Tag_Count_Table(self.project, self.node_controller.visibles_tags, self.push_button_tag_filter.text())
        if popUp.exec_():
            self.push_button_tag_filter.setText(popUp.selected_tag)

    def update_tags(self):
        """
        Updates the list of visualized tags

        :return:
        """

        dialog = QDialog()
        visualized_tags = Ui_Visualized_Tags(self.project, self.node_controller.visibles_tags)
        layout = QVBoxLayout()
        layout.addWidget(visualized_tags)
        buttons_layout = QHBoxLayout()
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        buttons_layout.addWidget(buttons)
        layout.addLayout(buttons_layout)
        dialog.setLayout(layout)
        dialog.show()
        dialog.setMinimumHeight(600)
        dialog.setMinimumWidth(600)
        if dialog.exec():
            new_visibilities = []
            for x in range(visualized_tags.list_widget_selected_tags.count()):
                visible_tag = visualized_tags.list_widget_selected_tags.item(x).text()
                new_visibilities.append(visible_tag)
            new_visibilities.append(TAG_FILENAME)
            self.table_data.update_visualized_columns(self.node_controller.visibles_tags, new_visibilities)
            self.node_controller.visibles_tags = new_visibilities
            for row in self.advanced_search.rows:
                fields = row[2]
                fields.clear()
                for visible_tag in new_visibilities:
                    fields.addItem(visible_tag)
                fields.model().sort(0)
                fields.addItem("All visualized tags")

    def reset_search_bar(self):
        """
        Reset the search bar of the rapid search

        :return:
        """
        self.rapid_search.setText("")
        self.advanced_search.rows = []
        self.advanced_search.show_search()

        # All rows reput
        old_scan_list = self.table_data.scans_to_visualize
        self.table_data.scans_to_visualize = self.scans_list
        self.table_data.scans_to_search = self.scans_list
        self.table_data.update_visualized_rows(old_scan_list)

    def search_str(self, str_search):
        """
        Updates the files to display in the browser
        :param str_search: string typed in the rapid search
        :return:
        """

        from Project.Project import COLLECTION_CURRENT, TAG_FILENAME
        from DataBrowser.DataBrowser import not_defined_value

        old_scan_list = self.table_data.scans_to_visualize

        # Every scan taken if empty search
        if str_search == "":
            return_list = self.table_data.scans_to_search
        else:
            # Scans with at least a not defined value
            if str_search == not_defined_value:
                filter = self.prepare_not_defined_filter(self.project.session.get_visibles())

            # Scans matching the search
            else:
                filter = self.rapid_search.prepare_filter(str_search, self.project.session.get_visibles(), self.table_data.scans_to_search)

            generator = self.project.session.filter_documents(COLLECTION_CURRENT, filter)

            # Creating the list of scans
            return_list = [getattr(scan, TAG_FILENAME) for scan in generator]

        self.table_data.scans_to_visualize = return_list
        self.advanced_search.scans_list = return_list

        # Rows updated
        self.table_data.update_visualized_rows(old_scan_list)

    def ok_clicked(self):
        """
        Sets the new value to the node plug and closes the widget
        :return:
        """

        # To use if the filters are set on plugs, which is not the case
        """
        if isinstance(self.process, Process_mia):
            (fields, conditions, values, links, nots) = self.advanced_search.get_filters(False)


            plug_filter = Filter(None, nots, values, fields, links, conditions, "")
            self.process.filters[self.plug_name] = plug_filter
        """

        self.set_plug_value()
        self.close()

    def set_plug_value(self):
        """
        Emits a signal to set the file names to the node plug
        :return:
        """

        result_names = []
        filter = self.table_data.get_current_filter()
        for i in range(len(filter)):
            scan_name = filter[i]
            tag_name = self.push_button_tag_filter.text()
            value = self.project.session.get_value(COLLECTION_CURRENT, scan_name, tag_name)
            if tag_name == TAG_FILENAME:
                value = os.path.abspath(os.path.join(self.project.folder, value))
            result_names.append(value)

        self.plug_value_changed.emit(result_names)


class FilterWidget(QWidget):
    """
    Filter widget used on a Input_Filter process

    The widget displays a browser with the selected files of the database,
    a rapid search and an advanced search to filter these files. Once the
    filtering is done, the filter is saved in the process.

    Attributes:
        - advanced_search: advanced search widget to build a complex filter
        - main_window: parent main window
        - process: process instance of the selected node
        - project: current project in the software
        - node: instance of the corresponding Input_Filter node
        - node_controller: parent node controller
        - rapid_search: rapid search widget to build a simple filter
        - scan_list: list of database files to filter
        - table_data: browser that displays the database files to filter
        - visible_tags: tags that are visible in the current project

    Methods:
        - update_tag_to_filter: updates the tag to Filter
        - update_tags: updates the list of visualized tags
        - reset_search_bar: reset the search bar of the rapid search
        - search_str: updates the files to display in the browser
        - ok_clicked: sets the filter to the process and closes the widget
        - set_plug_value: sets the output of the filter to the output of the node
    """

    def __init__(self, project, node_name, node, main_window):
        """
        Initialization of the Filter Widget

        :param project: current project in the software
        :param node_name: name of the current node
        :param node: instance of the corresponding Input_Filter node
        :param main_window: parent main window
        """

        super(FilterWidget, self).__init__(None)

        from DataBrowser.RapidSearch import RapidSearch

        self.project = project
        self.visible_tags = self.project.session.get_visibles()
        self.node = node
        self.process = node.process
        self.main_window = main_window

        scan_list = []
        # The scan list to filter corresponds to the input of the Input Filter
        if self.process.input and self.process is not Undefined:
            for scan in self.process.input:
                path, file_name = os.path.split(scan)
                path, second_folder = os.path.split(path)
                first_folder = os.path.basename(path)
                database_file = os.path.join(first_folder, second_folder, file_name)
                scan_list.append(database_file)

        self.scan_list = scan_list

        self.setWindowTitle("Filter - " + node_name)

        # Graphical components
        self.table_data = TableDataBrowser(self.project, self, self.visible_tags, False, False)

        # Reducing the list of scans to selection
        all_scans = self.table_data.scans_to_visualize

        self.table_data.scans_to_visualize = self.scan_list
        self.table_data.scans_to_search = self.scan_list
        self.table_data.update_visualized_rows(all_scans)

        # Filter information
        filter_to_apply = node.process.filter

        search_bar_layout = QHBoxLayout()

        self.rapid_search = RapidSearch(self)
        if filter_to_apply.search_bar:
            self.rapid_search.setText(filter_to_apply.search_bar)
        self.rapid_search.textChanged.connect(partial(self.search_str))

        self.button_cross = QToolButton()
        self.button_cross.setStyleSheet('background-color:rgb(255, 255, 255);')
        self.button_cross.setIcon(QIcon(os.path.join('..', 'sources_images', 'gray_cross.png')))
        self.button_cross.clicked.connect(self.reset_search_bar)

        search_bar_layout.addWidget(self.rapid_search)
        search_bar_layout.addWidget(self.button_cross)

        self.advanced_search = AdvancedSearch(self.project, self, self.scan_list, self.visible_tags,
                                              from_pipeline=True)
        self.advanced_search.show_search()
        self.advanced_search.apply_filter(filter_to_apply)

        push_button_tags = QPushButton("Visualized tags")
        push_button_tags.clicked.connect(self.update_tags)

        self.push_button_tag_filter = QPushButton(TAG_FILENAME)
        self.push_button_tag_filter.clicked.connect(self.update_tag_to_filter)

        push_button_ok = QPushButton("OK")
        push_button_ok.clicked.connect(self.ok_clicked)

        push_button_cancel = QPushButton("Cancel")
        push_button_cancel.clicked.connect(self.close)

        # Layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(push_button_tags)
        buttons_layout.addWidget(self.push_button_tag_filter)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(push_button_ok)
        buttons_layout.addWidget(push_button_cancel)

        main_layout = QVBoxLayout()
        main_layout.addLayout(search_bar_layout)
        main_layout.addWidget(self.advanced_search)
        main_layout.addWidget(self.table_data)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        screen_resolution = QApplication.instance().desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        self.setMinimumWidth(0.6 * width)
        self.setMinimumHeight(0.8 * height)

    def update_tag_to_filter(self):
        """
        Updates the tag to Filter

        :return:
        """

        popUp = Ui_Select_Tag_Count_Table(self.project, self.visible_tags, self.push_button_tag_filter.text())
        if popUp.exec_():
            self.push_button_tag_filter.setText(popUp.selected_tag)

    def update_tags(self):
        """
        Updates the list of visualized tags
        :return:
        """

        dialog = QDialog()
        visualized_tags = Ui_Visualized_Tags(self.project, self.visible_tags)
        layout = QVBoxLayout()
        layout.addWidget(visualized_tags)
        buttons_layout = QHBoxLayout()
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        buttons_layout.addWidget(buttons)
        layout.addLayout(buttons_layout)
        dialog.setLayout(layout)
        dialog.show()
        dialog.setMinimumHeight(600)
        dialog.setMinimumWidth(600)
        if dialog.exec():
            new_visibilities = []
            for x in range(visualized_tags.list_widget_selected_tags.count()):
                visible_tag = visualized_tags.list_widget_selected_tags.item(x).text()
                new_visibilities.append(visible_tag)
            new_visibilities.append(TAG_FILENAME)
            self.table_data.update_visualized_columns(self.visible_tags, new_visibilities)
            self.node_controller.visibles_tags = new_visibilities
            for row in self.advanced_search.rows:
                fields = row[2]
                fields.clear()
                for visible_tag in new_visibilities:
                    fields.addItem(visible_tag)
                fields.model().sort(0)
                fields.addItem("All visualized tags")

    def reset_search_bar(self):
        """
        Reset the search bar of the rapid search

        :return:
        """
        self.rapid_search.setText("")
        self.advanced_search.rows = []
        self.advanced_search.show_search()

        # All rows reput
        old_scan_list = self.table_data.scans_to_visualize
        self.table_data.scans_to_visualize = self.scan_list
        self.table_data.scans_to_search = self.scan_list
        self.table_data.update_visualized_rows(old_scan_list)

    def search_str(self, str_search):
        """
        Updates the files to display in the browser

        :param str_search: string typed in the rapid search
        :return:
        """

        from Project.Project import COLLECTION_CURRENT, TAG_FILENAME
        from DataBrowser.DataBrowser import not_defined_value

        old_scan_list = self.table_data.scans_to_visualize

        # Every scan taken if empty search
        if str_search == "":
            return_list = self.table_data.scans_to_search
        else:
            # Scans with at least a not defined value
            if str_search == not_defined_value:
                filter = self.prepare_not_defined_filter(self.project.session.get_visibles())
            # Scans matching the search
            else:
                filter = self.rapid_search.prepare_filter(str_search, self.project.session.get_visibles(), old_scan_list)

            generator = self.project.session.filter_documents(COLLECTION_CURRENT, filter)

            # Creating the list of scans
            return_list = [getattr(scan, TAG_FILENAME) for scan in generator]

        self.table_data.scans_to_visualize = return_list
        self.advanced_search.scans_list = return_list

        # Rows updated
        self.table_data.update_visualized_rows(old_scan_list)

    def ok_clicked(self):
        """
        Sets the filter to the process and closes the widget

        :return:
        """
        if isinstance(self.process, Process_mia):
            (fields, conditions, values, links, nots) = self.advanced_search.get_filters(False)
            filt = Filter(None, nots, values, fields, links, conditions, self.rapid_search.text())
            self.process.filter = filt

        self.set_output_value()
        self.close()

    def set_output_value(self):
        """
        Sets the output of the filter to the output of the node

        :return:
        """

        result_names = []
        filter = self.table_data.get_current_filter()
        for i in range(len(filter)):
            scan_name = filter[i]
            tag_name = self.push_button_tag_filter.text()
            value = self.project.session.get_value(COLLECTION_CURRENT, scan_name, tag_name)
            if tag_name == TAG_FILENAME:
                value = os.path.abspath(os.path.join(self.project.folder, value))
            result_names.append(value)

        result_files = []
        for result_name in result_names:
            full_path = os.path.abspath(os.path.join(self.project.folder, result_name))
            result_files.append(full_path)

        self.node.set_plug_value("output", result_files)

