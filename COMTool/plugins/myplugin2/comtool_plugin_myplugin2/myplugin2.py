'''
    @brief This is an example plugin, can receive and send data
    @author
    @date
    @license LGPL-3.0
'''
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLineEdit
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor

try:
    from plugins.base import Plugin_Base
    from conn import ConnectionStatus
except ImportError:
    from COMTool.plugins.base import Plugin_Base
    from COMTool.conn import  ConnectionStatus

# i18n for this plugin
# to use translation, use `comtool-i18n -p COMTool/plugins/myplugin2/comtool_plugin_myplugin2 prepare` first
#                     and translate file in locales dir
#                     use `comtool-i18n -p COMTool/plugins/myplugin2/comtool_plugin_myplugin2 finish` to generate translate binary files(*.mo)
# `comtool-i18n` command from comtool, or you can run source `python COMTool/i18n.py -p COMTool/plugins/myplugin2/comtool_plugin_myplugin2 prepare`
try:
    from .plugin_i18n import _
except Exception:
    from plugin_i18n import _

class Plugin(Plugin_Base):
    id = "myplugin2"
    name = _("my plugin2")
    updateSignal = pyqtSignal(str, str)

    def onConnChanged(self, status:ConnectionStatus, msg:str):
        print("-- connection changed: {}, msg: {}".format(status, msg))

    def onWidgetMain(self, parent):
        '''
            main widget, just return a QWidget object
        '''
        self.widget = QWidget()
        layout = QVBoxLayout()
        # receive widget
        self.receiveArea = QTextEdit("")
        font = QFont('Menlo,Consolas,Bitstream Vera Sans Mono,Courier New,monospace, Microsoft YaHei', 10)
        self.receiveArea.setFont(font)
        self.receiveArea.setLineWrapMode(QTextEdit.NoWrap)
        # send input widget
        self.input = QTextEdit()
        self.input.setAcceptRichText(False)
        # send button
        self.button = QPushButton(_("Send"))
        # add widgets
        layout.addWidget(self.receiveArea)
        layout.addWidget(self.input)
        layout.addWidget(self.button)
        self.widget.setLayout(layout)
        # event
        self.button.clicked.connect(self.buttonSend)
        self.updateSignal.connect(self.updateUI)
        return self.widget

    def buttonSend(self):
        '''
            UI thread
        '''
        data = self.input.toPlainText()
        if not data:
            # to pop up a warning window
            self.hintSignal.emit("error", _("Error"), _("Input data first please") )
            return
        dataBytes = data.encode(self.configGlobal["encoding"])
        self.send(dataBytes)

    def updateUI(self, dataType, data):
        '''
            UI thread
        '''
        if dataType == "receive":
            self.receiveArea.moveCursor(QTextCursor.End)
            self.receiveArea.insertPlainText(data)

    def onReceived(self, data : bytes):
        '''
            call in receive thread, not UI thread
        '''
        super().onReceived(data)
        # decode data
        dataStr = data.decode(self.configGlobal["encoding"])
        # DO NOT set seld.receiveBox here for all UI operation should be in UI thread,
        # instead, set self.receiveBox in UI thread, we can use signal to send data to UI thread
        self.updateSignal.emit("receive", dataStr)
