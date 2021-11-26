from PyQt5 import QtWidgets, QtCore, QtGui, uic
import sys


#import images resource python file
import images_rc

#main class for the ui
class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() #call inherited classes __init__
        uic.loadUi('main.ui', self) #load ui file
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setWindowTitle("GUI To-Do List")

        #Run all sub functions for organisation
        self.showtime()
        self.fontsetup()
        self.uisetup()
        self.timefunc()
        self.systemtraysetup()

        self.oldPos = self.pos() #for mousemoveevent to titlebar
        self.stackedWidget.setCurrentIndex(0) #sets the current index page to the first page, which is the main page
        self.list = []
        self.textlist = []

        #basic move event function that subtracts the difference from new pos and old pos and then moves it by that amount
        def moveEvent(event):
            point = QtCore.QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + point.x(), self.y() + point.y())
            self.oldPos = event.globalPos()

        #sets the mousemoveevent method of the titlebar to the moveevent function
        self.title_bar.mouseMoveEvent = moveEvent

        #save file is opened for the todolist checkboxes and then added all back before the ui is shown
        with open('save.txt') as text_file:
            text_file = text_file.readlines()
            if text_file:
                for line in text_file:
                    line = line.strip()
                    checkbox(line, self.formLayout, self.list, self.textlist)

        #setting options are loaded back in
        with open('checkbox.txt') as text_file:
            text_file = text_file.readlines()
            if text_file:
                for index, line in enumerate(text_file):
                    if index == 0:
                        self.checkBox_exitTray.setChecked(eval(line))
                    if index == 1:
                        self.checkBox_onTop.setChecked(eval(line))

        #setting functions ran once at the start
        self.systemmanage('placeholderreason')
        self.onTop()

        self.show() #show ui

    def fontsetup(self):
        #sets up font scaling so different resolutions wont make the labels cut, applies to all text in the app
        fontId = QtGui.QFontDatabase.addApplicationFont("fonts/LEMON MILK.otf")
        families = QtGui.QFontDatabase.applicationFontFamilies(fontId)

        lemonfont = QtGui.QFont()
        lemonfont.setFamily(families[0])
        lemonfont.setPixelSize(60)
        self.label_time.setFont(lemonfont)
        lemonfont.setPixelSize(24)
        self.label_date_3.setFont(lemonfont)
        lemonfont.setPixelSize(15)
        self.label_credits.setFont(lemonfont)
        lemonfont.setPixelSize(35)
        self.label_settings.setFont(lemonfont)

        segoefont = QtGui.QFont()
        segoefont.setFamily("Segoe UI")
        segoefont.setPixelSize(12)
        segoefont.setBold(True)
        self.deletetask.setFont(segoefont)
        self.newtask.setFont(segoefont)
        self.settings.setFont(segoefont)
        self.btn_backmenu.setFont(segoefont)
        self.checkBox_exitTray.setFont(segoefont)
        self.checkBox_onTop.setFont(segoefont)

    def uisetup(self):
        #sets up most functions of the UI

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint) #removes default border
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground) #makes the designing background transparent


        #links each button to a function
        self.btn_minimize.clicked.connect(lambda: self.showMinimized())
        self.btn_close.clicked.connect(lambda: self.close())
        self.btn_backmenu.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.btn_forcequit.clicked.connect(lambda: self.exitWindow())
        self.newtask.clicked.connect(lambda: self.addtask())
        self.deletetask.clicked.connect(lambda: self.resetall())
        self.settings.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.checkBox_onTop.stateChanged.connect(self.onTop)

        #sets tooltips for buttons
        self.btn_minimize.setToolTip("Minimize Window")
        self.btn_close.setToolTip("Close Window")
        self.btn_forcequit.setToolTip("Forcibly Quit Window")
        self.btn_backmenu.setToolTip("Main Menu")
        self.settings.setToolTip("Settings")
        self.newtask.setToolTip("Create New Task")
        self.deletetask.setToolTip("Reset All Tasks")

        #Links the Enter key to the NewTask Button as a shortcut for users
        self.newtask.setShortcut("Return")

        self.textEdit.installEventFilter(self) #Overrides the enter key for the textedit
        self.textEdit.setPlaceholderText("Type Task Here...")

        self.sizegrip = QtWidgets.QSizeGrip(self.frame_grip) #Creates a size grip as the borders were removed in the second line of UISetup
        self.sizegrip.setStyleSheet("QSizeGrip { width: 10px; height: 10px; border-radius: 10px; } QSizeGrip:hover { background-color: rgb(43, 43, 43) }") #Set the stylesheet for appearance
        self.sizegrip.setToolTip("Resize Window") #Tooltip

    #function that dictates windowsflags for Always On Top checkbox
    def onTop(self):
        #if checkbox is checked, add WindowStaysOnTopHint flag, else remove it
        #when flags are changed, window hides, so the window is shown again
        if self.checkBox_onTop.isChecked():
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            self.show()
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
            self.show()

    #systemtrayicon setup
    def systemtraysetup(self):
        #Creates a tray icon
        self.tray_icon = QtWidgets.QSystemTrayIcon()
        self.tray_icon.setIcon(QtGui.QIcon('icon.ico'))
        self.tray_icon.hide()

        def triggershow():
            self.tray_icon.hide()
            self.show()

        #Defines actions and connects actions to functions
        self.show_action = QtWidgets.QAction("Show", self)
        self.quit_action = QtWidgets.QAction("Exit", self)
        self.show_action.triggered.connect(lambda: triggershow())
        self.quit_action.triggered.connect(self.exitWindow)
        self.tray_icon.activated.connect(self.systemmanage)

        #Creates a menu and adds all the actions to it
        self.tray_menu = QtWidgets.QMenu()
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.quit_action)
        self.tray_icon.setContextMenu(self.tray_menu)

    #Checks if the systemicon is clicked
    def systemmanage(self, reason):
        if self.checkBox_exitTray.isChecked():
            if reason == QtWidgets.QSystemTrayIcon.Trigger:
                self.tray_icon.hide()
                self.show()

    #All ways to close end up at this function, except for force shutdown by an external factor (such as Task Manager on Windows)
    def exitWindow(self):
        #Saves todolist
        with open('save.txt', 'a') as txt:
            txt.truncate(0)
            for line in self.textlist:
                txt.write(line + "\n")

        #Saves settings
        with open('checkbox.txt', 'a') as txt:
            txt.truncate(0)
            txt.write(str(self.checkBox_exitTray.isChecked()) + "\n")
            txt.write(str(self.checkBox_onTop.isChecked()) + "\n")

        #Quits the application
        app.quit()


    #detects every mouse press event and sets the old position to the place where the event occured
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    #Time function
    def timefunc(self):
        timer = QtCore.QTimer(self) #creates new timer
        timer.timeout.connect(self.showtime) # connects the timer to the showtime function
        timer.start(1000) #updates timer every second (1000 milliseconds)

    def showtime(self):
        current_time = QtCore.QTime.currentTime() #reads system clock
        current_date = QtCore.QDate.currentDate() #reads date

        lbltime = current_time.toString("h:mmap") #converts QTime object into a string, hh to hours, mm to minutes and ap converts to 12 hour time w/ AM or PM
        lbldate = current_date.toString("MMMM d, yyyy") #converst QDate object into MMMM (month in full name), d (day), yyyy (full year)

        #sets respective text to labels, updated per second
        self.label_time.setText(lbltime)
        self.label_date_3.setText(lbldate)

    def addtask(self):
        if self.textEdit.toPlainText(): #if textedit has text in it, creates a checkbox using the checkbox class and then clears the textedit
            checkbox(self.textEdit.toPlainText(), self.formLayout, self.list, self.textlist)
            self.textEdit.clear()

    def resetall(self):
        for widget in self.frame_actuallist.children(): #loops throguh every widget in the main checkbox frame
            if isinstance(widget, QtWidgets.QCheckBox): #if is a checkbox, destroy it
                widget.setParent(None)
        self.list.clear() #clears the list keeping track
        self.textlist.clear()

    #eventfilter which overrides the enter keypress for the textedit object
    def eventFilter(self, obj, event):
        if obj is self.textEdit and event.type() == QtCore.QEvent.KeyPress: #detects if the object creating the event is a textEdit and if the event is a keypress
            if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter): #if key is return or enter (numpad enter)
                self.addtask() #addtask function
                return True #returns True to stop any other functions from happening
        return super().eventFilter(obj, event) #else, use the default eventFilter from the inherited class

    #Overrides the default closeEvent
    def closeEvent(self, event):
        if self.checkBox_exitTray.isChecked(): #if the setting is checked, when user tries to close, event is ignored and then hidden
            self.tray_icon.show()
            event.ignore()
            self.hide()
        else:
            self.exitWindow() #if the setting is not checked, redirect to exitWindow function


#Main checkbox class to manage checkboxes
class checkbox():
    def __init__(self, text, layout, list, textlist):
        self.list = list
        self.text = text
        self.layout = layout
        self.checkbox = QtWidgets.QCheckBox()
        self.textlist = textlist

        #Sets up checkbox
        checkboxfont = QtGui.QFont()
        checkboxfont.setFamily("Segoe UI")
        checkboxfont.setPixelSize(12)
        checkboxfont.setBold(True)
        self.checkbox.setFont(checkboxfont)
        self.checkbox.setText(text)
        self.checkbox.setStyleSheet("color: rgb(255, 255, 255);")

        #if the checkbox is checked, destroy the checkbox and remove it from the list
        def func():
            if self.checkbox.isChecked():
                self.checkbox.setParent(None)
                self.list.remove(self.checkbox)
                self.textlist.remove(self.text)


        self.checkbox.stateChanged.connect(func) #links each state change of every checkbox to a function

        #append the checkbox to the tracking list and add the checkbox to the frame layout
        self.list.append(self.checkbox)
        self.textlist.append(self.text)
        self.layout.addRow(self.checkbox)

        print(self.textlist)
        print()




#Runs application
if __name__ == "__main__":
    #Attributes that contribute to supporting several resolutions
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv) #Passes system arguments to the application
    window = Ui() #Creates instance of the class as the main window
    app.exec() #Executes the app
