from MainController import MainController

import sys

# class Application(QCoreApplication):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     def start(self):
#         self.scanner = SensorScanner()
#         self.scanner.scan()
#         self.exec()


if __name__ == '__main__':
  mainController = MainController()
  sys.exit(mainController.run())
