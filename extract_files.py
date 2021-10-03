import os, zipfile, shutil
from pathlib import Path
from zipfile import ZipFile


def extract(zipname, file_names, copy_from_downloads = False):
    if copy_from_downloads:
        # Copy zip file from Dowloads to archive folder
        downloads_path = str(Path.home() / "Downloads")
        shutil.move(downloads_path+'\\'+zipname, 'archive')
    
    # Extract the needed files from the archive folder to data folder
    print('archive/'+zipname)
    with ZipFile('archive/'+zipname) as zip_file:
        zip_file.extract(file_names[0], 'data')
        zip_file.extract(file_names[1], 'data')
