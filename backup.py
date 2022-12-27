

from __future__ import annotations
import pathlib
import tqdm
import videotools
import enum
import dataclasses
import typing
import copypathmanager
import sys
import glob
import datetime


if __name__ == '__main__':
    datestr = datetime.datetime.now().strftime('+%Y.%m.%d-%H.%M.%S')
    
    cpm = copypathmanager.CopyPathManager.from_pathnames(
        in_path = '/DataDrive/code/polarization-twitter',
        out_path = f'/tmp/polarization-twitter',
    )
    
    f'/BackupDrive/project_backups/polarization-twitter/polarization-twitter_{datestr}/',
    
    
