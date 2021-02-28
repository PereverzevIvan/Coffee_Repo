# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QWidget
from UI.design import Ui_MainWindow
from UI.addEditCoffeeForm import Ui_Form
import sqlite3


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Кофе-брэйк')
        self.error_lab.hide()
        self.btn_add.clicked.connect(self.add_cell)
        self.btn_edit.clicked.connect(self.edit_cell)
        self.btn_show.clicked.connect(self.load_table)
        self.all_titles = None
        self.open_form = None
        self.show_table = False
        self.con = None

    def edit_cell(self):
        if self.show_table:
            self.error_lab.hide()
            select_rows = list(set([i.row() for i in self.table_w.selectedItems()]))
            if select_rows and 0 not in select_rows:
                info = [self.table_w.item(select_rows[0], i).text() for i in range(len(self.all_titles))]
                self.open_form = AddEditCoffeeForm(self, 'edit')
                self.open_form.id.setText(info[0])
                self.open_form.name.setText(info[1])
                self.open_form.roast.setText(info[2])
                self.open_form.ground_coffee.setText(info[3])
                self.open_form.corn_coffee.setText(info[4])
                self.open_form.taste.setText(info[5])
                self.open_form.price.setText(info[6])
                self.open_form.volume.setText(info[7])
                self.open_form.show()
        else:
            self.error_lab.setText('Сначала загрузите таблицу')
            self.error_lab.show()

    def add_cell(self):
        if self.show_table:
            self.error_lab.hide()
            ids = [self.table_w.item(i, 0).text() for i in range(self.table_w.rowCount())]
            self.open_form = AddEditCoffeeForm(self, 'add')
            self.open_form.id.setText(str(int(ids[-1]) + 1))
            self.open_form.show()
        else:
            self.error_lab.setText('Сначала загрузите таблицу')
            self.error_lab.show()

    def load_table(self):
        self.error_lab.hide()
        self.con = sqlite3.connect('data/coffee.sqlite')
        cur = self.con.cursor()
        table_info = cur.execute("SELECT * FROM 'информация_о_кофе'").fetchall()
        self.all_titles = [description[0] for description in cur.description]
        self.table_w.setColumnCount(len(self.all_titles))
        self.table_w.setRowCount(len(table_info) + 1)
        for i, row in enumerate(self.all_titles):
            self.table_w.setItem(0, i, QTableWidgetItem(str(row)))
        for i, row in enumerate(table_info):
            column_set = 0
            for j in row:
                elem = j
                elem = '' if elem is None else elem
                self.table_w.setItem(i + 1, column_set, QTableWidgetItem(str(elem)))
                column_set += 1
        self.show_table = True

    def update_cell(self, changes):
        for i in range(len(self.all_titles[1:])):
            request_1 = f"UPDATE 'информация_о_кофе'\n"
            request_2 = f"SET '{self.all_titles[1:][i].lower()}' = '{changes[1:][i].text()}'\n"
            request_3 = f"WHERE id = '{changes[0].text()}'"
            request = request_1 + request_2 + request_3
            cur = self.con.cursor()
            cur.execute(request)
            self.con.commit()
        self.load_table()

    def insert_cell(self, changes):
        request = f"INSERT INTO 'информация_о_кофе'(id, 'название сорта', 'степень обжарки'," \
                  f" 'молотый', 'в зернах', 'описание вкуса', 'цена', 'объем упаковки')" \
                  f" VALUES('{changes[0].text()}'"
        for i in changes[1:]:
            request += f", '{i.text()}'"
        request += ')'
        cur = self.con.cursor()
        cur.execute(request)
        self.con.commit()
        self.load_table()


class AddEditCoffeeForm(QWidget, Ui_Form):
    def __init__(self, parent, mission):
        super(AddEditCoffeeForm, self).__init__()
        self.setupUi(self)
        self.parent_ = parent
        self.mission = mission
        self.error_lab.hide()
        self.btn_ok.clicked.connect(self.success)
        self.id.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel)
        if mission == 'edit':
            self.setWindowTitle('Редактировние')
        elif mission == 'add':
            self.setWindowTitle('Добавление')
        self.inputs = [self.id, self.name, self.roast, self.ground_coffee, self.corn_coffee,
                       self.taste, self.price, self.volume]

    def success(self):
        self.error_lab.hide()
        empty = all([i.text().replace(' ', '') for i in self.inputs])
        if self.mission == 'edit':
            if empty:
                self.parent_.update_cell(self.inputs)
                self.close()
            else:
                self.error_lab.setText('Вы пропустили поле')
                self.error_lab.show()
        elif self.mission == 'add':
            if empty:
                self.parent_.insert_cell(self.inputs)
                self.close()
            else:
                self.error_lab.setText('Вы пропустили поле')
                self.error_lab.show()

    def cancel(self):
        self.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    wnd = Window()
    wnd.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
