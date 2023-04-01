import glob
import pathlib
import ffmpeg
import sys
import os
import videotools
import pprint

if __name__ == '__main__':
    vid_fpath = pathlib.Path('/StorageDrive/purchases/compressed_crf=30/cory_chase/Cory Chase And Jessica Rex What A Nice Vibrator You Have #le.mp4')
    
    info = videotools.ffmpeg_probe(str(vid_fpath))
    pprint.pprint(info)
    

