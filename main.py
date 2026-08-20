import sys
from PySide6.QtWidgets import QApplication

from wizard_cat.ui import WizardCat


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    window = WizardCat()
    window.show()
    window.setFocus()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()