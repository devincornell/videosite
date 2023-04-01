from __future__ import annotations
import jinja2
import typing
import pathlib
import doctable
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

def fname_to_title(fname: str, max_char: int = 50) -> str:
    replaced = fname.replace('_', ' ').replace('-', ' ')
    return ' '.join(replaced.strip().split()).title()[:max_char]

def parse_url(urlstr: str) -> str:
    try:
        return urllib.parse.quote(urlstr)
    except TypeError as e:
        return ''

@dataclasses.dataclass
class SiteConfig:
    base_path: pathlib.Path
    thumb_base_path: pathlib.Path
    template: str
    page_fname: str
    vid_extensions: str
    img_extensions: str
    thumb_extension: str
    video_width: int
    ideal_aspect: float


class InfoBase:
    #fpath = None

    @classmethod
    def from_fpath(self, *args, **kwargs):
        raise NotImplementedError(f'This method should have been implemented by subclass.')
    
    def get_rel_path(self) -> pathlib.Path:
        '''Path relative to the original base path.'''
        return self.fpath.relative_to(self.config.base_path)
    
    def file_size(self) -> int:
        return self.fpath.stat().st_size

@dataclasses.dataclass
class VidInfo(InfoBase):
    '''Info about a single video.'''
    fpath: pathlib.Path
    probe: pydevin.FFProbeInfo
    config: SiteConfig

    @classmethod
    def from_fpath(cls, vpath: pathlib.Path, config: SiteConfig) -> VidInfo:
        if not vpath.is_file():
            raise ValueError(f'The provided video path is not a file.')
        
        probe = pydevin.ffmpeg_probe(str(vpath))
        if probe is None or not probe.has_video:
            raise ValueError(f'This file did not have valid video.')
        return cls(vpath, probe, config)
    
    def aspect(self) -> float:
        return self.probe.aspect
        
    def has_thumb(self) -> bool:
        return self.thumb_path_abs().is_file()

    def make_thumb(self):
        '''Actually make thumbnail.'''
        tfp = self.thumb_path_abs()
        tfp.parent.mkdir(exist_ok=True, parents=True)
        return pydevin.make_thumb_ffmpeg(str(self.fpath), str(tfp))
    
    def thumb_path_rel(self) -> pathlib.Path:
        '''Thumb path relative to base path.'''
        fp = self.thumb_path_abs().relative_to(self.config.base_path)
        #print(fp)
        return fp

    def thumb_path_abs(self) -> pathlib.Path:
        '''Absolute thumb path.'''
        rel_path = self.get_rel_path().with_suffix(self.config.thumb_extension)
        #print(f'=============')
        #print(rel_path)
        thumb_fname = str(rel_path).replace('/', '.')
        #print(thumb_fname)
        #print(self.config.thumb_base_path.joinpath(thumb_fname))
        return self.config.thumb_base_path.joinpath(thumb_fname)
    
    def info_dict(self) -> typing.Dict[str, str]:
        return {
            'vid_web': parse_url(self.fpath.name),
            'vid_title': fname_to_title(self.fpath.stem),
            'thumb_web': parse_url('/'+str(self.thumb_path_rel())),
            'vid_size': self.file_size(),
            'vid_size_str': doctable.format_memory(self.file_size()),
            
            # from ffmpeg probe
            'do_autoplay': 'autoplay loop muted' if self.probe.duration <= 60 else '',
            'duration': self.probe.duration,
            'duration_str': doctable.format_time(self.probe.duration),
            'res_str': f'{self.probe.res[0]}x{self.probe.res[1]}',
            'aspect': self.probe.aspect
        }

@dataclasses.dataclass
class ImgInfo(InfoBase):
    fpath: pathlib.Path
    config: SiteConfig

    @classmethod
    def from_fpath(cls, fpath: pathlib.Path, config: SiteConfig) -> ImgInfo:
        if not fpath.is_file():
            raise ValueError(f'The provided image is not a file: {fpath}')
        return cls(fpath, config)
    
    def info_dict(self) -> typing.Dict[str, str]:
        return {'path': self.get_rel_path()}

@dataclasses.dataclass
class PageInfo:
    folder_fpath: pathlib.Path
    config: SiteConfig
    vid_infos: typing.List[VidInfo]
    img_infos: typing.List[ImgInfo]
    subpages: typing.List[PageInfo]

    @classmethod
    def from_fpath(cls, fpath: pathlib.Path, config: SiteConfig, verbose: bool = False) -> PageInfo:

        if verbose:
            print(f'entering {str(fpath)}')


        if not fpath.is_dir():
            raise ValueError(f'The provided path is not a directory: {fpath}')

        subpages = list()
        for cp in sorted(fpath.iterdir()):
            if cp.is_dir() and not cp.is_relative_to(config.thumb_base_path):
                try:
                    subpages.append(cls.from_fpath(cp, config, verbose=verbose))
                except ValueError:
                    print(f'Could not parse subdir {str(cp)}')

        return cls(
            folder_fpath = fpath, 
            config = config,
            vid_infos = cls.get_info_objs(fpath, config, VidInfo, config.vid_extensions),
            img_infos = cls.get_info_objs(fpath, config, ImgInfo, config.img_extensions),
            subpages = subpages,
        )
    
    def page_path(self) -> pathlib.Path:
        return self.folder_fpath.joinpath(self.config.page_fname)
    
    def page_path_rel(self) -> pathlib.Path:
        return self.folder_fpath_rel.joinpath(self.config.page_fname)
    
    @property
    def folder_fpath_rel(self) -> pathlib.Path:
        return self.folder_fpath.relative_to(self.config.base_path)
    
    @property
    def has_childs(self) -> bool:
        return all([self.total_vids > 0, self.total_imgs > 0, self.num_subpages > 0])
    
    @property
    def num_subpages(self) -> int:
        return len(self.subpages)

    @property
    def total_vids(self) -> int:
        return self.num_vids + sum([sp.total_vids for sp in self.subpages])
    
    @property
    def num_vids(self) -> int:
        return len(self.vid_infos)

    @property
    def total_imgs(self) -> int:
        return self.num_imgs + sum([sp.total_imgs for sp in self.subpages])
    
    @property
    def num_imgs(self) -> int:
        return len(self.img_infos)
    
    @property
    def total_size(self) -> int:
        return self.data_size + sum([sp.data_size for sp in self.subpages])
    
    @property
    def data_size(self) -> int:
        return sum(v.file_size() for v in self.vid_infos) + sum(im.file_size() for im in self.img_infos)
    
    def all_vid_infos(self) -> typing.List[VidInfo]:
        if not self.has_childs:
            return list()
        return self.vid_infos + [vi for sp in self.subpages for vi in sp.all_vid_infos()]

    def make_thumbs(self, verbose: bool = False) -> None:
        vis = self.vid_infos
        if verbose:
            print(f'making thumbns in {self.folder_fpath}')
            vis = tqdm.tqdm(vis, ncols=80)
        
        for vi in vis:
            vi.make_thumb()

    @classmethod
    def get_info_objs(cls, fpath: pathlib.Path, config: SiteConfig, InfoType: type, extensions: typing.List[str]) -> typing.List[VidInfo]:
        img_infos = list()
        for fp in cls.base_get_fpaths(fpath, extensions=extensions):
            try:
                img_infos.append(InfoType.from_fpath(fp, config))
            except ValueError as e:
                pass
        return img_infos
        
    @staticmethod
    def base_get_fpaths(fpath: pathlib.Path, extensions: typing.List[str]) -> typing.List[pathlib.Path]:
        all_paths = list()
        for ext in extensions:
            all_paths += list(sorted(fpath.glob(f'*.{ext}')))
        return all_paths

    @property
    def thumb_path(self) -> pathlib.Path:
        pass
    
    def vid_fpaths(self) -> typing.List[pathlib.Path]:
        return self.get_fpaths(extensions=self.config.vid_extensions)
    
    def img_fpaths(self) -> typing.List[pathlib.Path]:
        return self.get_fpaths(extensions=self.config.img_extensions)

    def get_fpaths(self, extensions: typing.List[str]) -> typing.List[pathlib.Path]:
        all_paths = list()
        for ext in extensions:
            all_paths += list(sorted(self.fpath.glob(f'*.{ext}')))
        return all_paths
    
    def get_best_thumb(self) -> pathlib.Path:
        vis = self.all_vid_infos()
        if len(vis) == 0:
            return None
        vi = min(vis, key=lambda sp: (sp.aspect() - self.config.ideal_aspect))
        return vi.thumb_path_rel()
    
    def vid_info_dicts(self) -> typing.List[typing.Dict[str, str]]:
        return [vi.info_dict() for vi in self.vid_infos]

    def img_info_dicts(self) -> typing.List[typing.Dict[str, str]]:
        return [ii.info_dict() for ii in self.img_infos]

    def subpage_info_dicts(self) -> typing.List[typing.Dict[str, str]]:
        return [sp.info_dict() for sp in self.subpages]

    def info_dict(self) -> typing.Dict[str, float]:
        print(self.get_best_thumb())
        return {
            'path': f'/{str(self.page_path_rel())}', 
            #'path': str(child_path).replace('_', ' '), 
            'name': fname_to_title(self.folder_fpath.name), 
            'subfolder_thumb': parse_url(self.get_best_thumb()),
            'num_vids': self.total_vids,
            'num_imgs': self.total_imgs,
            'num_subfolders': self.num_subpages,
            'files_size_str': doctable.format_memory(self.total_size),
        }


def make_pages(fpath: pathlib.Path, config: SiteConfig, make_thumbs: bool = True) -> PageInfo:
    page_tree = PageInfo.from_fpath(fpath, config, verbose=True)
    return make_files_recursive(page_tree, config=config, make_thumbs=make_thumbs)

def make_files_recursive(pinfo: PageInfo, config: SiteConfig, make_thumbs: bool):
    print(f'starting in {str(pinfo.folder_fpath)}')

    print(f'making thumbnails')
    if make_thumbs:
        pinfo.make_thumbs(verbose=True)

    for sp in pinfo.subpages:
        make_files_recursive(sp, config, make_thumbs=make_thumbs)

    sp_infos = list(sorted(pinfo.subpage_info_dicts(), key=lambda pi: pi['name']))
    vid_infos = list(sorted(pinfo.vid_info_dicts(), key=lambda vi: -vi['aspect']))
    #img_infos = list(sorted(pinfo.img_info_dicts(), key=lambda vi: vi))

    import json
    print(json.dumps(sp_infos, indent=2))
    #print(json.dumps(vid_infos, indent=2))
    #print(json.dumps(img_infos, indent=2))
    

    html_str = config.template.render(
        vid_info = vid_infos, 
        child_paths = sp_infos, 
        video_width = config.video_width, 
        name = pinfo.folder_fpath_rel,
    )

    # write the template
    pp = pinfo.page_path()
    print(f'saving {pp} with {pinfo.num_imgs} images, {pinfo.num_vids} vids, and {pinfo.num_subpages} subfolders')
    with pp.open('w') as f:
        f.write(html_str)


if __name__ == '__main__':


    base_path = pathlib.Path('/StorageDrive/purchases/')
    thumb_path = base_path.joinpath('_thumbs/')

    print('reading template')
    template_path = pathlib.Path('templates/band1_template.html')
    with template_path.open('r') as f:
        template_html = f.read()
    environment = jinja2.Environment()
    template = environment.from_string(template_html)


    config = SiteConfig(
        base_path = base_path,
        thumb_base_path = thumb_path,
        template = template,
        page_fname = 'web2.html',
        vid_extensions = ['mp4'],
        img_extensions = ['png', 'gif', 'jpg'],
        thumb_extension = '.gif',
        video_width = 300,
        ideal_aspect = 1.0,
    )
    
    print(f'making pages')
    make_pages(
        fpath=base_path.joinpath('tmp/'),
        config=config,
        make_thumbs=True,
    )


