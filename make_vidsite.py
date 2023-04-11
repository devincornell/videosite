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

import vidsite


def make_pages(fpath: pathlib.Path, config: vidsite.SiteConfig, make_thumbs: bool = True) -> vidsite.PageInfo:
    page_tree = vidsite.PageInfo.from_fpath(fpath, config, verbose=True)
    return make_files_recursive(page_tree, config=config, make_thumbs=make_thumbs)

def make_files_recursive(pinfo: vidsite.PageInfo, config: vidsite.SiteConfig, make_thumbs: bool):
    print(f'starting in {str(pinfo.folder_fpath)}')

    print(f'making thumbnails')
    if make_thumbs:
        pinfo.make_thumbs(verbose=True)

    for sp in pinfo.subpages:
        make_files_recursive(sp, config, make_thumbs=make_thumbs)

    sp_infos = list(sorted(pinfo.subpage_info_dicts(), key=lambda pi: pi['name']))
    vid_infos = list(sorted(pinfo.vid_info_dicts(), key=lambda vi: -vi['aspect']))
    img_infos = list(sorted(pinfo.img_info_dicts(), key=lambda vi: vi['title']))

    vids = [vi for vi in vid_infos if not vi['is_clip']]
    clips = [vi for vi in vid_infos if vi['is_clip']]

    import json
    print(json.dumps(sp_infos, indent=2))
    #print(json.dumps(vid_infos, indent=2))
    #print(json.dumps(img_infos, indent=2))
    

    html_str = config.template.render(
        vids = vids, 
        clips = clips,
        imgs = img_infos,
        child_paths = sp_infos, 
        video_width = config.video_width, 
        clip_width = config.clip_width,
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


    config = vidsite.SiteConfig(
        base_path = base_path,
        thumb_base_path = thumb_path,
        template = template,
        page_fname = 'web2.html',
        vid_extensions = ['mp4'],
        img_extensions = ['png', 'gif', 'jpg'],
        thumb_extension = '.gif',
        video_width = '85%',
        clip_width = '100%',
        ideal_aspect = 1.8,
        clip_duration = 60,
        do_clip_autoplay = False,
    )
    
    print(f'making pages')
    make_pages(
        fpath=base_path,#.joinpath('TEMP_VIDS_LINK/'),
        config=config,
        make_thumbs=True,
    )


