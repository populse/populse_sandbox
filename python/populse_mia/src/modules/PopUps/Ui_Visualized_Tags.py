##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

# MIA import
from Project.Project import TAG_CHECKSUM, TAG_FILENAME, COLLECTION_CURRENT


class Ui_Visualized_Tags(QWidget):
    """
    Is called when the user wants to update the tags that are visualized
    """

    # Signal that will be emitted at the end to tell that the preferences have been changed
    signal_preferences_change = pyqtSignal()

    def __init__(self, database, tags):
        super().__init__()
        self.retranslate_Ui(database, tags)

    def retranslate_Ui(self, project, tags):
        _translate = QtCore.QCoreApplication.translate

        # Two buttons to select or unselect tags
        self.push_button_select_tag = QtWidgets.QPushButton(self)
        self.push_button_select_tag.setObjectName("pushButton_select_tag")
        self.push_button_select_tag.clicked.connect(self.click_select_tag)

        self.push_button_unselect_tag = QtWidgets.QPushButton(self)
        self.push_button_unselect_tag.setObjectName("pushButton_unselect_tag")
        self.push_button_unselect_tag.clicked.connect(self.click_unselect_tag)

        self.push_button_select_tag.setText(_translate("MainWindow", "-->"))
        self.push_button_unselect_tag.setText(_translate("MainWindow", "<--"))

        vbox_tag_buttons = QVBoxLayout()
        vbox_tag_buttons.addWidget(self.push_button_select_tag)
        vbox_tag_buttons.addWidget(self.push_button_unselect_tag)

        # The "Tag list" label
        self.label_tag_list = QtWidgets.QLabel(self)
        self.label_tag_list.setTextFormat(QtCore.Qt.AutoText)
        self.label_tag_list.setObjectName("label_tag_list")
        self.label_tag_list.setText(_translate("MainWindow", "Available tags:"))

        # The search bar to search in the list of tags
        self.search_bar = QtWidgets.QLineEdit(self)
        self.search_bar.setObjectName("lineEdit_search_bar")
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.textChanged.connect(self.search_str)

        # The list of tags
        self.list_widget_tags = QtWidgets.QListWidget(self)
        self.list_widget_tags.setObjectName("listWidget_tags")
        self.list_widget_tags.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        hbox_top_left = QHBoxLayout()
        hbox_top_left.addWidget(self.label_tag_list)
        hbox_top_left.addWidget(self.search_bar)

        vbox_top_left = QVBoxLayout()
        vbox_top_left.addLayout(hbox_top_left)
        vbox_top_left.addWidget(self.list_widget_tags)

        # List of the tags selected by the user
        self.list_widget_selected_tags = QtWidgets.QListWidget(self)
        self.list_widget_selected_tags.setObjectName("listWidget_visualized_tags")
        self.list_widget_selected_tags.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        hbox_tags = QHBoxLayout()
        hbox_tags.addLayout(vbox_top_left)
        hbox_tags.addLayout(vbox_tag_buttons)
        hbox_tags.addWidget(self.list_widget_selected_tags)

        self.setLayout(hbox_tags)

        self.left_tags = []  # List that will keep track on the tags on the left (invisible tags)

        for tag in project.session.get_fields_names(COLLECTION_CURRENT):
            if tag != TAG_CHECKSUM and tag != TAG_FILENAME:
                item = QtWidgets.QListWidgetItem()
                if not tag in tags:
                    # Tag not visible: left side
                    self.list_widget_tags.addItem(item)
                    self.left_tags.append(tag)
                else:
                    # Tag visible: right side
                    self.list_widget_selected_tags.addItem(item)
                item.setText(tag)
        self.list_widget_tags.sortItems()

    def search_str(self, str_search):
        return_list = []
        if str_search != "":
            for tag in self.left_tags:
                if str_search.upper() in tag.upper():
                    return_list.append(tag)
        else:
            for tag in self.left_tags:
                return_list.append(tag)

        # Selection updated
        self.list_widget_tags.clear()
        for tag_name in return_list:
            item = QtWidgets.QListWidgetItem()
            self.list_widget_tags.addItem(item)
            item.setText(tag_name)
        self.list_widget_tags.sortItems()

    def click_select_tag(self):
        """
        Puts the selected tags in the "selected tag" table
        :return:
        """

        rows = sorted([index.row() for index in self.list_widget_tags.selectedIndexes()],
                      reverse=True)
        for row in rows:
            # assuming the other listWidget is called listWidget_2
            self.left_tags.remove(self.list_widget_tags.item(row).text())
            self.list_widget_selected_tags.addItem(self.list_widget_tags.takeItem(row))

    def click_unselect_tag(self):
        """
        Removes the unselected tags from the "selected tag" table
        :return:
        """

        rows = sorted([index.row() for index in self.list_widget_selected_tags.selectedIndexes()],
                      reverse=True)
        for row in rows:
            self.left_tags.append(self.list_widget_selected_tags.item(row).text())
            self.list_widget_tags.addItem(self.list_widget_selected_tags.takeItem(row))

        self.list_widget_tags.sortItems()