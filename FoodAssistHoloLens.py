import sys
import initializer
import PyQt5.QtCore as qtc

app = qtc.QCoreApplication([])
# created initializer globally
my_initializer = initializer.Initializer()

# run the app
sys.exit(app.exec_())
