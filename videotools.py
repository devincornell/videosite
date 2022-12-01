import ffmpeg
import sys
import glob
import pathlib
import tqdm


def ffmpeg_catch_errors(ffmpeg_command) -> str:
    try:
        output = ffmpeg_command.run(capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        print('\n', e.stderr.decode(), file=sys.stderr)
        pass
    else:
        return output


def make_thumb_ffmpeg(in_filename, out_filename):
    # copied directly from here: 
    # https://api.video/blog/tutorials/automatically-add-a-thumbnail-to-your-video-with-python-and-ffmpeg
    
    try:
        probe = ffmpeg.probe(in_filename)
    except ffmpeg._run.Error:
        pass
    else:
        try:
            time = float(probe['streams'][0]['duration']) // 2
            width = probe['streams'][0]['width']
            try:
                (
                    ffmpeg
                    .input(in_filename, ss=time)
                    .filter('scale', width, -1)
                    .output(out_filename, vframes=1)
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
            except ffmpeg.Error as e:
                print(e.stderr.decode(), file=sys.stderr)
                pass
        except KeyError:
            pass



def codec_compress(input_fname: str, output_fname: str, vcodec: str = 'libx265', crf: int = 30):
    return ffmpeg_catch_errors(
        ffmpeg
        .input(input_fname)
        .output(output_fname, vcodec=vcodec, crf=crf)
        .overwrite_output()
    )


if __name__ == '__main__':
    #folder = '/BackupDrive/purchases/tmp/test/'
    #input_folder = pathlib.Path('/BackupDrive/purchases/channels/rsc')
    #output_folder = pathlib.Path('/DataDrive/purchases/rsc_small')
    
    input_folder = pathlib.Path('/DataDrive/purchases/isla_summer')
    output_folder = pathlib.Path('/DataDrive/purchases/isla_summer_small')
    
    
    fnames = list(input_folder.glob(f'*.mp4'))
    
    
    
    for fp in tqdm.tqdm(fnames):
        out_fp = output_folder.joinpath(fp.name)
        
        #print(f'input: {fp}')
        #print(f'output: {out_fp}')
        codec_compress(str(fp), str(out_fp))
        
        
        
    
    