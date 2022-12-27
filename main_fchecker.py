

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
        
if __name__ == '__main__':
    patterns = [f'*.mp4', f'*.mov', f'*.wmv']
    ps1 = copypathmanager.CopyPathManager.from_pathnames(
        in_path = '/StorageDrive/purchases',
        out_path = f'/tmp/purchases',
        patterns = patterns,
    )

    ps2 = copypathmanager.CopyPathManager.from_pathnames(
        in_path = '/BackupDrive/purchases',
        out_path = f'/tmp/purchases',
        patterns = patterns,
    )
    
    #ps3 = pathmanager.CopyPathManager.from_pathnames(
    #    in_path = '/StorageDrive/purchases/compressed/isla_summer_bunkr_compressed',
    #    out_path = f'/tmp/isla',
    #    patterns = patterns,
    #)

    
    ps1_fpaths = {pe.rel_path for pe in ps1.rglob_iter()}
    ps2_fpaths = {pe.rel_path for pe in ps2.rglob_iter()}
    #ps3_fpaths = {pe.rel_path for pe in ps3.rglob_iter()}
    
    print(f'{ps1.in_path=}, {len(ps1_fpaths)=}')
    print(f'{ps2.in_path=}, {len(ps2_fpaths)=}')
    #print(f'{ps3.in_path=}, {len(ps3_fpaths)=}')
    
    print(f'{len(ps1_fpaths&ps2_fpaths)=}')
    #print(f'{len(ps1_fpaths&ps3_fpaths)=}')
    #print(f'{len(ps2_fpaths&ps3_fpaths)=}')

    exit()
    for pe in ps1.rglob_iter():
        print(f'{pe.rel_path=}')
        print(f'{pe.in_path=}')
        print(f'{pe.out_path=}')
        print()
    