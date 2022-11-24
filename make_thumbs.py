

import glob
import pathlib
import ffmpeg
import sys
import os

if __name__ == '__main__':
    source_path = pathlib.Path('/BackupDrive/purchases/tmp/')
    target_path = pathlib.Path('/BackupDrive/purchases/tmp/web/')
    
    #target_path.mkdir(parents=True, exist_ok=True)
    
    vpaths = list(source_path.rglob('*.mp4', ))
    #print(glob.glob(str(source_path) + '/*.mp4'), str(source_path) + '/*.mp4')
    
    folders = dict()
    for vpath in vpaths:
        relpath = vpath.relative_to(source_path)
        folders
        thumb_path = target_path.joinpath(relpath.stem).with_suffix('.gif')
        
        folders.setdefault(thumb_path.parent, list())
        folders[thumb_path.parent].append()
        folders.add()


        thumb_path.mkdir(parents=True, exist_ok=True)
        print(vpath, relpath, thumb_path)
    

