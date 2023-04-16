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

from .util import *
from .siteconfig import SiteConfig
from .vidinfo import VidInfo
from .imginfo import ImgInfo



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
        return any([self.total_vids > 0, self.total_imgs > 0, self.num_subpages > 0])
    
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
        mvi = min(vis, key=lambda sp: abs(sp.aspect() - self.config.ideal_aspect))
        print('-->', mvi.aspect(), abs(mvi.aspect()-self.config.ideal_aspect), [vi.aspect() for vi in vis])
        return mvi.thumb_path_rel()
    
    def vid_info_dicts(self) -> typing.List[typing.Dict[str, str]]:
        return [vi.info_dict() for vi in self.vid_infos]

    def img_info_dicts(self) -> typing.List[typing.Dict[str, str]]:
        return [ii.info_dict() for ii in self.img_infos]

    def subpage_info_dicts(self) -> typing.List[typing.Dict[str, str]]:
        return [sp.info_dict() for sp in self.subpages]

    def info_dict(self) -> typing.Dict[str, float]:
        return {
            'path': f'/{str(self.page_path_rel())}', 
            'name': fname_to_title(self.folder_fpath.name), 
            'subfolder_thumb': parse_url('/'+str(self.get_best_thumb())),
            'num_vids': self.total_vids,
            'num_imgs': self.total_imgs,
            'num_subfolders': self.num_subpages,
            'files_size_str': doctable.format_memory(self.total_size),
            'idx': fname_to_id(self.folder_fpath.name),
        }