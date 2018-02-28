import ffmpy
from wrmota.api import sanitize as Sanitize

def audio_files(original):
    new_file = Sanitize.get_extension(original, split=True)['name']
    webm = '{}.webm'.format(new_file)
    mp3 = '{}.mp3'.format(new_file)
    ogg = '{}.ogg'.format(new_file)

    try:
        ff = ffmpy.FFmpeg(
            inputs={ original: '-n' },
            outputs={
                webm: '-dash 1',
                mp3: None,
                ogg: None,
            },
        )
        ff.run()
        print('CONVERSION: audio files {} successfully converted to webm,mp3,ogg'.format(original))
    except:
        print('CONVERSION: failed to convert files')
