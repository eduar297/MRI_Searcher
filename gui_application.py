import sys
import os

from PyQt5.Qt import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QColor, QPaintDevice

from Model_Vectorial import Vectorial
from Model_Ext_Vectorial import Ext_Vectorial

import directory
from collection import build_cran_documents, build_cisi_documents
import webbrowser as wb

from trie import Trie


class DirectoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.directory = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'collection\\', QFileDialog.ShowDirsOnly)
        
        if not os.listdir(self.directory):
            print('building collection')
            build_cran_documents()
            build_cisi_documents()

    def goToMain(self):
        return MainWindow(self.directory)


class MainWindow(QWidget):
    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.trie = Trie(self.directory)
        self.auto = False
        self.currentQuery = ''

        self.model_type = "Vectorial"
        self.models = {
            "Vectorial": Vectorial(self.directory),
            "Extended Vectorial": Ext_Vectorial(self.directory)
        }
        self.model = self.models[self.model_type]

        self.initUI()
        self.show()
        
    def initUI(self):
        self.setGeometry(0, 0, 900, 700)
        self.setMinimumSize(900, 700)
        self.setMaximumSize(900, 700)
        self.setWindowTitle('Retrieving Information System')


        #Setting the 'Query' label
        self.label1 = QLabel("MRI_SEARCHER", self)
        self.label1.setStyleSheet('color: gray')
        self.label1.move(int(self.width()/2) - 160, 30)
        self.label1.setFont(QFont("Times", 28, QFont.Bold))

        #Setting the query box
        self.qbox = QLineEdit(self)
        self.qbox.setStyleSheet(
                                "border                     : 1px solid gray;"
                                "border-top-right-radius    : 20px; "
                                "border-bottom-right-radius : 20px")

        self.qbox.setPlaceholderText(' Search...')

        self.btn_icon = QPushButton("", self)
        pixmapi = getattr(QStyle, "SP_ArrowForward")
        icon = self.style().standardIcon(pixmapi)

        self.btn_icon.setIcon(icon)
        self.btn_icon.setStyleSheet('border: none')
        self.btn_icon.move(int(self.width()/2 - self.qbox.width()/2) + 360, 120)
        self.btn_icon.clicked.connect(self.search)

        self.qbox.setFont(QFont("Times", 14))
        self.qbox.resize(500, 60)
        self.qbox.move(int(self.width()/2 - self.qbox.width()/2) + 100, 100)
        self.qbox.textChanged.connect(self.autocomplete)
        self.qbox.returnPressed.connect(self.search)

        self.model_btn = QPushButton(self.model_type, self)
        pixmapi = getattr(QStyle, "SP_ArrowDown")
        icon = self.style().standardIcon(pixmapi)
        self.model_btn.setIcon(icon)

        self.model_btn.setStyleSheet(
                                "border                     : 1px solid gray;"
                                "background-color           : white;"
                                "border-top-left-radius     : 20px;"
                                "border-bottom-left-radius  : 20px; ")

        self.model_btn.setFont(QFont("Times", 8))
        self.model_btn.resize(200, 60)
        self.model_btn.move(int(self.width()/2 - self.qbox.width()/2) - 100, 100)
        self.model_btn.clicked.connect(self.change_model)

        #Setting qList
        self.qList = QListWidget(self)
        self.qList.doubleClicked.connect(self.qList_clicked)
        self.qList.setStyleSheet('color: gray;'
                                 "border-top-left-radius     : 20px;"
                                 "border-top-right-radius    : 20px; "
                                 "border-bottom-left-radius  : 20px; "
                                 "border-bottom-right-radius : 20px"
                                 )
        self.qList.setFont(QFont("Comic Sams", 14))
        self.qList.move(15, 240)
        self.qList.resize(self.width() - 30, 400)
        self.qList.hide()
        
        
        #Setting autocomplete
        self.qAuto = QListWidget(self)
        self.qAuto.clicked.connect(self.qAuto_clicked)
        
        self.qAuto.setStyleSheet('color: black;'
                                 "border-top-left-radius     : 20px;"
                                 "border-top-right-radius    : 20px; "
                                 "border-bottom-left-radius  : 20px; "
                                 "border-bottom-right-radius : 20px"
                                 )
        self.qAuto.setFont(QFont("Comic Sams", 14))
        self.qAuto.move(300, 160)
        self.qAuto.resize(500, 400)
        self.qAuto.hide()
        
        
        self.label_location = QLabel(self.directory, self)
        self.label_location.setStyleSheet('color: black')
        self.label_location.move(10, 650)
        self.label_location.setFont(QFont("Times", 10))
        

    def keyPressEvent(self, event):
        if self.auto:
            if event.key() == Qt.Key_Escape:
                self.auto_close()
            if event.key() == Qt.Key_Down:
                self.auto_down()
            if event.key() == Qt.Key_Up:
                self.auto_up()
        
    def auto_close(self):
        self.qAuto.close()
    def auto_down(self):
        index = self.qAuto.currentRow()
        print(index)
    
    def autocomplete(self):
        self.query = self.qbox.text()
        spl = self.query.split(' ')
        if len(spl) > 1:
            self.query = spl[len(spl)-1]

        self.currentQuery = spl[:len(spl)-1]

        self.currentQuery = ' '.join(self.currentQuery)


        if len(self.query) >= 40: self.btn_icon.hide()
        else: self.btn_icon.show()
        
        words = self.trie.enumerate(self.query)
        if words:
            try:
                self.resultLbl.clear()
            except:
                pass
        
            self.auto = True
            self.qAuto.show()
            self.buildAutoList(words)
        else:
            try:
                self.resultLbl.show()
            except:
                pass
            
            self.auto = False
            self.qAuto.clear()
            self.qAuto.close()         
          
    def change_model(self):
        if self.model_type == "Vectorial":
            self.model_type = "Extended Vectorial"
        elif self.model_type == "Extended Vectorial":
            self.model_type = "Vectorial"

        self.model_btn.setText(self.model_type)
        self.model = self.models[self.model_type]

        self.qbox.setText("")
        
        self.auto = False
        self.qAuto.clear()
        self.qAuto.close()
        self.qList.clear()
        self.qList.close()

    def qAuto_clicked(self):
        self.currentQuery += ' ' + str(self.qAuto.currentItem().text())
        self.qbox.setText(self.currentQuery)
        self.qAuto.clear()
        self.qAuto.close()
        
    def qList_clicked(self):
        
        tmp = self.directory.split("/")
        tmp.pop()
        
        _directory = ""
        for t in tmp:
            _directory += t + "/"
            
        _directory += "docs"
        
        current = str(self.qList.currentItem().text())
        path = current.split(' | ')
        
        filename = _directory + "/" + path[1]
        wb.open_new(filename)

    def buildAutoList(self, items):
        self.qAuto.hide()
        self.qAuto.clear()
        for item in items:
            self.qAuto.addItem(item)
        self.qAuto.show()
        
    def buildList(self, items):
        self.qList.hide()
        self.qList.clear()
        s = str(len(items)) + " results has been found"
        try:
            self.resultLbl.clear()
        except:
            pass
        self.resultLbl = QLabel(s, self)
        self.resultLbl.setFont(QFont("Comic Sams", 16))
        self.resultLbl.move(int(self.width()/2) - 150, 180)
        self.resultLbl.show()
        
        tmp = self.directory.split("/")
        tmp.pop()
        
        _directory = ""
        for t in tmp:
            _directory += t + "/"
            
        _directory += "titles"

        for item in items:
            with open(f'{_directory}/{item[1]}', 'r') as f:
                title = str(f.readline())
                self.qList.addItem(str(item[0])[:5] + " | " + item[1] + " | " + title)
        self.qList.show()

    def search(self):
        self.query = self.qbox.text()
        self.auto = False
        self.qAuto.clear()
        self.qAuto.close()
        relevant_docs = self.model.process_query(self.query)
        self.buildList(relevant_docs)

def main():
    app = QApplication(sys.argv)
    d = DirectoryWindow()
    m = d.goToMain()
    d.close()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
        