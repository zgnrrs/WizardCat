import signal
import sys
from PySide6.QtWidgets import QApplication

from wizard_cat.ui import WizardCat


def main():
    # Enable clean Ctrl+C termination without traceback logs
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    window = WizardCat()
    window.show()
    window.setFocus()

    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()