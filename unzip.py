import subprocess, sys, os, argparse

def unzip(zip=None):
    if not zip:
        parser = argparse.ArgumentParser()
        parser.add_argument("zip", action="store")
        args = parser.parse_args()
        zipfile = args.zip
    else:
        zipfile=zip

    os.chdir(os.getcwd())
    if os.path.splitext(zipfile)[-1] == '.zip':
        subprocess.call(f"unzip {zipfile}", shell=True)
        os.remove(zipfile)
    else:
        print('.zip extension file required')

if __name__ == "___main__":
    unzip()
