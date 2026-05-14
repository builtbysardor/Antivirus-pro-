import sys
from PyQt5 import QtWidgets, QtGui, QtCore

def capture_screen():
    app = QtWidgets.QApplication(sys.argv)
    screen = QtWidgets.QApplication.primaryScreen()
    screenshot = screen.grabWindow(0) # Grab entire desktop (0)
    
    # Create screenshots directory
    import os
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')
        
    screenshot.save('screenshots/real_dashboard.png', 'png')
    print("Screenshot saved to screenshots/real_dashboard.png")
    app.quit()

if __name__ == "__main__":
    capture_screen()
