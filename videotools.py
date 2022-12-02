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
        .input(input_fname, hwaccel='cuda')
        .output(output_fname, vcodec=vcodec, crf=crf)
        .overwrite_output()
    )



        
        
        
    
    