from __future__ import annotations
import pathlib
import tqdm
import videotools
import enum
import dataclasses
import typing
import pathmanager

        
if __name__ == '__main__':
    
    class PathSelect(enum.Enum):
        ISLA = enum.auto()
        RSC = enum.auto()
        FTV = enum.auto()

    select = PathSelect.FTV
    
    if select == PathSelect.ISLA:
        pmanager = pathmanager.PathManager.from_pathnames(
            in_path = '/DataDrive/purchases/isla_summer',
            out_path = '/StorageDrive/purchases/isla_summer_small',
        )
    elif select == PathSelect.RSC:
        pmanager = pathmanager.PathManager.from_pathnames(
            in_path = '/BackupDrive/purchases/channels/rsc',
            out_path = '/DataDrive/purchases/rsc_small',
        )
    elif select == PathSelect.FTV:
        pmanager = pathmanager.PathManager.from_pathnames(
            in_path = '/BackupDrive/purchases/channels/ftv',
            out_path = '/StorageDrive/purchases/ftv_small',
        )
    
    for rp, ip, op in pmanager.rglob_iter(f'*.mp4', verbose=True):
        videotools.codec_compress(str(ip), str(op))
        #print(f'{rp}\n{ip}\n{op}\n')
        #videotools.codec_compress(str(fp), str(out_fp))
        #out_fp = output_folder.joinpath(fp.name)
        
        #print(f'input: {fp}')
        #print(f'output: {out_fp}')
        videotools.codec_compress(str(ip), str(op))