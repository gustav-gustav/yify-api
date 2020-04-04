from zipfile import ZipFile
import os, argparse

def unzip(zip_file=None):
    '''
    Takes an argument (.zip file) from cmd line as required from argparse or,
    if imported, takes a path-like string of the .zip file.
    Unzips using python stdlib zipfile.ZipFile
    '''
    if not zip_file:
        parser = argparse.ArgumentParser()
        parser.add_argument("zip", action="store")
        args = parser.parse_args()
        zip_file = args.zip
    else:
        pass

    os.chdir(os.getcwd())
    if os.path.splitext(zip_file)[-1] == '.zip':
        with ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(os.getcwd())
        os.remove(zip_file)
    else:
        print('.zip extension file required')

if __name__ == "___main__":
    unzip()
