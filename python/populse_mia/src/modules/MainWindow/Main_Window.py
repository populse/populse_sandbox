##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

'''
Created on 11 janv. 2018

@author: omonti

'''
import subprocess
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QAction, QLineEdit, \
    QMainWindow, QMessageBox, QMenu, QPushButton
from SoftwareProperties.SavedProjects import SavedProjects
from SoftwareProperties.Config import Config
import DataBrowser.DataBrowser
from ImageViewer.ImageViewer import ImageViewer
from PipelineManager.PipelineManagerTab import PipelineManagerTab
from PopUps.Ui_Dialog_New_Project import Ui_Dialog_New_Project
from PopUps.Ui_Dialog_Open_Project import Ui_Dialog_Open_Project
from PopUps.Ui_Dialog_Preferences import Ui_Dialog_Preferences
from PopUps.Ui_Dialog_Settings import Ui_Dialog_Settings
from PopUps.Ui_Dialog_Save_Project_As import Ui_Dialog_Save_Project_As
from PopUps.Ui_Dialog_Quit import Ui_Dialog_Quit
from PopUps.Ui_Dialog_See_All_Projects import Ui_Dialog_See_All_Projects

import ProjectManager.Controller as controller
import shutil
from Project.Project import Project, COLLECTION_CURRENT

from datetime import datetime


class Main_Window(QMainWindow):
    """
    Primary master class

    Attributes
    ----------


    Methods
    -------


    """
    def __init__(self, project, test=False):

        ############### Main Window ################################################################
        super(Main_Window, self).__init__()

        self.project = project
        self.test = test
        self.force_exit = False
        app_icon = QIcon(os.path.join('..', 'sources_images', 'brain_mri.jpeg'))
        self.setWindowIcon(app_icon)

        ############### initial setting ############################################################
        config = Config()

        self.saved_projects = SavedProjects()
        self.saved_projects_list = self.saved_projects.pathsList

        self.saved_projects_actions = []

        ################ Create actions & menus ####################################################

        config = Config()
        background_color = config.getBackgroundColor()
        text_color = config.getTextColor()
        self.setStyleSheet("background-color:" + background_color + ";color:" + text_color + ";")

        self.create_actions()
        self.create_menus()

        self.setWindowTitle('MIA - Multiparametric Image Analysis')
        self.statusBar().showMessage('Please create a new project (Ctrl+N) or open an existing project (Ctrl+O)')

        # BELOW : WAS AT THE END OF MODIFY_UI
        self.setWindowTitle('MIA - Multiparametric Image Analysis - Unnamed project')
        ################ Create Tabs ###############################################################
        self.create_tabs()
        self.setCentralWidget(self.centralWindow)
        self.showMaximized()

    def create_actions(self):
        """ Create the actions in each menu """

        self.action_create = QAction('New project', self)
        self.action_create.setShortcut('Ctrl+N')

        self.action_open = QAction('Open project', self)
        self.action_open.setShortcut('Ctrl+O')

        self.action_save = QAction('Save project', self)
        self.action_save.setShortcut('Ctrl+S')

        self.action_save_as = QAction('Save project as', self)
        self.action_save_as.setShortcut('Ctrl+Shift+S')

        self.action_import = QAction(QIcon(os.path.join('..', 'sources_images', 'Blue.png')), 'Import', self)
        self.action_import.setShortcut('Ctrl+I')

        for i in range(self.saved_projects.maxProjects):
            self.saved_projects_actions.append(QAction(self, visible=False,
                                                       triggered=self.open_recent_project))

        self.action_see_all_projects = QAction('See all projects', self)

        self.action_project_properties = QAction('Project properties', self)

        self.action_software_preferences = QAction('MIA preferences', self)

        self.action_package_library = QAction('Package library manager', self)
        if Config().get_clinical_mode() == 'yes':
            self.action_package_library.setDisabled(True)
        else:
            self.action_package_library.setEnabled(True)

        self.action_exit = QAction(QIcon(os.path.join('..', 'sources_images', 'exit.png')), 'Exit', self)
        self.action_exit.setShortcut('Ctrl+W')

        self.action_undo = QAction('Undo', self)
        self.action_undo.setShortcut('Ctrl+Z')

        self.action_redo = QAction('Redo', self)
        self.action_redo.setShortcut('Ctrl+Y')

        self.action_install_processes_folder = QAction('From folder', self)
        self.action_install_processes_zip = QAction('From zip file', self)
        # if Config().get_clinical_mode() == 'yes':
        #     self.action_install_processes.setDisabled(True)
        # else:
        #     self.action_install_processes.setEnabled(True)

        # Connection of the several triggered signals of the actions to some other methods
        self.action_create.triggered.connect(self.create_project_pop_up)
        self.action_open.triggered.connect(self.open_project_pop_up)
        self.action_exit.triggered.connect(self.close)
        self.action_save.triggered.connect(self.saveChoice)
        self.action_save_as.triggered.connect(self.save_project_as)
        self.action_import.triggered.connect(self.import_data)
        self.action_see_all_projects.triggered.connect(self.see_all_projects)
        self.action_project_properties.triggered.connect(self.project_properties_pop_up)
        self.action_software_preferences.triggered.connect(self.software_preferences_pop_up)
        self.action_package_library.triggered.connect(self.package_library_pop_up)
        self.action_undo.triggered.connect(self.undo)
        self.action_redo.triggered.connect(self.redo)
        self.action_install_processes_folder.triggered.connect(lambda: self.install_processes_pop_up(folder=True))
        self.action_install_processes_zip.triggered.connect(lambda: self.install_processes_pop_up(folder=False))

    def create_menus(self):
        """ Create the menubar """

        # Menubar
        self.menu_file = self.menuBar().addMenu('File')
        self.menu_edition = self.menuBar().addMenu('Edit')
        self.menu_help = self.menuBar().addMenu('Help')
        self.menu_about = self.menuBar().addMenu('About')
        self.menu_more = self.menuBar().addMenu('More')
        self.menu_install_process = QMenu('Install processes', self)
        self.menu_more.addMenu(self.menu_install_process)

        # Submenu of menu_file menu
        self.menu_saved_projects = QMenu('Saved projects', self)

        # Actions in the "File" menu
        self.menu_file.addAction(self.action_create)
        self.menu_file.addAction(self.action_open)
        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_save_as)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_import)
        self.menu_file.addSeparator()
        self.menu_file.addMenu(self.menu_saved_projects)
        for i in range(self.saved_projects.maxProjects):
            self.menu_saved_projects.addAction(self.saved_projects_actions[i])
        self.menu_saved_projects.addSeparator()
        self.menu_saved_projects.addAction(self.action_see_all_projects)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_software_preferences)
        self.menu_file.addAction(self.action_project_properties)
        self.menu_file.addAction(self.action_package_library)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_exit)
        self.update_recent_projects_actions()

        # Actions in the "Edition" menu
        self.menu_edition.addAction(self.action_undo)
        self.menu_edition.addAction(self.action_redo)

        # Actions in the "Help" menu
        self.menu_help.addAction('Documentations')
        self.menu_help.addAction('Credits')

        # Actions in the "More > Install processes" menu
        self.menu_install_process.addAction(self.action_install_processes_folder)
        self.menu_install_process.addAction(self.action_install_processes_zip)

    def undo(self):
        """
        To undo the last action done by the user
        """
        if self.tabs.tabText(self.tabs.currentIndex()) == 'Data Browser':
            # In Data Browser
            self.project.undo(self.data_browser.table_data)  # Action reverted in the Database
        elif self.tabs.tabText(self.tabs.currentIndex()) == 'Pipeline Manager':
            # In Pipeline Manager
            self.pipeline_manager.undo()

    def redo(self):
        """
        To redo the last action made by the user
        """
        if self.tabs.tabText(self.tabs.currentIndex()) == 'Data Browser':
            # In Data Browser
            self.project.redo(self.data_browser.table_data)  # Action remade in the Database
        elif self.tabs.tabText(self.tabs.currentIndex()) == 'Pipeline Manager':
            # In Pipeline Manager
            self.pipeline_manager.redo()

    def closeEvent(self, event):
        """ Overriding the closing event to check if there are unsaved modifications """

        if self.force_exit:
            event.accept()
            return
        if self.check_unsaved_modifications():
            self.pop_up_close = Ui_Dialog_Quit(self.project)
            self.pop_up_close.save_as_signal.connect(self.saveChoice)
            self.pop_up_close.exec()
            can_exit = self.pop_up_close.can_exit()

        else:
            can_exit = True

        if can_exit:
            self.project.unsaveModifications()

            # Clean up
            config = Config()
            opened_projects = config.get_opened_projects()
            opened_projects.remove(self.project.folder)
            config.set_opened_projects(opened_projects)
            self.remove_raw_files_useless()

            event.accept()
        else:
            event.ignore()

    def remove_raw_files_useless(self):
        """
        Removes the useless raw files of the current project
        """
        import glob

        # If it's unnamed project, we can remove the whole project
        if self.project.isTempProject:
            self.project.database.__exit__(None, None, None)
            shutil.rmtree(self.project.folder)
        else:
            for filename in glob.glob(os.path.join(os.path.relpath(self.project.folder), 'data', 'raw_data', '*')):
                scan = os.path.basename(filename)
                # The file is removed only if it's not a scan in the project, and if it's not a logExport
                # Json files associated to nii files are kept for the raw_data folder
                file_name, file_extension = os.path.splitext(scan)
                file_in_database = False
                for database_scan in self.project.session.get_documents_names(COLLECTION_CURRENT):
                    if file_name in database_scan:
                        file_in_database = True
                if "logExport" in scan:
                    file_in_database = True
                if not file_in_database:
                    os.remove(filename)
            for filename in glob.glob(os.path.join(os.path.relpath(self.project.folder), 'data', 'derived_data', '*')):
                scan = os.path.basename(filename)
                # The file is removed only if it's not a scan in the project, and if it's not a logExport
                if self.project.session.get_document(COLLECTION_CURRENT, os.path.join("data", "derived_data", scan)) is None and "logExport" not in scan:
                    os.remove(filename)
            for filename in glob.glob(os.path.join(os.path.relpath(self.project.folder), 'data', 'downloaded_data', '*')):
                scan = os.path.basename(filename)
                # The file is removed only if it's not a scan in the project, and if it's not a logExport
                if self.project.session.get_document(COLLECTION_CURRENT, os.path.join("data", "downloaded_data", scan)) is None and "logExport" not in scan:
                    os.remove(filename)
            self.project.database.__exit__(None, None, None)

    def saveChoice(self):
        """ Checks if the project needs to be saved as or just saved """
        if self.project.isTempProject:
            self.save_project_as()
        else:
            controller.save_project(self.project)

    def check_unsaved_modifications(self):
        """ Check if there are differences between the current project and the data base
            Returns 1 if there are unsaved modifications, 0 otherwise
        """
        if self.project.isTempProject and len(self.project.session.get_documents_names(COLLECTION_CURRENT)) > 0:
            return 1
        if self.project.isTempProject:
            return 0
        if self.project.hasUnsavedModifications():
            return 1
        else:
            return 0

    def create_tabs(self):
        """ Creates the tabs """
        self.config = Config()

        self.tabs = QTabWidget()
        self.tabs.setAutoFillBackground(False)
        #self.tabs.setStyleSheet('QTabBar{font-size:14pt;font-family:Helvetica;text-align: center;color:blue;}')
        self.tabs.setStyleSheet('QTabBar{font-size:16pt;text-align: center}')
        self.tabs.setMovable(True)

        self.data_browser = DataBrowser.DataBrowser.DataBrowser(self.project, self)
        self.tabs.addTab(self.data_browser, "Data Browser")

        self.image_viewer = ImageViewer()
        self.tabs.addTab(self.image_viewer, "Data Viewer")

        self.pipeline_manager = PipelineManagerTab(self.project, [], self)
        self.tabs.addTab(self.pipeline_manager, "Pipeline Manager")

        self.tabs.currentChanged.connect(self.tab_changed)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.tabs)
        self.centralWindow = QWidget()
        self.centralWindow.setLayout(vertical_layout)

    def save_project_as(self):
        """ Open a pop-up to save the current project as """

        import glob
        self.exPopup = Ui_Dialog_Save_Project_As()
        if self.exPopup.exec_():

            old_folder = self.project.folder
            file_name = self.exPopup.relative_path
            data_path = os.path.join(os.path.relpath(self.exPopup.relative_path), 'data')
            database_path = os.path.join(os.path.relpath(self.exPopup.relative_path), 'database')
            properties_path = os.path.join(os.path.relpath(self.exPopup.relative_path), 'properties')
            filters_path = os.path.join(os.path.relpath(self.exPopup.relative_path), 'filters')
            data_path = os.path.join(os.path.relpath(self.exPopup.relative_path), 'data')
            raw_data_path = os.path.join(data_path, 'raw_data')
            derived_data_path = os.path.join(data_path, 'derived_data')
            downloaded_data_path = os.path.join(data_path, 'downloaded_data')

            # List of projects updated
            if not self.test:
                self.saved_projects_list = self.saved_projects.addSavedProject(file_name)
            self.update_recent_projects_actions()

            os.makedirs(self.exPopup.relative_path)

            os.mkdir(data_path)
            os.mkdir(raw_data_path)
            os.mkdir(derived_data_path)
            os.mkdir(downloaded_data_path)
            os.mkdir(filters_path)

            # Data files copied
            if os.path.exists(os.path.join(old_folder, 'data')):
                for filename in glob.glob(os.path.join(os.path.relpath(old_folder), 'data', 'raw_data', '*')):
                    shutil.copy(filename, os.path.join(os.path.relpath(data_path), 'raw_data'))
                for filename in glob.glob(os.path.join(os.path.relpath(old_folder), 'data', 'derived_data', '*')):
                    shutil.copy(filename, os.path.join(os.path.relpath(data_path), 'derived_data'))
                for filename in glob.glob(os.path.join(os.path.relpath(old_folder), 'data', 'downloaded_data', '*')):
                    shutil.copy(filename, os.path.join(os.path.relpath(data_path), 'downloaded_data'))

            if os.path.exists(os.path.join(old_folder, 'filters')):
                for filename in glob.glob(os.path.join(os.path.relpath(old_folder), 'filters', '*')):
                    shutil.copy(filename, os.path.join(os.path.relpath(filters_path)))

            # First we register the Database before commiting the last pending modifications
            shutil.copy(os.path.join(os.path.relpath(old_folder), 'database', 'mia.db'), os.path.join(os.path.relpath(old_folder), 'database', 'mia_before_commit.db'))

            # We commit the last pending modifications
            self.project.saveModifications()

            os.mkdir(properties_path)
            shutil.copy(os.path.join(os.path.relpath(old_folder), 'properties', 'properties.yml'), os.path.relpath(properties_path))

            # We copy the Database with all the modifications commited in the new project
            os.mkdir(os.path.relpath(database_path))
            shutil.copy(os.path.join(os.path.relpath(old_folder), 'database', 'mia.db'), os.path.relpath(database_path))

            # We remove the Database with all the modifications saved in the old project
            os.remove(os.path.join(os.path.relpath(old_folder), 'database', 'mia.db'))

            # We reput the Database without the last modifications in the old project
            shutil.copy(os.path.join(os.path.relpath(old_folder), 'database', 'mia_before_commit.db'), os.path.join(os.path.relpath(old_folder), 'database', 'mia.db'))

            os.remove(os.path.join(os.path.relpath(old_folder), 'database', 'mia_before_commit.db'))

            self.remove_raw_files_useless() # We remove the useless files from the old project

            # Removing the old project from the list of currently opened projects
            config = Config()
            opened_projects = config.get_opened_projects()
            opened_projects.remove(self.project.folder)
            config.set_opened_projects(opened_projects)

            # Project updated everywhere
            self.project = Project(self.exPopup.relative_path, False)
            self.project.setName(os.path.basename(self.exPopup.relative_path))
            self.project.setDate(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
            self.project.saveModifications()

            self.update_project(file_name, call_update_table=False) # Project updated everywhere

    def create_project_pop_up(self):

        if self.check_unsaved_modifications():
            self.pop_up_close = Ui_Dialog_Quit(self.project)
            self.pop_up_close.save_as_signal.connect(self.saveChoice)
            self.pop_up_close.exec()
            can_switch = self.pop_up_close.can_exit()

        else:
            can_switch = True
        if can_switch:

            # Opens a pop-up when the 'New Project' action is clicked and updates the recent projects
            self.exPopup = Ui_Dialog_New_Project()

            if self.exPopup.exec_():

                self.project.session.unsave_modifications()
                self.remove_raw_files_useless()  # We remove the useless files from the old project

                file_name = self.exPopup.selectedFiles()
                self.exPopup.retranslateUi(self.exPopup.selectedFiles())
                file_name = self.exPopup.relative_path

                # Removing the old project from the list of currently opened projects
                config = Config()
                opened_projects = config.get_opened_projects()
                opened_projects.remove(self.project.folder)
                config.set_opened_projects(opened_projects)

                self.project = Project(self.exPopup.relative_path, True)

                self.update_project(file_name) # Project updated everywhere

    def open_project_pop_up(self):
        """ Opens a pop-up when the 'Open Project' action is clicked and updates the recent projects """
        # Ui_Dialog() is defined in pop_ups.py

        self.exPopup = Ui_Dialog_Open_Project()
        if self.exPopup.exec_():

            file_name = self.exPopup.selectedFiles()
            self.exPopup.retranslateUi(file_name)
            file_name = self.exPopup.relative_path

            self.switch_project(self.exPopup.relative_path, file_name, self.exPopup.name)  # We switch project

    def open_recent_project(self):
        """ Opens a recent project """
        action = self.sender()
        if action:
            file_name = action.data()
            entire_path = os.path.abspath(file_name)
            path, name = os.path.split(entire_path)
            relative_path = os.path.relpath(file_name)

            self.switch_project(relative_path, file_name, name) # We switch project

    def switch_project(self, path, file_name, name):
        """
        Called to switch project if it's possible
        :param path: relative path of the new project
        :param file_name: raw file_name
        :param name: project name
        """

        # Switching project only if it's a different one
        if path != self.project.folder:

            # If the file exists
            if os.path.exists(os.path.join(path)):

                if os.path.exists(os.path.join(path, "properties", "properties.yml")) and os.path.exists(os.path.join(path, "database", "mia.db")) and os.path.exists(os.path.join(path, "data", "raw_data")) and os.path.exists(os.path.join(path, "data", "derived_data")) and os.path.exists(os.path.join(path, "data", "downloaded_data")) and os.path.exists(os.path.join(path, "filters")):

                    # We check for unsaved modifications
                    if self.check_unsaved_modifications():

                        # If there are unsaved modifications, we ask the user what he wants to do
                        self.pop_up_close = Ui_Dialog_Quit(self.project)
                        self.pop_up_close.save_as_signal.connect(self.saveChoice)
                        self.pop_up_close.exec()
                        can_switch = self.pop_up_close.can_exit()

                    else:
                        can_switch = True

                    # We can open a new project
                    if can_switch:

                        # We check for invalid scans in the project

                        try:
                            tempDatabase = Project(path, False)
                        except IOError:
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText(
                                "Project already opened")
                            msg.setInformativeText(
                                "The project at " + str(path) + " is already opened in another instance of the software.")
                            msg.setWindowTitle("Warning")
                            msg.setStandardButtons(QMessageBox.Ok)
                            msg.buttonClicked.connect(msg.close)
                            msg.exec()
                            return False
                        problem_list = controller.verify_scans(tempDatabase, path)

                        # Message if invalid files
                        if problem_list != []:
                            str_msg = ""
                            for element in problem_list:
                                str_msg += element + "\n\n"
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText(
                                "These files have been modified or removed since they have been converted for the first time:")
                            msg.setInformativeText(str_msg)
                            msg.setWindowTitle("Warning")
                            msg.setStandardButtons(QMessageBox.Ok)
                            msg.buttonClicked.connect(msg.close)
                            msg.exec()

                    self.project.session.unsave_modifications()
                    self.remove_raw_files_useless()  # We remove the useless files from the old project

                    # Project removed from the opened projects list
                    config = Config()
                    opened_projects = config.get_opened_projects()
                    opened_projects.remove(self.project.folder)
                    config.set_opened_projects(opened_projects)

                    self.project = tempDatabase  # New Database

                    self.update_project(file_name) # Project updated everywhere

                    return True

                # Not a MIA project
                else:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText("The project selected isn't a valid MIA project")
                    msg.setInformativeText(
                        "The project selected " + name + " isn't a MIA project.\nPlease select a valid one.")
                    msg.setWindowTitle("Warning")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.buttonClicked.connect(msg.close)
                    msg.exec()
                    return False

            # The project doesn't exist anymore
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("The project selected doesn't exist anymore")
                msg.setInformativeText(
                    "The project selected " + name + " doesn't exist anymore.\nPlease select another one.")
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(msg.close)
                msg.exec()
                return False

    def update_project(self, file_name, call_update_table=True):
        """
        Updates the project once the Database has been updated
        :param file_name: File name of the new project
        """

        self.data_browser.update_database(self.project)  # Database update DataBrowser
        self.pipeline_manager.update_project(self.project)

        if call_update_table:
            self.data_browser.table_data.update_table() # Table updated

        # Window name updated
        if self.project.isTempProject:
            self.setWindowTitle('MIA - Multiparametric Image Analysis - Unnamed project')
        else:
            self.setWindowTitle('MIA - Multiparametric Image Analysis - ' + self.project.getName())

        # List of project updated
        if not self.test:
            self.saved_projects_list = self.saved_projects.addSavedProject(file_name)
        self.update_recent_projects_actions()

    def update_recent_projects_actions(self):
        """ Updates the list of recent projects """
        if self.saved_projects_list != []:
            for i in range(min(len(self.saved_projects_list), self.saved_projects.maxProjects)):
                text = os.path.basename(self.saved_projects_list[i])
                self.saved_projects_actions[i].setText(text)
                self.saved_projects_actions[i].setData(self.saved_projects_list[i])
                self.saved_projects_actions[i].setVisible(True)

    def see_all_projects(self):
        """ Opens a pop-up when the 'See all projects' action is clicked and show the recent projects """
        # Ui_Dialog() is defined in pop_ups.py
        self.exPopup = Ui_Dialog_See_All_Projects(self.saved_projects, self)
        if self.exPopup.exec_():
            file_name = self.exPopup.relative_path
            if not self.test:
                self.saved_projects_list = self.saved_projects.addSavedProject(file_name)
            self.update_recent_projects_actions()

    def project_properties_pop_up(self):
        """ Opens the Project properties pop-up """

        old_tags = self.project.session.get_visibles()
        self.pop_up_settings = Ui_Dialog_Settings(self.project, self.data_browser, old_tags)
        self.pop_up_settings.setGeometry(300, 200, 800, 600)
        self.pop_up_settings.show()

        if self.pop_up_settings.exec_():
            self.data_browser.table_data.update_visualized_columns(old_tags, self.project.session.get_visibles())

    def software_preferences_pop_up(self):
        """ Opens the MIA2 preferences pop-up """

        self.pop_up_preferences = Ui_Dialog_Preferences(self)
        self.pop_up_preferences.setGeometry(300, 200, 800, 600)
        self.pop_up_preferences.show()
        self.pop_up_preferences.use_clinical_mode_signal.connect(self.add_clinical_tags)

        # Modifying the options in the Pipeline Manager (verify if clinical mode)
        self.pop_up_preferences.signal_preferences_change.connect(self.pipeline_manager.update_clinical_mode)
        self.pop_up_preferences.signal_preferences_change.connect(self.update_package_library_action)

    def update_package_library_action(self):
        """ Updates the package library action depending on the mode """
        if Config().get_clinical_mode() == 'yes':
            self.action_package_library.setDisabled(True)
            # self.action_install_processes.setDisabled(True)
        else:
            self.action_package_library.setEnabled(True)
            # self.action_install_processes.setEnabled(True)

    def package_library_pop_up(self):
        """ Opens the package library pop-up """
        from PipelineManager.process_library import PackageLibraryDialog
        self.pop_up_package_library = PackageLibraryDialog(self)
        self.pop_up_package_library.setGeometry(300, 200, 800, 600)
        self.pop_up_package_library.show()
        self.pop_up_package_library.signal_save.connect(self.pipeline_manager.processLibrary.update_process_library)

    def install_processes_pop_up(self, folder=False):
        """ Opens the install processes pop-up """
        from PipelineManager.process_library import InstallProcesses
        self.pop_up_install_processes = InstallProcesses(self, folder=folder)
        self.pop_up_install_processes.show()
        self.pop_up_install_processes.process_installed.connect(self.pipeline_manager.processLibrary.update_process_library)
        self.pop_up_install_processes.process_installed.connect(self.pipeline_manager.processLibrary.pkg_library.update_config)

    def add_clinical_tags(self):
        """ Adds the clinical tags to the database and the data browser """
        added_tags = self.project.add_clinical_tags()
        for tag in added_tags:
            column = self.data_browser.table_data.get_index_insertion(tag)
            self.data_browser.table_data.add_column(column, tag)

    def import_data(self):
        """ Calls the import software (MRI File Manager), reads the imported files and loads them into the
         data base """
        # Opens the conversion software to convert the MRI files in Nifti/Json
        code_exit = subprocess.call(['java', '-Xmx4096M', '-jar', os.path.join('..', '..', 'ressources', 'mia', 'MRIFileManager', 'MRIManager.jar'),
                         '[ExportNifti] ' + os.path.join(self.project.folder, 'data', 'raw_data'),
                         '[ExportToMIA] PatientName-StudyName-CreationDate-SeqNumber-Protocol-SequenceName-AcquisitionTime',
                         'CloseAfterExport'])
        # 'NoLogExport'if we don't want log export

        if code_exit == 0:

            #import cProfile

            # Database filled
            new_scans = controller.read_log(self.project, self)

            # Table updated
            documents = self.project.session.get_documents_names(COLLECTION_CURRENT)
            self.data_browser.table_data.scans_to_visualize = documents
            self.data_browser.table_data.scans_to_search = documents
            self.data_browser.table_data.add_columns()
            self.data_browser.table_data.fill_headers()
            self.data_browser.table_data.add_rows(new_scans)
            self.data_browser.reset_search_bar()
            self.data_browser.frame_advanced_search.setHidden(True)
            self.data_browser.advanced_search.rows = []

        else:
            pass

    def tab_changed(self):
        """
        Method called when the tab is changed
        """

        if self.tabs.tabText(self.tabs.currentIndex()) == 'Data Browser':
            # DataBrowser refreshed after working with pipelines
            old_scans = self.data_browser.table_data.scans_to_visualize
            documents = self.project.session.get_documents_names(COLLECTION_CURRENT)

            self.data_browser.table_data.add_columns()
            self.data_browser.table_data.fill_headers()

            self.data_browser.table_data.add_rows(documents)

            self.data_browser.table_data.scans_to_visualize = documents
            self.data_browser.table_data.scans_to_search = documents

            self.data_browser.table_data.itemChanged.disconnect()
            self.data_browser.table_data.fill_cells_update_table()
            self.data_browser.table_data.itemChanged.connect(self.data_browser.table_data.change_cell_color)

            self.data_browser.table_data.update_visualized_rows(old_scans)

            # Advanced search + search_bar opened
            old_search = self.project.currentFilter.search_bar
            self.data_browser.reset_search_bar()
            self.data_browser.search_bar.setText(old_search)

            if len(self.project.currentFilter.nots) > 0:
                self.data_browser.frame_advanced_search.setHidden(False)
                self.data_browser.advanced_search.scans_list = self.data_browser.table_data.scans_to_visualize
                self.data_browser.advanced_search.show_search()
                self.data_browser.advanced_search.apply_filter(self.project.currentFilter)

        elif self.tabs.tabText(self.tabs.currentIndex()) == 'Pipeline Manager':
            # Pipeline Manager
            # The pending modifications must be saved before working with pipelines (auto_commit)
            if self.project.hasUnsavedModifications():
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Unsaved modifications in the Data Browser !")
                msg.setInformativeText(
                    "There are unsaved modifications in the database, "
                    "you need to save or remove them before working with pipelines.")
                msg.setWindowTitle("Warning")
                save_button = QPushButton("Save")
                save_button.clicked.connect(self.project.saveModifications)
                unsave_button = QPushButton("Not Save")
                unsave_button.clicked.connect(self.project.unsaveModifications)
                msg.addButton(save_button, QMessageBox.AcceptRole)
                msg.addButton(unsave_button, QMessageBox.AcceptRole)
                msg.exec()
