import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import codecs
import pandas as pd
import numpy as np

import voctrain as vt


class Window(QtWidgets.QWidget):
    fname = 'words.xlsx'
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setFixedSize(560, 550)
        self.setWindowTitle("Train vocabulary")

        # Loading vocabulary trainer class and making it ready
        self.vocab = vt.VocabularyTrainer(self.fname)
        
        self.f_out = QtWidgets.QTextBrowser(self)
        self.f_out.setGeometry(30, 30, 500, 200)
        self.f_out.setStyleSheet("""border: 1px solid; font: Arial; font-size: 16px;""")
        self.f_out.setText("In this field a definition of word will appear")

        self.f_in = QtWidgets.QTextEdit(self)
        self.f_in.setGeometry(30, 260, 500, 100)
        self.f_in.setStyleSheet("""border: 1px solid; font: Arial; font-size: 16px;""")
        self.f_in.setText("In this field you should type your answer")

        # Start button
        self.b_start = QtWidgets.QPushButton(self)
        self.b_start.setGeometry(160, 390, 240, 60)
        self.b_start.setStyleSheet("""background-color: rgb(170, 170, 170); font: bold Arial; font-size: 18px;""")
        self.b_start.setText("Start training!")
        self.b_start.clicked.connect(self.start_training)

        # Answer button
        self.b_answer = QtWidgets.QPushButton(self)
        self.b_answer.setGeometry(210, 390, 320, 60)
        self.b_answer.setStyleSheet("""background-color: rgb(100, 170, 100); font: bold Arial; font-size: 18px;""")
        self.b_answer.setText("answer")
        self.b_answer.clicked.connect(self.event_answer)
        self.b_answer.hide()

        # Stop button
        self.b_stop = QtWidgets.QPushButton(self)
        self.b_stop.setGeometry(30, 390, 150, 60)
        self.b_stop.setStyleSheet("""background-color: rgb(180, 60, 60); font: bold Arial; font-size: 18px;""")
        self.b_stop.setText("save and \nexit")
        self.b_stop.clicked.connect(self.event_stop)
        self.b_stop.hide()

        # Next button
        self.b_next = QtWidgets.QPushButton(self)
        self.b_next.setGeometry(210, 390, 320, 60)
        self.b_next.setStyleSheet("""background-color: rgb(100, 100, 100); font: bold Arial; font-size: 18px;""")
        self.b_next.setText("next word")
        self.b_next.clicked.connect(self.event_next)
        self.b_next.hide()

        self.stats = QtWidgets.QLabel(self)
        self.stats.setGeometry(-2, 530, 564, 22)
        self.stats.setAlignment(QtCore.Qt.AlignRight)
        self.stats.setStyleSheet("""border: 2px solid rgb(150, 150, 150); font: Arial; font-size: 16px;""")
        self.stats.setText("This session stats: 0✔ 0✘")

        # Connection of Input field receiving  'Ctrl+Enter' to function 
        shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Return"), self.f_in)
        shortcut.activated.connect(self.ctrl_enter_pressed)

        # self.finp_path = QtWidgets.QFileDialog(self)
        # self.finp_path.setGeometry(10, 10, 500, 30)
        # self.finp_path.show()


        self.show()


    def start_training(self):
        self.b_start.hide()

        self.f_out.setText('• '+self.vocab.get_definition())
        self.f_in.setText("")
        
        self.b_answer.show()
        self.b_stop.show()


    def event_answer(self):
        user_answer = self.f_in.toPlainText()
        self.f_out.append(self.vocab.check_answer(user_answer))

        self.stats.setText("This session stats: %d✔ %d✘"%(self.vocab.n_correct, self.vocab.n_incorrect))

        self.b_answer.hide()
        self.b_next.show()


    def event_stop(self):
        self.vocab.save_data(self.fname)
        self.close()


    def event_next(self):
        self.f_out.append("")
        self.f_out.append('• '+self.vocab.get_definition())
        self.f_in.setText("")

        self.b_answer.show()
        self.b_next.hide()

    def ctrl_enter_pressed(self):
        if self.b_answer.isVisible():
            self.event_answer()
        elif self.b_next.isVisible():
            self.event_next()
        else:
            print("Nothing is active yet!")


app = QtWidgets.QApplication(sys.argv)
app.aboutToQuit.connect(app.deleteLater)
a_window = Window()
app.exec_()
    