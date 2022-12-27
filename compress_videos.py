from __future__ import annotations
import pathlib
import tqdm
import videotools
import enum
import dataclasses
import typing
import copypathmanager
import sys
        
def pmanager_lookup(select: PathSelect) -> copypathmanager.CopyPathManager:
    uncompressed_path = '/BackupDrive/uncompressed_purchases'
    compressed_path = '/StorageDrive/purchases/compressed'
    patterns = [f'*.mp4', f'*.mov', f'*.wmv']
    
    if select == PathSelect.UNCOMPRESSED:
        pmanager = copypathmanager.CopyPathManager.from_pathnames(
            in_path = f'{uncompressed_path}',
            out_path = f'{compressed_path}',
            patterns=patterns,
        )
    else:
        raise ValueError(f'a pathmanager was not provided for {select}. please add this to the script.')
    return pmanager
        
        
        
        
if __name__ == '__main__':
    
    class PathSelect(enum.Enum):
        UNCOMPRESSED = enum.auto()
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
        if not new_path.is_file():
            print(f'{pe.rel_path} does not exist and will be created')
            use_fpaths.add(pe)
            pass
        else:
            if not force_overwrite:
                #print(f'{rp} already exists and won\'t be overwritten')
                pass
            else:
                print(f'{pe.rel_path} already exists and will be overwritten')
                use_fpaths.add(pe)
                
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

            videotools.codec_compress(str(pe.in_path), str(new_path))
            pass
        ct += 1
        
    print(f'finished processing {ct} videos.')