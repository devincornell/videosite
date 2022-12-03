from __future__ import annotations
import pathlib
import tqdm
import videotools
import enum
import dataclasses
import typing
import pathmanager
import sys
        
if __name__ == '__main__':
    
    class PathSelect(enum.Enum):
        ALL = enum.auto()
        ISLA = enum.auto()
        RSC = enum.auto()
        FTV = enum.auto()
        VIXEN = enum.auto()
        MPOV = enum.auto()
        

    #have user enter which option they want to run
    try:
        command_select = sys.argv[1]
    except IndexError as e:
        raise ValueError(f'You must provide an argument to determine which paths to select.')
    print(f'found argument {command_select}')
    select = getattr(PathSelect, command_select.upper())
    
    try:
        force_overwrite = bool(int(sys.argv[2]))
    except: 
        force_overwrite = False
    print(f'{select=}, {force_overwrite=}')
    
    uncompressed_path = '/StorageDrive/purchases/uncompressed'
    compressed_path = '/StorageDrive/purchases/compressed'

    if select == PathSelect.ISLA:
        pmanager = pathmanager.PathManager.from_pathnames(
            in_path = f'{uncompressed_path}/isla_summer_bunkr_large',
            out_path = f'{compressed_path}/isla_summer_bunkr_compressed',
        )
    elif select == PathSelect.RSC:
        pmanager = pathmanager.PathManager.from_pathnames(
            in_path = f'/BackupDrive/purchases/channels/rsc',
            out_path = f'{compressed_path}/rsc_compressed',
        )
    elif select == PathSelect.FTV:
        pmanager = pathmanager.PathManager.from_pathnames(
            in_path = '/BackupDrive/purchases/channels/ftv',
            out_path = f'{compressed_path}/ftv_compressed',
        )
    elif select == PathSelect.VIXEN:
        pmanager = pathmanager.PathManager.from_pathnames(
            in_path = f'{uncompressed_path}/vixen',
            out_path = f'{compressed_path}/vixen_compressed',
        )
    elif select == PathSelect.MPOV:
        pmanager = pathmanager.PathManager.from_pathnames(
            in_path = f'{uncompressed_path}/mpov',
            out_path = f'{compressed_path}/mpov_compressed',
        )
    elif select == PathSelect.ALL:
        pmanager = pathmanager.PathManager.from_pathnames(
            in_path = '/BackupDrive/purchases',
            out_path = f'{compressed_path}/purchases_ALL_compressed',
        )

    
    
    ct = 0
    for rp, ip, op in pmanager.rglob_iter([f'*.mp4', f'*.mov', f'*.wmv'], verbose=True):
        new_path = op.with_suffix('.mp4')
        #print(f'{rp}\n{ip}\n{op}\n{new_path}\n')
        
        if not new_path.is_file():
            #print(f'{rp}\n{ip}\n{op}\n{new_path}\n')
            pass
        
        if not new_path.is_file() or force_overwrite:
            videotools.codec_compress(str(ip), str(new_path))
            pass
            
            
        ct += 1
        
    print(f'finished processing {ct} videos.')