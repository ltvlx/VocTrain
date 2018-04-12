import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import voctrain as vt
import plotwindow as pw


class Window(QtWidgets.QWidget):
    fname = ''
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # basic geometry parameters of window and widgets
        margin = 25
        main_w, main_h = 560, 550
        btn_h = 60
        out_h = 200
        in_h = 100
        bar_h = 25

        # other parameters that are automatically calculated from basic ones
        in_w = out_w = main_w - 2 * margin
        in_y = margin * 2 + out_h
        btn_y =  in_y + in_h + margin
        btn_s_w = 0.4 * main_w
        btn_s_x = 0.3 * main_w
        btn_1_w = (main_w - margin * 3) * 0.4
        btn_2_w = (main_w - margin * 3) * 0.6
        btn_1_x = margin
        btn_2_x = btn_1_x + btn_1_w + margin


        self.setFixedSize(main_w, main_h)
        self.setWindowTitle("Train vocabulary")
        
        self.f_out = QtWidgets.QTextBrowser(self)
        self.f_out.setGeometry(margin, margin, out_w, out_h)
        self.f_out.setStyleSheet("""border: 1px solid; font: Arial; font-size: 16px;""")

        self.f_in = QtWidgets.QTextEdit(self)
        self.f_in.setGeometry(margin, in_y, in_w, in_h)
        self.f_in.setStyleSheet("""border: 1px solid; font: Arial; font-size: 16px;""")

        self.b_start = QtWidgets.QPushButton(self)
        self.b_start.setGeometry(btn_s_x, btn_y, btn_s_w, btn_h)
        self.b_start.setStyleSheet("""background-color: rgb(170, 170, 170); font: bold Arial; font-size: 18px;""")
        self.b_start.setText("Select vocabulary \nand start training")
        self.b_start.clicked.connect(self.start_training)

        # Stop button
        self.b_stop = QtWidgets.QPushButton(self)
        self.b_stop.setGeometry(btn_1_x, btn_y, btn_1_w, btn_h)
        self.b_stop.setStyleSheet("""background-color: rgb(180, 60, 60); font: bold Arial; font-size: 18px;""")
        self.b_stop.setText("save and \nexit")
        self.b_stop.clicked.connect(self.event_stop)
        self.b_stop.hide()

        # Answer button
        self.b_answer = QtWidgets.QPushButton(self)
        self.b_answer.setGeometry(btn_2_x, btn_y, btn_2_w, btn_h)
        self.b_answer.setStyleSheet("""background-color: rgb(100, 170, 100); font: bold Arial; font-size: 18px;""")
        self.b_answer.setText("answer")
        self.b_answer.clicked.connect(self.event_answer)
        self.b_answer.hide()

        # Next button
        self.b_next = QtWidgets.QPushButton(self)
        self.b_next.setGeometry(btn_2_x, btn_y, btn_2_w, btn_h)
        self.b_next.setStyleSheet("""background-color: rgb(100, 100, 100); font: bold Arial; font-size: 18px;""")
        self.b_next.setText("next word")
        self.b_next.clicked.connect(self.event_next)
        self.b_next.hide()

        # Stats panel
        self.stats = QtWidgets.QLabel(self)
        self.stats.setGeometry(-2, main_h - bar_h, main_w + 4, bar_h + 2)
        self.stats.setAlignment(QtCore.Qt.AlignRight)
        self.stats.setStyleSheet("""border: 2px solid rgb(150, 150, 150); font: Arial; font-size: 16px;""")
        self.stats.hide()

        # Connection of Input field receiving  'Ctrl+Enter' to function
        shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Return"), self.f_in)
        shortcut.activated.connect(self.ctrl_enter_pressed)

        # Stats button
        self.b_stats = QtWidgets.QPushButton(self)
        self.b_stats.setGeometry(-2, main_h - bar_h, 100, bar_h + 2)
        self.b_stats.setStyleSheet("""border: 2px solid rgb(150, 150, 150); background-color: rgb(240, 240, 240); font: Arial; font-size: 16px;""")
        self.b_stats.setText("show stats")
        self.b_stats.hide()
        
        self.b_stats.clicked.connect(self.show_stats_plot)

        self.show()


    def start_training(self):
        self.fname = self.select_xlsx()
        
        k_train = self.select_mode()
        
        self.vocab = vt.VocabularyTrainer(self.fname, k_train)
        
        self.stats.setText(self.vocab.get_status())

        self.b_start.hide()

        self.f_out.append(' • '+self.vocab.get_definition())
        self.f_in.setText("")
        
        self.b_answer.show()
        self.b_stop.show()
        self.b_stats.show()
        self.stats.show()


    def select_xlsx(self):
        fname =  QtWidgets.QFileDialog.getOpenFileName(directory='./', filter='Vocabulary in excel table (*.xlsx *.xls)')[0]
        if fname == '':
            print("No file selected! Program exit!")
            sys.exit()
        return fname


    def select_mode(self):
        modes = ['All words', 'Bad words', ]
        descriptions = ['In this mode you need to translate all words from your vocabulary provided to you in random order.',
                        'In this mode you will get random words from your vocabulary. Less known words will be given more often.']
        
        self.dialog = QtWidgets.QInputDialog(self)
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.dialog.move((resolution.width() / 2) - (self.dialog.width() / 2),(resolution.height() / 2) - (self.dialog.height() / 2))
        self.dialog.setStyleSheet("""background-color: rgb(240, 240, 240); font: Arial; font-size: 16px;""")
        selected_mode = self.dialog.getItem(self.dialog, "Mode selector", "Select training program     ", modes, 0, False)[0]
        i = modes.index(selected_mode)
        self.f_out.append("'%s' training mode selected."%modes[i])
        self.f_out.append(descriptions[i] + "\n")
        return i


    def event_answer(self):
        user_answer = self.f_in.toPlainText()
        self.f_out.append(self.vocab.set_answer(user_answer))

        self.stats.setText(self.vocab.get_status())

        self.b_answer.hide()
        self.b_next.show()


    def event_stop(self):
        self.vocab.save_data(self.fname)
        try:
            del self.stats_plot
        except:
            pass
        self.close()


    def event_next(self):
        self.f_out.append("")
        self.f_out.append('• '+self.vocab.get_definition())
        self.f_in.setText("")

        self.b_answer.show()
        self.b_next.hide()


    def show_stats_plot(self):
        self.stats_plot = pw.PlotWindow()

        self.stats_plot.plot(self.vocab.l_cor, self.vocab.l_inc)
        self.stats_plot.show()


    def ctrl_enter_pressed(self):
        if self.b_answer.isVisible():
            self.event_answer()
        elif self.b_next.isVisible():
            self.event_next()
        else:
            self.start_training()




app = QtWidgets.QApplication(sys.argv)
app.aboutToQuit.connect(app.deleteLater)
a_window = Window()
app.exec_()
    