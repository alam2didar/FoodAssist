import sys
import initializer
# import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw

app = qtw.QApplication([])
# created initializer globally
my_initializer = initializer.Initializer()

# run the app
sys.exit(app.exec_())
