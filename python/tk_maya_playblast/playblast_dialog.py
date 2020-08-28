
import os
import re
import sys
import threading

import maya.cmds as cmds

import tank
from tank.platform.qt import QtCore, QtGui
from .ui.playblast_dialog import Ui_PlayblastDialog

SCALE_OPTIONS = [50, 100]


class PlayblastDialog(QtGui.QWidget):
    """
    Main application dialog window
    """

    def __init__(self, app, handler, parent=None):
        """
        Constructor
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent)

        self._app = app
        self._handler = handler

        # now load in the UI that was created in the UI designer
        self._ui = Ui_PlayblastDialog()
        self._ui.setupUi(self)
        self.__initComponents()

        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        # self._app = tank.platform.current_bundle()

        # via the self._app handle we can for example access:
        # - The engine, via self._app.engine
        # - A Shotgun API instance, via self._app.shotgun
        # - A tk API instance, via self._app.tk

        # lastly, set up our very basic UI
        # self._ui.context.setText("Current Shot: %s" % self._app.context)
        self._ui.btnPlayblast.clicked.connect(self.doPlayblast)

    def __initComponents(self):
        # Setting up playblast resolution percentage. Customizable through
        # optional "scale_options" field in app settings.
        scaleIntList = self._app.get_setting("scale_options", SCALE_OPTIONS)
        for percentInt in scaleIntList:
            self._ui.cmbPercentage.addItem("%d%%" % percentInt, userData=percentInt)

        # Get all cameras first
        cameras = cmds.ls(type=('camera'), l=True)
        # Let's filter all startup / default cameras
        startup_cameras = [camera for camera in cameras if cmds.camera(cmds.listRelatives(camera, parent=True)[0], startupCamera=True, q=True)]
        # non-default cameras are easy to find now.
        non_startup_cameras = list(set(cameras) - set(startup_cameras))
        # Let's get their respective transform names, just in-case
        startup_cameras_transforms = map(lambda x: cmds.listRelatives(x, parent=True)[0], startup_cameras)
        non_startup_cameras_transforms = map(lambda x: cmds.listRelatives(x, parent=True)[0], non_startup_cameras)

        for c in non_startup_cameras_transforms:
            self._ui.cmbCamera.addItem(c, userData=c)
        for c in startup_cameras_transforms:
            self._ui.cmbCamera.addItem(c, userData=c)
        self._ui.cmbCamera.insertSeparator(len(non_startup_cameras_transforms))

    def doPlayblast(self):
        overridePlayblastParams = {}

        # uploadToShotgun = self._ui.chbUploadToShotgun.isChecked()
        # self._handler.setUploadToShotgun(uploadToShotgun)

        showViewer = self._ui.chbShowViewer.isChecked()
        overridePlayblastParams["viewer"] = showViewer

        percentInt = self._ui.cmbPercentage.itemData(self._ui.cmbPercentage.currentIndex())
        overridePlayblastParams["percent"] = percentInt

        camera = self._ui.cmbCamera.itemData(self._ui.cmbCamera.currentIndex())

        self._handler.doPlayblast(playblastCamera=camera, **overridePlayblastParams)
        self.close()
