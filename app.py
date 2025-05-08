import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QAction, 
                             QToolBar, QVBoxLayout, QWidget, QSizePolicy, QPushButton)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon, QKeySequence, QDragEnterEvent, QDropEvent
from model_vis import model_file_vis as file_vis

SUPPORTED_FILE_EXTS = ['.safetensors']

# Get application path (works for both regular Python and PyInstaller)
def get_application_path():
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        # Otherwise, we're running in a bundle
        return os.path.dirname(sys.executable)
    # Regular Python execution
    return os.path.dirname(os.path.abspath(__file__))

# Get path to resource
def resource_path(relative_path):
    base_path = get_application_path()
    return os.path.join(base_path, relative_path)

class FileViewerWindow(QMainWindow):
    """A window that displays the HTML visualization of a file."""
    
    def __init__(self, filepath=None, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self.init_ui()
        
        if filepath:
            self.load_file(filepath)
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Model Weights Visualizer")
        self.setGeometry(100, 100, 800, 600)
        
        # Set application icon
        icon_path = resource_path("app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Create web engine view for displaying HTML
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.web_view)
        self.setCentralWidget(central_widget)
        
        # Create toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Add reload action
        reload_action = QAction("Reload", self)
        reload_action.setShortcut(QKeySequence.Refresh)
        reload_action.triggered.connect(self.reload_file)
        toolbar.addAction(reload_action)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def load_file(self, filepath):
        """Load and visualize the specified file."""
        self.filepath = filepath
        self.setWindowTitle(f"Model Weights Visualizer - {os.path.basename(filepath)}")
        
        try:
            # Call the file_vis function to get HTML
            html_content = file_vis(filepath)
            
            # Display the HTML
            self.web_view.setHtml(html_content, baseUrl=QUrl.fromLocalFile(os.path.dirname(filepath) + os.sep))
            
        except Exception as e:
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .error {{ color: red; }}
                </style>
            </head>
            <body>
                <h1>Error Loading File</h1>
                <p class="error">Error: {str(e)}</p>
            </body>
            </html>
            """
            self.web_view.setHtml(error_html)
    
    def reload_file(self):
        """Reload the current file."""
        if self.filepath:
            self.load_file(self.filepath)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events for files."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].isLocalFile():
                filepath = urls[0].toLocalFile()
                # Check if the file has a supported extension
                if any(filepath.lower().endswith(ext) for ext in SUPPORTED_FILE_EXTS):
                    event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events for files."""
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            filepath = urls[0].toLocalFile()
            # Check if the file has a supported extension
            if any(filepath.lower().endswith(ext) for ext in SUPPORTED_FILE_EXTS):
                # Get the main window to handle the file opening
                main_app = QApplication.instance().topLevelWidgets()[0]
                if hasattr(main_app, 'create_viewer_window'):
                    main_app.create_viewer_window(filepath)
                else:
                    # Fallback if main window reference not found
                    viewer = FileViewerWindow(filepath)
                    viewer.show()


class FileVisualizerApp(QMainWindow):
    """Main application window with menu for file operations."""
    
    def __init__(self):
        super().__init__()
        self.viewer_windows = []  # Keep track of all open viewer windows
        self.init_ui()
    
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Model Weights Visualizer")
        self.setGeometry(100, 100, 400, 200)
        
        # Set application icon
        icon_path = resource_path("app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Create menu bar
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # Open action
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Set central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Add Open File button
        open_file_button = QPushButton("Open File", self)
        open_file_button.setFixedSize(200, 50)
        open_file_button.clicked.connect(self.open_file)
        layout.addWidget(open_file_button, 0, Qt.AlignCenter)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def open_file(self):
        """Open file dialog and create a new viewer window for the selected file."""
        # Create file filter string based on supported extensions
        filter_string = "Supported Files ("
        for ext in SUPPORTED_FILE_EXTS:
            filter_string += f"*{ext} "
        filter_string = filter_string.strip() + ")"
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", f"{filter_string};;All Files (*)")
        
        if filepath:
            # Verify the file has a supported extension
            if any(filepath.lower().endswith(ext) for ext in SUPPORTED_FILE_EXTS):
                self.create_viewer_window(filepath)
    
    def create_viewer_window(self, filepath):
        """Create a new viewer window for the specified file."""
        viewer = FileViewerWindow(filepath)
        viewer.show()
        
        # Keep a reference to prevent garbage collection
        self.viewer_windows.append(viewer)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events for files."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].isLocalFile():
                filepath = urls[0].toLocalFile()
                # Check if the file has a supported extension
                if any(filepath.lower().endswith(ext) for ext in SUPPORTED_FILE_EXTS):
                    event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events for files."""
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            filepath = urls[0].toLocalFile()
            # Check if the file has a supported extension
            if any(filepath.lower().endswith(ext) for ext in SUPPORTED_FILE_EXTS):
                self.create_viewer_window(filepath)


def main():
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("Model Weights Visualizer")
    
    # Create and show the main window
    main_window = FileVisualizerApp()
    main_window.show()
    
    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()