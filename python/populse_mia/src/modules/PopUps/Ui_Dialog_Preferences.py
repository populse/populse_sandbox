##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QCheckBox, QComboBox, QVBoxLayout, QHBoxLayout, QDialog, QLabel, QLineEdit, QPushButton, \
    QFileDialog, QMessageBox
from functools import partial

from SoftwareProperties.Config import Config

import os


class Ui_Dialog_Preferences(QDialog):
    """
    Is called when the user wants to change the software preferences
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_preferences_change = pyqtSignal()
    use_clinical_mode_signal = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.setModal(True)
        self.pop_up(main_window)

    def pop_up(self, main_window):
        _translate = QtCore.QCoreApplication.translate

        self.setObjectName("Dialog")
        self.setWindowTitle('MIA preferences')

        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setEnabled(True)

        config = Config()

        # The 'Tools" tab
        self.tab_tools = QtWidgets.QWidget()
        self.tab_tools.setObjectName("tab_tools")
        self.tab_widget.addTab(self.tab_tools, _translate("Dialog", "Tools"))

        # Groupbox "Global preferences"
        self.groupbox_global = QtWidgets.QGroupBox("Global preferences")

        self.save_checkbox = QCheckBox('', self)
        self.save_label = QLabel("Auto save")

        if config.isAutoSave() == "yes":
            self.save_checkbox.setChecked(1)

        h_box_auto_save = QtWidgets.QHBoxLayout()
        h_box_auto_save.addWidget(self.save_checkbox)
        h_box_auto_save.addWidget(self.save_label)
        h_box_auto_save.addStretch(1)

        self.clinical_mode_checkbox = QCheckBox('', self)
        self.clinical_mode_label = QLabel("Clinical mode")

        if config.get_clinical_mode() == "yes":
            self.clinical_mode_checkbox.setChecked(1)
        else:
            self.clinical_mode_checkbox.setChecked(1)
            self.clinical_mode_checkbox.setChecked(0)

        h_box_clinical_mode = QtWidgets.QHBoxLayout()
        h_box_clinical_mode.addWidget(self.clinical_mode_checkbox)
        h_box_clinical_mode.addWidget(self.clinical_mode_label)
        h_box_clinical_mode.addStretch(1)

        v_box_global = QtWidgets.QVBoxLayout()
        v_box_global.addLayout(h_box_auto_save)
        v_box_global.addLayout(h_box_clinical_mode)

        self.groupbox_global.setLayout(v_box_global)

        # Groupbox "Matlab"
        self.groupbox_matlab = QtWidgets.QGroupBox("Matlab")
        self.use_matlab_label = QLabel("Use Matlab")
        self.use_matlab_checkbox = QCheckBox('', self)

        self.matlab_label = QLabel("Matlab path:")
        self.matlab_choice = QLineEdit(config.get_matlab_path())
        self.matlab_browse = QPushButton("Browse")
        self.matlab_browse.clicked.connect(self.browse_matlab)

        self.matlab_standalone_label = QLabel("Matlab standalone path:")
        self.matlab_standalone_choice = QLineEdit(config.get_matlab_standalone_path())
        self.matlab_standalone_browse = QPushButton("Browse")
        self.matlab_standalone_browse.clicked.connect(self.browse_matlab_standalone)

        if config.get_use_matlab() == "yes":
            self.use_matlab_checkbox.setChecked(1)
        else:
            self.use_matlab_checkbox.setChecked(0)

        h_box_use_matlab = QtWidgets.QHBoxLayout()
        h_box_use_matlab.addWidget(self.use_matlab_checkbox)
        h_box_use_matlab.addWidget(self.use_matlab_label)
        h_box_use_matlab.addStretch(1)

        h_box_matlab_path = QtWidgets.QHBoxLayout()
        h_box_matlab_path.addWidget(self.matlab_choice)
        h_box_matlab_path.addWidget(self.matlab_browse)

        v_box_matlab_path = QtWidgets.QVBoxLayout()
        v_box_matlab_path.addWidget(self.matlab_label)
        v_box_matlab_path.addLayout(h_box_matlab_path)

        h_box_matlab_standalone_path = QtWidgets.QHBoxLayout()
        h_box_matlab_standalone_path.addWidget(self.matlab_standalone_choice)
        h_box_matlab_standalone_path.addWidget(self.matlab_standalone_browse)

        v_box_matlab_standalone_path = QtWidgets.QVBoxLayout()
        v_box_matlab_standalone_path.addWidget(self.matlab_standalone_label)
        v_box_matlab_standalone_path.addLayout(h_box_matlab_standalone_path)

        v_box_matlab = QtWidgets.QVBoxLayout()
        v_box_matlab.addLayout(h_box_use_matlab)
        v_box_matlab.addLayout(v_box_matlab_path)
        v_box_matlab.addLayout(v_box_matlab_standalone_path)

        self.groupbox_matlab.setLayout(v_box_matlab)

        # Groupbox "SPM"
        self.groupbox_spm = QtWidgets.QGroupBox("SPM")

        self.use_spm_label = QLabel("Use SPM")
        self.use_spm_checkbox = QCheckBox('', self)

        self.spm_label = QLabel("SPM path:")
        self.spm_choice = QLineEdit(config.get_spm_path())
        self.spm_browse = QPushButton("Browse")
        self.spm_browse.clicked.connect(self.browse_spm)

        if config.get_use_spm() == "yes":
            self.use_spm_checkbox.setChecked(1)
        else:
            self.use_spm_checkbox.setChecked(0)

        h_box_use_spm = QtWidgets.QHBoxLayout()
        h_box_use_spm.addWidget(self.use_spm_checkbox)
        h_box_use_spm.addWidget(self.use_spm_label)
        h_box_use_spm.addStretch(1)

        h_box_spm_path = QtWidgets.QHBoxLayout()
        h_box_spm_path.addWidget(self.spm_choice)
        h_box_spm_path.addWidget(self.spm_browse)

        v_box_spm_path = QtWidgets.QVBoxLayout()
        v_box_spm_path.addWidget(self.spm_label)
        v_box_spm_path.addLayout(h_box_spm_path)

        self.use_spm_standalone_label = QLabel("Use SPM standalone")
        self.use_spm_standalone_checkbox = QCheckBox('', self)

        self.spm_standalone_label = QLabel("SPM standalone path:")
        self.spm_standalone_choice = QLineEdit(config.get_spm_standalone_path())
        self.spm_standalone_browse = QPushButton("Browse")
        self.spm_standalone_browse.clicked.connect(self.browse_spm_standalone)

        if config.get_use_spm_standalone() == "yes":
            self.use_spm_standalone_checkbox.setChecked(1)
        else:
            self.use_spm_standalone_checkbox.setChecked(0)

        h_box_use_spm_standalone = QtWidgets.QHBoxLayout()
        h_box_use_spm_standalone.addWidget(self.use_spm_standalone_checkbox)
        h_box_use_spm_standalone.addWidget(self.use_spm_standalone_label)
        h_box_use_spm_standalone.addStretch(1)

        h_box_spm_standalone_path = QtWidgets.QHBoxLayout()
        h_box_spm_standalone_path.addWidget(self.spm_standalone_choice)
        h_box_spm_standalone_path.addWidget(self.spm_standalone_browse)

        v_box_spm_standalone_path = QtWidgets.QVBoxLayout()
        v_box_spm_standalone_path.addWidget(self.spm_standalone_label)
        v_box_spm_standalone_path.addLayout(h_box_spm_standalone_path)

        v_box_spm = QtWidgets.QVBoxLayout()
        v_box_spm.addLayout(h_box_use_spm)
        v_box_spm.addLayout(v_box_spm_path)
        v_box_spm.addLayout(h_box_use_spm_standalone)
        v_box_spm.addLayout(v_box_spm_standalone_path)

        self.groupbox_spm.setLayout(v_box_spm)

        # Final tab layouts
        h_box_top = QtWidgets.QHBoxLayout()
        h_box_top.addWidget(self.groupbox_global)
        h_box_top.addStretch(1)

        self.tab_tools_layout = QtWidgets.QVBoxLayout()
        self.tab_tools_layout.addLayout(h_box_top)
        self.tab_tools_layout.addWidget(self.groupbox_matlab)
        self.tab_tools_layout.addWidget(self.groupbox_spm)
        self.tab_tools_layout.addStretch(1)
        self.tab_tools.setLayout(self.tab_tools_layout)

        # The 'OK' push button
        self.push_button_ok = QtWidgets.QPushButton("OK")
        self.push_button_ok.setObjectName("pushButton_ok")
        self.push_button_ok.clicked.connect(partial(self.ok_clicked, main_window))

        # The 'Cancel' push button
        self.push_button_cancel = QtWidgets.QPushButton("Cancel")
        self.push_button_cancel.setObjectName("pushButton_cancel")
        self.push_button_cancel.clicked.connect(self.close)

        # Buttons ayouts
        hbox_buttons = QHBoxLayout()
        hbox_buttons.addStretch(1)
        hbox_buttons.addWidget(self.push_button_ok)
        hbox_buttons.addWidget(self.push_button_cancel)

        vbox = QVBoxLayout()
        vbox.addWidget(self.tab_widget)
        vbox.addLayout(hbox_buttons)

        # The 'Appearance" tab
        self.tab_appearance = QtWidgets.QWidget()
        self.tab_appearance.setObjectName("tab_appearance")
        self.tab_widget.addTab(self.tab_appearance, _translate("Dialog", "Appearance"))

        self.appearance_layout = QVBoxLayout()
        self.label_background_color = QLabel("Background color")
        self.background_color_combo = QComboBox(self)
        self.background_color_combo.addItem("")
        self.background_color_combo.addItem("Black")
        self.background_color_combo.addItem("Blue")
        self.background_color_combo.addItem("Green")
        self.background_color_combo.addItem("Grey")
        self.background_color_combo.addItem("Orange")
        self.background_color_combo.addItem("Red")
        self.background_color_combo.addItem("Yellow")
        self.background_color_combo.addItem("White")
        background_color = config.getBackgroundColor()
        self.background_color_combo.setCurrentText(background_color)
        self.label_text_color = QLabel("Text color")
        self.text_color_combo = QComboBox(self)
        self.text_color_combo.addItem("")
        self.text_color_combo.addItem("Black")
        self.text_color_combo.addItem("Blue")
        self.text_color_combo.addItem("Green")
        self.text_color_combo.addItem("Grey")
        self.text_color_combo.addItem("Orange")
        self.text_color_combo.addItem("Red")
        self.text_color_combo.addItem("Yellow")
        self.text_color_combo.addItem("White")
        text_color = config.getTextColor()
        self.text_color_combo.setCurrentText(text_color)
        self.appearance_layout.addWidget(self.label_background_color)
        self.appearance_layout.addWidget(self.background_color_combo)
        self.appearance_layout.addWidget(self.label_text_color)
        self.appearance_layout.addWidget(self.text_color_combo)
        self.appearance_layout.addStretch(1)
        self.tab_appearance.setLayout(self.appearance_layout)

        self.setLayout(vbox)

        # Disabling widgets
        self.use_spm_changed()
        self.use_matlab_changed()

        # Signals
        self.use_matlab_checkbox.stateChanged.connect(self.use_matlab_changed)
        self.use_spm_checkbox.stateChanged.connect(self.use_spm_changed)
        self.use_spm_standalone_checkbox.stateChanged.connect(self.use_spm_standalone_changed)

    def use_spm_standalone_changed(self):
        """
        Called when the use_spm_standalone checkbox is changed
        """

        if not self.use_spm_standalone_checkbox.isChecked():
            self.spm_standalone_choice.setDisabled(True)
            self.spm_standalone_label.setDisabled(True)
            self.spm_standalone_browse.setDisabled(True)
        else:
            self.spm_standalone_choice.setDisabled(False)
            self.spm_standalone_label.setDisabled(False)
            self.spm_standalone_browse.setDisabled(False)
            self.spm_choice.setDisabled(True)
            self.spm_label.setDisabled(True)
            self.spm_browse.setDisabled(True)
            self.use_spm_checkbox.setChecked(False)

    def use_spm_changed(self):
        """
        Called when the use_spm checkbox is changed
        """

        if not self.use_spm_checkbox.isChecked():
            self.spm_choice.setDisabled(True)
            self.spm_label.setDisabled(True)
            self.spm_browse.setDisabled(True)
        else:
            self.spm_choice.setDisabled(False)
            self.spm_label.setDisabled(False)
            self.spm_browse.setDisabled(False)
            self.spm_standalone_choice.setDisabled(True)
            self.spm_standalone_label.setDisabled(True)
            self.spm_standalone_browse.setDisabled(True)
            self.use_spm_standalone_checkbox.setChecked(False)

    def use_matlab_changed(self):
        """
        Called when the use_matlab checkbox is changed
        """

        if not self.use_matlab_checkbox.isChecked():
            self.matlab_choice.setDisabled(True)
            self.matlab_standalone_choice.setDisabled(True)
            self.spm_choice.setDisabled(True)
            self.spm_standalone_choice.setDisabled(True)
            self.matlab_label.setDisabled(True)
            self.matlab_standalone_label.setDisabled(True)
            self.spm_label.setDisabled(True)
            self.spm_standalone_label.setDisabled(True)
            self.spm_browse.setDisabled(True)
            self.spm_standalone_browse.setDisabled(True)
            self.matlab_browse.setDisabled(True)
            self.matlab_standalone_browse.setDisabled(True)
            self.use_spm_checkbox.setChecked(False)
            self.use_spm_standalone_checkbox.setChecked(False)
        else:
            self.matlab_choice.setDisabled(False)
            self.matlab_standalone_choice.setDisabled(False)
            self.matlab_label.setDisabled(False)
            self.matlab_standalone_label.setDisabled(False)
            self.matlab_browse.setDisabled(False)
            self.matlab_standalone_browse.setDisabled(False)

    def browse_matlab(self):
        """
        Called when matlab browse button is clicked
        """

        fname = QFileDialog.getOpenFileName(self, 'Choose Matlab file')[0]
        if fname:
            self.matlab_choice.setText(fname)

    def browse_matlab_standalone(self):
        """
        Called when matlab browse button is clicked
        """

        fname = QFileDialog.getExistingDirectory(self, 'Choose MCR directory')
        if fname:
            self.matlab_standalone_choice.setText(fname)

    def browse_spm_standalone(self):
        """
        Called when spm standalone browse button is clicked
        """

        fname = QFileDialog.getExistingDirectory(self, 'Choose SPM standalone directory')
        if fname:
            self.spm_standalone_choice.setText(fname)

    def browse_spm(self):
        """
        Called when spm browse button is clicked
        """

        fname = QFileDialog.getExistingDirectory(self, 'Choose SPM directory')
        if fname:
            self.spm_choice.setText(fname)

    def ok_clicked(self, main):
        config = Config()

        # Auto-save
        if self.save_checkbox.isChecked():
            config.setAutoSave("yes")
        else:
            config.setAutoSave("no")

        # Use Matlab
        if self.use_matlab_checkbox.isChecked():
            config.set_use_matlab("yes")
        else:
            config.set_use_matlab("no")

        # Use SPM
        if self.use_spm_checkbox.isChecked():
            config.set_use_spm("yes")
        else:
            config.set_use_spm("no")

        # Use SPM standalone
        if self.use_spm_standalone_checkbox.isChecked():
            config.set_use_spm_standalone("yes")
        else:
            config.set_use_spm_standalone("no")

        # Clinical mode
        if self.clinical_mode_checkbox.isChecked():
            config.set_clinical_mode("yes")
            self.use_clinical_mode_signal.emit()
        else:
            config.set_clinical_mode("no")

        # Matlab
        if self.use_matlab_checkbox.isChecked():
            matlab_input = self.matlab_choice.text()
            if os.path.exists(matlab_input) or matlab_input == "":
                config.set_matlab_path(matlab_input)
            else:
                self.msg = QMessageBox()
                self.msg.setIcon(QMessageBox.Critical)
                self.msg.setText("Invalid Matlab path")
                self.msg.setInformativeText("The MCR path entered {0} is invalid.".format(matlab_input))
                self.msg.setWindowTitle("Error")
                self.msg.setStandardButtons(QMessageBox.Ok)
                self.msg.buttonClicked.connect(self.msg.close)
                self.msg.show()
                return

            matlab_standalone_input = self.matlab_standalone_choice.text()
            if os.path.exists(matlab_standalone_input) or matlab_standalone_input == "":
                config.set_matlab_standalone_path(matlab_standalone_input)
            else:
                self.msg = QMessageBox()
                self.msg.setIcon(QMessageBox.Critical)
                self.msg.setText("Invalid MCR path")
                self.msg.setInformativeText("The MCR path entered {0} is invalid.".format(matlab_standalone_input))
                self.msg.setWindowTitle("Error")
                self.msg.setStandardButtons(QMessageBox.Ok)
                self.msg.buttonClicked.connect(self.msg.close)
                self.msg.show()
                return

        # SPM
        if self.use_spm_checkbox.isChecked():
            spm_input = self.spm_choice.text()
            if os.path.exists(spm_input):
                config.set_spm_path(spm_input)
            else:
                self.msg = QMessageBox()
                self.msg.setIcon(QMessageBox.Critical)
                self.msg.setText("Invalid SPM standalone path")
                self.msg.setInformativeText("The SPM path entered {0} is invalid.".format(spm_input))
                self.msg.setWindowTitle("Error")
                self.msg.setStandardButtons(QMessageBox.Ok)
                self.msg.buttonClicked.connect(self.msg.close)
                self.msg.show()

        if self.use_spm_standalone_checkbox.isChecked():
            spm_input = self.spm_standalone_choice.text()
            if os.path.exists(spm_input) and "spm12" in spm_input:
                config.set_spm_standalone_path(spm_input)
            else:
                self.msg = QMessageBox()
                self.msg.setIcon(QMessageBox.Critical)
                self.msg.setText("Invalid SPM standalone path")
                self.msg.setInformativeText("The SPM standalone path entered {0} is invalid.".format(spm_input))
                self.msg.setWindowTitle("Error")
                self.msg.setStandardButtons(QMessageBox.Ok)
                self.msg.buttonClicked.connect(self.msg.close)
                self.msg.show()
                return

        #Colors
        background_color = self.background_color_combo.currentText()
        text_color = self.text_color_combo.currentText()
        config.setBackgroundColor(background_color)
        config.setTextColor(text_color)
        main.setStyleSheet("background-color:" + background_color + ";color:" + text_color + ";")

        self.signal_preferences_change.emit()
        self.accept()
        self.close()