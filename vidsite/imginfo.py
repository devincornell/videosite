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
from .siteconfig import SiteConfig
from .util import *

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
        return {
            'path': parse_url(self.fpath.name),
            'title': fname_to_title(self.fpath.stem),
        }
