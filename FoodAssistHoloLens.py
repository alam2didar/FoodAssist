import sys
import initializer
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw

def main():
  # initiate app
  app = qtw.QApplication([])
  # created initializer globally
  my_initializer = initializer.Initializer()

  # run the app
  sys.exit(app.exec_())
if __name__ == '__main__':
  main()
