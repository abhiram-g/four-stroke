import os

def search_file(filename, dirname):
    for root, dirs, files in os.walk(dirname):
        for file in files:
            if file == filename:
                filepath = os.path.join(root, file)
                return filepath

    return False
                