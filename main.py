import sys
import subprocess
import importlib.util
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication

# Custom imports
import global_vars
from gui.pyqt6_gui import Yolo8AnnotationTool

# List of required packages with version specifications
required_packages = {
    'numpy': '1.26.4',
    'Pillow': '9.4.0',
    'PyQt6': '6.7.1'
}
python_version = "3.9"  # Python version for running code


def check_python_version(version):
    """Check if a specific version of Python is installed."""
    try:
        # Run the command to check the Python version
        result = subprocess.run(
            [sys.executable, '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        installed_version = result.stdout.strip().split()[1]
        if installed_version.startswith(version):
            print(f"Python {version} is installed.")
            print(f"Version info: {installed_version}")
        else:
            print(f"Expected Python {version}, but found {installed_version}.")
            print(f"Please install Python {version} from the official Python website.")
    except subprocess.CalledProcessError as e:
        print(f"Error checking Python version: {e}")
        print(f"Please install Python {version} from the official Python website.")
    except FileNotFoundError:
        print(f"Python is not installed.")
        print(f"Please install Python {version} from the official Python website.")


def install_package(package_name, version):
    """Install a package using pip with a specified version."""
    package_with_version = f"{package_name}=={version}"
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_with_version])
    except subprocess.CalledProcessError as e:
        print(f"Error installing package {package_with_version}: {e}")
        sys.exit(1)


def is_package_installed(package_name):
    """Check if a package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False


def validate_packages():
    """Ensure all required packages are installed."""
    for package_name, version in required_packages.items():
        if is_package_installed(package_name):
            print(f"{package_name} is already installed.")
        else:
            print(f"{package_name} is not installed. Installing version {version}...")
            install_package(package_name, version)


def main():

    QCoreApplication.setApplicationName("YOLO8 ANNOTATION TOOL")
    app = QApplication(sys.argv)
    window = Yolo8AnnotationTool()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    validate_packages()
    check_python_version(python_version)
    main()
