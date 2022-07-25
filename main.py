from MainController import MainController
import argparse
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
  parser = argparse.ArgumentParser()
  parser.add_argument('--ttl', type=str, choices=('True','False'))
  parser.add_argument('--ECG', type=str, choices=('True', 'False'))
  args = parser.parse_args()
  mainController = MainController(args.ttl == "True", args.ECG == "True")
  sys.exit(mainController.run())
