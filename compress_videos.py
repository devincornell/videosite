from __future__ import annotations
import pathlib
import tqdm
#import videotools
import pydevin
import enum
import dataclasses
import typing
import copypathmanager
import sys
        
def pmanager_lookup(select: PathSelect) -> copypathmanager.CopyPathManager:
    uncompressed_path = '/BackupDrive/uncompressed_purchases'
    storage_path = '/StorageDrive/purchases'
    patterns = [f'*.mp4', f'*.mov', f'*.wmv']
    
    if select == PathSelect.ALL:
        pmanager = copypathmanager.CopyPathManager.from_pathnames(
            in_path = f'/StorageDrive/purchases/uncompressed2',
            out_path = f'/AddStorage/newly_compressed',
            patterns=patterns,
        )

    elif select == PathSelect.ISLA:
        pmanager = copypathmanager.CopyPathManager.from_pathnames(
            in_path = f'{storage_path}/creators/isla_summer/onlyfans_from_bunkr_libx265_hvec',
            out_path = f'{storage_path}/creators/isla_summer/converted_from_libx265',
            patterns=patterns,
        )

    else:
        raise ValueError(f'a pathmanager was not provided for {select}. please add this to the script.')
    return pmanager
        
        
        
        
if __name__ == '__main__':
    
    class PathSelect(enum.Enum):
        ALL = enum.auto()
        ISLA = enum.auto()

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
    

    pmanager = pmanager_lookup(select)
    print(f'{pmanager.in_path=}\n{pmanager.out_path=}')

    print(f'identifying fnames to use')
    use_fpaths: typing.Set[copypathmanager.PathEntry] = set()
    for pe in pmanager.rglob_iter(verbose=False):
        new_path = pe.new_path.with_suffix('.mp4')
        print(f'{pe.rel_path}')
        if not new_path.is_file():
            print(f'   does not exist and will be created')
            use_fpaths.add(pe)
            pass
        else:
            if not force_overwrite:
                print(f'   exists and won\'t be overwritten')
                pass
            else:
                print(f'   exists and will be overwritten')
                use_fpaths.add(pe)
            
            old_size = pe.in_path.stat().st_size
            new_size = new_path.stat().st_size
            size_change = (new_size-old_size)/old_size*100
            if new_size > old_size:
                print(f'   WARNING: file size increased by {size_change:0.2f}%')
            else:
                print(f'   compression rate: {new_size/old_size*100:0.2f}%')
                

    #exit()
    print(f'Now compressing {len(use_fpaths)} videos.')
    
    ct = 0
    for pe in tqdm.tqdm(use_fpaths, ncols=80):
        new_path = pe.new_path.with_suffix('.mp4')

        # add checks one more time to be sure
        if not new_path.is_file() or force_overwrite:
            try:
                pe.new_path.parent.mkdir(exist_ok=True, parents=True)
            except FileExistsError:
                pass

            pydevin.codec_compress(str(pe.in_path), str(new_path))
            pass
        ct += 1
        
    print(f'finished processing {ct} videos.')
