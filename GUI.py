# -*- coding: utf-8 -*-
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PIL.ImageQt import ImageQt
import from_dxf_to_image
import main

class ModalWind(QDialog):

    def __init__(self, parent=None):
        super(ModalWind, self).__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.WindowSystemMenuHint)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("Ввод параметров")

        # OK and Cancel buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)

        label1 = QLabel(("Количество 1-K квартир"))
        label2 = QLabel(("Количество 2-K квартир"))
        label3 = QLabel(("Количество 3-K квартир"))
        label4 = QLabel(("Количество 4-K квартир"))
        self.k1 = QLineEdit()
        self.k2 = QLineEdit()
        self.k3 = QLineEdit()
        self.k4 = QLineEdit()

        vbox = QVBoxLayout()
        vbox.addWidget(label1)
        vbox.addWidget(self.k1)
        vbox.addWidget(label2)
        vbox.addWidget(self.k2)
        vbox.addWidget(label3)
        vbox.addWidget(self.k3)
        vbox.addWidget(label4)
        vbox.addWidget(self.k4)
        vbox.addWidget(self.buttons)
        self.setLayout(vbox)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

class MySplashScreen(QSplashScreen):
    def __init__(self, animation, flags):
        # run event dispatching in another thread
        QSplashScreen.__init__(self, QPixmap(), flags)
        self.movie = QMovie(animation)
        self.movie.frameChanged.connect(self.onNextFrame)
        #self.connect(self.movie, SIGNAL('frameChanged(int)'), SLOT('onNextFrame()'))
        self.movie.start()


    def onNextFrame(self):
        pixmap = self.movie.currentPixmap()
        self.setPixmap(pixmap)
        self.setMask(pixmap.mask())

class ImageViewer(QMainWindow):
    def __init__(self):
        super(ImageViewer, self).__init__()

        self.printer = QPrinter()
        self.scaleFactor = 0.0

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored,
                QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.setCentralWidget(self.scrollArea)

        self.createActions()
        self.createMenus()

        self.createToolBar()

        self.setWindowTitle("Авто-Планировщик")
        self.resize(500, 400)

    def handleButton(self):
        print ('Hello World')

    def open(self):
        global fileName
        fileName = QFileDialog.getOpenFileName(self, "Open File",
                QDir.currentPath())
        if fileName:
            from_dxf_to_image.main_def(fileName)
            image = QImage('temp_file.jpg')
            if image.isNull():
                QMessageBox.information(self, "Image Viewer",
                        "Cannot load %s." % fileName)
                return

            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.scaleFactor = 1.0

            self.printAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

    def print_(self):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def Close(self):
        self.close()
        os.remove('temp_file.jpg')

    def about(self):
        QMessageBox.about(self, "About Image Viewer",
                "<p>The <b>Image Viewer</b> example shows how to combine "
                "QLabel and QScrollArea to display an image. QLabel is "
                "typically used for displaying text, but it can also display "
                "an image. QScrollArea provides a scrolling view around "
                "another widget. If the child widget exceeds the size of the "
                "frame, QScrollArea automatically provides scroll bars.</p>"
                "<p>The example demonstrates how QLabel's ability to scale "
                "its contents (QLabel.scaledContents), and QScrollArea's "
                "ability to automatically resize its contents "
                "(QScrollArea.widgetResizable), can be used to implement "
                "zooming and scaling features.</p>"
                "<p>In addition the example shows how to use QPainter to "
                "print an image.</p>")

    def createActions(self):
        self.openAct = QAction("Открыть...", self, shortcut="Ctrl+O",
                triggered=self.open)

        self.printAct = QAction("Печать...", self, shortcut="Ctrl+P",
                enabled=False, triggered=self.print_)

        self.exitAct = QAction("Выход", self, shortcut="Ctrl+Q",
                triggered=self.Close)

        self.zoomInAct = QAction("Zoom &In (25%)", self,
                shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QAction("Zoom &Out (25%)", self,
                shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QAction("&Normal Size", self,
                shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)

        self.aboutAct = QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                triggered=qApp.aboutQt)

    def createMenus(self):
        self.fileMenu = QMenu("&Файл", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QMenu("&Вид", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.helpMenu = QMenu("&Помощь", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))

    def createToolBar(self):
        exitAction = QAction(QIcon('exit24.png'), 'Locate', self)
        exitAction.setShortcut('Ctrl+L')
        exitAction.triggered.connect(self.on_show)

        self.toolbar = self.addToolBar('Locate')
        self.setStyleSheet("""QToolBar {
             background-color: DarkSlateGray;
        }""")
        self.toolbar.addAction(exitAction)

        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle('Toolbar')
        self.show()

    def on_show(self):
        win = ModalWind(self)
        win.resize(200, 100)
        # сначало отображаем окно за пределами видимости
        win.move(win.width()*-2,0)
        # обязательно отображаем, потому-что, только так frameSize()
        # вернет коректное значение
        win.show()
        x = self.x()+(self.frameSize().width()-win.frameSize().width())//2
        y = self.y()+(self.frameSize().height()-win.frameSize().height())//2
        win.move(x, y)
        result = win.exec_()

        if result:
            splash = MySplashScreen('giphy.gif', Qt.WindowStaysOnTopHint)
            splash.show()
            app.processEvents()

            main.main(fileName, int(win.k1.text()), int(win.k2.text()), int(win.k3.text()), int(win.k4.text()))

            image = QImage('temp_file.jpg')

            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.scaleFactor = 1.0

            self.printAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    imageViewer = ImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())
