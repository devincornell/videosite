
import jinja2
import typing
import pathlib
import dataclasses
import pprint
import subprocess
import os
import tqdm
import ffmpeg
import sys
#import videotools
import pydevin
import html
import urllib.parse

@dataclasses.dataclass
class VidEntry:
    pass

def fname_to_title(fname: str) -> str:
    #fname = fpath.stem
    replaced = fname.replace('_', ' ').replace('-', ' ')
    return ' '.join(replaced.strip().split()).title()

def rmdir_recursive(directory: pathlib.Path):
    for item in directory.iterdir():
        if item.is_dir():
            rmdir_recursive(item)
        else:
            item.unlink()
    directory.rmdir()

def parse_url(urlstr: str) -> str:
    try:
        return urllib.parse.quote(urlstr)
    except TypeError as e:
        return ''
        


def make_files_recursive(
        base_path: pathlib.Path, 
        thumb_base_path: pathlib.Path, 
        template: jinja2.Template, 
        page_fname: str = 'web.html', 
        fpath: pathlib.Path = None, # changed in recursion
        vid_extension: str = '.mp4', 
        thumb_extension: str = '.gif', 
        video_width: int = 300,
        log_func: typing.Callable[[typing.Any], None] = print,
        clean_thumbs: bool = False,
    ):
    print(f'\nstarting in {fpath}')

    if fpath is None:
        fpath = base_path
        
        if clean_thumbs:
            rmdir_recursive(thumb_base_path)
            thumb_base_path.mkdir()
        
        
    rel_path = fpath.relative_to(base_path)
    thumb_path = thumb_base_path.joinpath(rel_path)
    rel_thumb_path = thumb_path.relative_to(base_path)
    
    # go through videos in the current folder
    vid_info = list()
    total_size = 0
    vid_fpaths = list(sorted(fpath.glob(f'*{vid_extension}')))
    current_folder_thumbs = list()
    for i, vid_path in tqdm.tqdm(enumerate(vid_fpaths), total=len(vid_fpaths)):
        thumb_fname = vid_path.name.replace(vid_extension, thumb_extension)
        thumb_web = f'/{rel_thumb_path.joinpath(thumb_fname)}'
        thumb_abs = thumb_path.joinpath(thumb_fname)
        thumb_abs.parent.mkdir(parents=True, exist_ok=True)
        
        # actually make thumbnail
        pydevin.make_thumb_ffmpeg(str(vid_path), str(thumb_abs))
        
        # get file size
        vid_size = vid_path.stat().st_size if vid_path.is_file() else None
        total_size += vid_size
        
        # probe the video file
        probe = pydevin.ffmpeg_probe(str(vid_path)) if vid_path.is_file() else None
        has_video = probe is not None and probe.has_video

        if probe is not None and probe.has_video:
            try:
                # keep this for use in template rendering
                vid_info.append({
                    'vid_web': parse_url(vid_path.name),
                    'vid_title': fname_to_title(vid_path.stem),
                    'thumb_web': parse_url((thumb_web)),
                    'vid_size': vid_size,
                    'vid_size_str': pydevin.format_memory(vid_size),
                    
                    # from ffmpeg probe
                    'do_autoplay': 'autoplay loop muted' if probe.duration <= 120 else '',
                    'duration': probe.duration,
                    'duration_str': pydevin.format_time(probe.duration),
                    'res_str': f'{probe.res[0]}x{probe.res[1]}',
                    'aspect': probe.aspect if has_video else None
                })

                if thumb_abs.is_file() and probe is not None:
                    current_folder_thumbs.append((probe.aspect, thumb_web))

            except KeyError:
                pass# usually raised when probe.duration has a keyerror

            

        else:
            print(f'\nCould not process video: {vid_path}')
        
    # go through subdirectories
    child_paths = list()
    num_child_vids = 0
    child_thumbs = list()
    child_path_iter = list(sorted(fpath.iterdir()))
    for i, child_path in enumerate(child_path_iter):
        if child_path.is_dir() and not child_path.is_relative_to(thumb_base_path):
            (thumb_aspect,subfolder_thumb), num_vids, num_subfolders, size = make_files_recursive(base_path, thumb_base_path, template, page_fname=page_fname, fpath=child_path, vid_extension=vid_extension, thumb_extension=thumb_extension, log_func=log_func)
            num_child_vids += num_vids
            total_size += size
            subfolder = str(child_path.relative_to(fpath).joinpath(page_fname))
            child_paths.append({
                'subfolder': subfolder, 
                #'path': str(child_path).replace('_', ' '), 
                'name': fname_to_title(child_path.name), 
                'subfolder_thumb': parse_url(subfolder_thumb),
                'num_vids': num_vids,
                'num_subfolders': num_subfolders,
                'files_size_str': doctable.format_memory(size),
            })
            if subfolder_thumb is not None:
                child_thumbs.append((thumb_aspect,subfolder_thumb))

    # sort according to name
    child_paths = list(sorted(child_paths, key=lambda x: x['name']))
    vid_info = list(sorted(vid_info, key=lambda x: x['vid_title']))

    # get the correct thumb for this folder
    current_thumb = (None, None)
    optimal_ratio = 1.6
    if len(current_folder_thumbs) > 0:
        current_thumb = list(sorted(current_folder_thumbs, key=lambda x: abs(x[0]-optimal_ratio)))[0]
    elif len(child_thumbs) > 0:
        current_thumb = list(sorted(child_thumbs, key=lambda x: abs(x[0]-optimal_ratio)))[0]

    # render the template
    html_str = template.render(vid_info=vid_info, child_paths=child_paths, video_width=video_width, name=rel_path)

    # write the template
    html_path = fpath.joinpath(page_fname)
    if log_func is not None: log_func(f'\nsaving {len(vid_info)} vids to {html_path}')
    with html_path.open('w') as f:
        f.write(html_str)

    return current_thumb, len(vid_info)+num_child_vids, len(child_paths), total_size
    



if __name__ == '__main__':
    base_path = pathlib.Path('/StorageDrive/purchases/')
    thumb_path = base_path.joinpath('tmp/thumbs')
    
    template_path = pathlib.Path('templates/band1_template.html')

    stepper = doctable.Stepper()
    stepper.step(f'{base_path=}, {template_path=}')

    stepper.step('reading template')
    with template_path.open('r') as f:
        template_html = f.read()
    environment = jinja2.Environment()
    template = environment.from_string(template_html)

    make_files_recursive(base_path, thumb_path, template, log_func=stepper.step)
    #print(glob.glob(str(base_path) + '/*.mp4'), str(base_path) + '/*.mp4')
    
    # need for each folder:
    #  for each video
    #   relative video path - linking video
    #   relative thumb path - linking thumb
    #   absolute video path - reading file
    #   absolute thumb path

    exit()
    #def vid_to_thumb_path(rel_vid_path: pathlib.Path, thumb_path: pathlib.Path) -> pathlib.Path:
    #    
    # we expect an index.html file at each of the key paths here
    folders: typing.Dict[pathlib.Path, typing.List[pathlib.Path]] = dict()
    for vid_path in base_path.rglob('*.mp4'):
        folders.setdefault(vid_path.parent, list())
        folders[vid_path.parent].append(vid_path)

    for folder_path, vid_paths in folders.items():
        print(f'{folder_path}: {len(vid_paths)} videos')
        rel_folder_path = folder_path.relative_to(base_path).joinpath(thumb_path)

        vid_info = list()
        for vp in vid_paths:
            #rel_vid_path.stem).with_suffix('.gif')
            #thumb_folder = root.joinpath(thumb_path_rel).joinpath(vp.parent)
            vid_info.append({
                'vid_fname': vp.name,
                #'thumb_path': .#folder_path.relative_to(base_path),
            })
        targ_vid_paths = [target_path.joinpath(vp.relative_to(base_path)) for vp in vid_paths]
        for rvp in rel_vid_paths:
            print(f'\t\t{rvp}')


        index_html = template.render()
        with folder_path.joinpath('index.html').open('w') as f:
            f.write(index_html)

    if False:
        thumb_path.mkdir(parents=True, exist_ok=True)

        rel_vid_path = vid_path.relative_to(base_path)
        thumb_path = target_path.joinpath(rel_vid_path.stem).with_suffix('.gif')
        
        folders.setdefault(1, list())
        folders[thumb_path.parent].append()
        folders.add()


        thumb_path.mkdir(parents=True, exist_ok=True)
        print(vid_path, rel_vid_path, thumb_path)
    








    
        target_file = target_path.joinpath('index.html')
