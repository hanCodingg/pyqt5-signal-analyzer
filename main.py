import sys
import os
import subprocess
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QProgressBar, QLineEdit, QPushButton, QLabel, QShortcut, QVBoxLayout
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QKeySequence
from spectrum_analyzer import spectrum_analyzer

# Function to load UI files dynamically
def load_ui_file(ui_file, parent=None):
    if hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        ui_path = os.path.join(sys._MEIPASS, 'ui', ui_file)
    else:
        # Running in a normal Python environment
        ui_path = os.path.join(os.path.dirname(__file__), 'ui', ui_file)
    loadUi(ui_path, parent)

# Splash screen section
class SplashWindows(QWidget):
    def __init__(self):
        super(SplashWindows, self).__init__()
        try:
            load_ui_file("sa_splash.ui", self)
            print("File 'sa_splash.ui' executed.")
        except FileNotFoundError:
            print("Error: File 'sa_splash.ui' not found. Program cannot proceed.")
            sys.exit(1)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.progress_bar = self.findChild(QProgressBar, "progressBar_saLoading")
        if self.progress_bar is None:
            print("Error: Progress bar not found. Program cannot proceed.")
            sys.exit(1)
        print("Progress bar is found.")
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress_bar)
        self.progress_value = 0
        self.timer.start(25)  # Adjust the interval as needed

    def update_progress_bar(self):
        if self.progress_value >= 100:
            self.timer.stop()
            print("Open 'sa_login.ui'")
            self.show_login_screen()
        else:
            self.progress_value += 1
            self.progress_bar.setValue(self.progress_value)

    def show_login_screen(self):
        print("Close 'sa_splash.ui'")
        self.login = LoginWindows()
        self.login.show()
        self.close()

# Login screen section
class LoginWindows(QWidget):
    def __init__(self):
        super(LoginWindows, self).__init__()
        try:
            load_ui_file("sa_login.ui", self)
        except FileNotFoundError:
            print("Error: UI file 'sa_login.ui' not found")
            sys.exit(1)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        print("File 'sa_login.ui' executed.")
        self.setWindowTitle("Spectrum Analyzer Login")
        self.username_edit = self.findChild(QLineEdit, "lineEdit_userName")
        self.password_edit = self.findChild(QLineEdit, "lineEdit_passWord")
        self.login_button = self.findChild(QPushButton, "pushButton_login")
        self.login_text = self.findChild(QLabel, "label_loginText")
        self.login_button.clicked.connect(self.validate_login)
        self.enter_shortcut = QShortcut(QKeySequence("Return"), self)
        self.enter_shortcut.activated.connect(self.login_button.click)

    def validate_login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        if username == "ipp123" and password == "sa123":
            print("Login successful")
            print("Open 'sa_main.ui'")
            self.show_main_screen()
        else:
            print("Invalid credentials")
            self.login_text.setText("Invalid username or password")
            self.login_text.setStyleSheet("color: red")

    def show_main_screen(self):
        print("Close 'sa_login.ui'")
        self.main = MainWindows()
        self.main.show()
        self.close()

# Main screen section
class MainWindows(QWidget):
    def __init__(self):
        super(MainWindows, self).__init__()
        try:
            load_ui_file("sa_main.ui", self)
        except FileNotFoundError:
            print("Error: UI file 'sa_main.ui' not found")
            sys.exit(1)
        print("File 'sa_main.ui' executed.")
        self.setWindowTitle("SignalPro Signal Analyzer")
        self.spectrum_analyzer_widget = self.findChild(QWidget, "widget_spectrumAnalyzer")
        self.frequency_display = self.findChild(QLabel, "label_frequencyText")
        self.frequency_lineinput = self.findChild(QLineEdit, "lineEdit_setFrequency")
        self.frequency_lineinput.returnPressed.connect(self.set_frequency_input)
        self.start_spectrum_analyzer()
        self.frequency_timer = QTimer()
        self.frequency_timer.timeout.connect(self.update_frequency_display)
        self.frequency_timer.start(100)

    def start_spectrum_analyzer(self):
        self.spectrum_analyzer = spectrum_analyzer()
        spectrum_widget = self.spectrum_analyzer
        spectrum_layout = self.spectrum_analyzer_widget.layout()
        if not spectrum_layout:
            spectrum_layout = QVBoxLayout(self.spectrum_analyzer_widget)
        spectrum_layout.addWidget(spectrum_widget)
        self.spectrum_analyzer.start()

    def update_frequency_display(self):
        current_frequency = self.spectrum_analyzer.get_frequency()
        self.frequency_display.setText(f"Frequency: {current_frequency / 1e6:.3f} MHz")

    def set_frequency_input(self):
        frequency_text = self.frequency_lineinput.text()
        try:
            # Convert the input text to a float value (assuming MHz input)
            new_frequency = float(frequency_text) * 1e6  # Convert MHz to Hz

            # Set the new frequency in the GNU Radio flowgraph
            self.spectrum_analyzer.set_frequency(new_frequency)

            # Update the QLabel immediately
            self.frequency_label.setText(f"Frequency: {new_frequency / 1e6:.3f} MHz")

        except ValueError:
            # Handle invalid input (non-numeric values)
            print("Invalid frequency input. Please enter a valid number.")        

    def closeEvent(self, event):
        # Properly stop the GNU Radio flowgraph when closing the window
        self.spectrum_analyzer.stop()
        self.spectrum_analyzer.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    splash = SplashWindows()
    splash.show()

    sys.exit(app.exec_())
