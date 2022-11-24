
import jinja2
import typing
import pathlib
import doctable
import dataclasses
import pprint

@dataclasses.dataclass
class VidEntry:
    pass

def make_files_recursive(base_path: pathlib.Path, thumb_base_path: pathlib.Path, template: jinja2.Template, page_fname: str = 'web.html', fpath: pathlib.Path = None, vid_extension: str = '.mp4', thumb_extension: str = '.gif', log_func=print):
    if fpath is None:
        fpath = base_path
    rel_path = fpath.relative_to(base_path)
    thumb_path = thumb_base_path.joinpath(rel_path)
    rel_thumb_path = thumb_path.relative_to(base_path)
    
    vid_info = list()
    for vp in fpath.glob(f'*{vid_extension}'):

        thumb_fname = vp.name.replace(vid_extension, thumb_extension)
        thumb_abs = thumb_path.joinpath(thumb_fname)
        thumb_abs.mkdir(parents=True, exist_ok=True)

        vid_info.append({
            'vid_web': vp.name,
            'vid_title': vp.name.replace('_', ' '),
            'thumb_web': f'/{rel_thumb_path.joinpath(thumb_fname)}',
        })
    
    
    child_paths = list()
    for child_path in fpath.iterdir():
        if child_path.is_dir() and not child_path.is_relative_to(thumb_base_path):
            make_files_recursive(base_path, thumb_base_path, template, page_fname=page_fname, fpath=child_path, vid_extension=vid_extension, thumb_extension=thumb_extension, log_func=log_func)
            subfolder = str(child_path.relative_to(fpath).joinpath(page_fname))
            child_paths.append({'subfolder': subfolder, 'name': str(child_path).replace('_', ' ')})

    html_str = template.render(vid_info = vid_info, child_paths=child_paths)

    html_path = fpath.joinpath(page_fname)
    if log_func is not None: log_func(f'saving {len(vid_info)} vids to {html_path}')
    with html_path.open('w') as f:
        f.write(html_str)




if __name__ == '__main__':
    base_path = pathlib.Path('/BackupDrive/purchases/')
    thumb_path = pathlib.Path('/BackupDrive/purchases/tmp/thumbs')
    #thumb_path = base_path.joinpath('tmp/thumbs/')
    
    
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
