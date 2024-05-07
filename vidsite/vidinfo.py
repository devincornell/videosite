
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


from .infobase import InfoBase
from .util import *
from .siteconfig import SiteConfig


@dataclasses.dataclass
class VidInfo(InfoBase):
    '''Info about a single video.'''
    fpath: pathlib.Path
    vf: pydevin.VideoFile
    probe: pydevin.ProbeInfo
    config: SiteConfig

    @classmethod
    def from_fpath(cls, vpath: pathlib.Path, config: SiteConfig) -> VidInfo:
        if not vpath.is_file():
            raise ValueError(f'The provided video path is not a file.')
        
        try:
            probe = pydevin.VideoFile(str(vpath)).probe()
            probe.video # will error if there is no video stream
        except pydevin.ProbeError:
            raise ValueError(f'This file did not have valid video.')
        
        return cls(
            fpath = vpath, 
            vf = pydevin.VideoFile(vpath),
            probe = probe, 
            config = config,
        )
    
    def aspect(self) -> float:
        return self.probe.video.width / self.probe.video.height
        
    def has_thumb(self) -> bool:
        return self.thumb_path_abs().is_file()

    def make_thumb(self):
        '''Actually make thumbnail.'''
        tfp = self.thumb_path_abs()
        if not tfp.is_file(): # NOTE: delete this if trying to force write
            tfp.parent.mkdir(exist_ok=True, parents=True)
            return self.vf.make_thumb(str(tfp))
            #return pydevin.make_thumb_ffmpeg(str(self.fpath), str(tfp))
    
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
    
    @property
    def is_clip(self) -> bool:
        return self.probe.duration <= self.config.clip_duration
    
    def info_dict(self) -> typing.Dict[str, str|int|bool]:
        return {
            'vid_web': parse_url(self.fpath.name),
            'vid_title': fname_to_title(self.fpath.stem),
            'thumb_web': parse_url('/'+str(self.thumb_path_rel())),
            'vid_size': self.file_size(),
            'vid_size_str': pydevin.format_memory(self.file_size()),
            
            # from ffmpeg probe
            'is_clip': self.is_clip,
            'do_autoplay': 'autoplay loop muted' if self.is_clip and self.config.do_clip_autoplay else '',
            'duration': self.probe.duration,
            'duration_str': pydevin.format_time(self.probe.duration),
            'res_str': f'{self.probe.video.width}x{self.probe.video.height}',
            'aspect': self.probe.video.aspect_ratio(),
            'idx': fname_to_id(self.fpath.stem)
        }