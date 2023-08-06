import djangopipstarter
import os

def list_template_files():
    """lists all template files"""

    file_list = []

    for root, subfolder, files in os.walk(get_template_path()):
        for f in files:
            filename = os.path.relpath(os.path.join(root, f),
                             get_template_path())
            if not filename.endswith(".pyc"):
                file_list.append(filename)

    return file_list

def get_template_path():
    return os.path.join(djangopipstarter.__path__[0], 'template')
