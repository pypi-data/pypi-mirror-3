"""
Grape Runner
"""
import glob
import os


class Runner(object):
    def __init__(self):
        self.running = False

    def start(self):
        self.running = True
        buildout_dir = os.path.abspath(os.path.curdir)
        scripts = [os.path.split(s) for s in glob.glob('parts/*/*.sh')]
        folders = [s for s in glob.glob('parts/*')]
        scripts.sort()
        folders.sort()
        runs = []
        print folders
        print scripts
        for folder in folders:
            if not (folder, 'start.sh') in scripts:
                continue
            if not (folder, 'execute.sh') in scripts:
                continue
            part_dir = os.path.join(buildout_dir, folder)            
            os.chdir(part_dir)
            os.system('./start.sh')
            os.system('./execute.sh')
            print part_dir

    def stop(self):
        self.running = False
