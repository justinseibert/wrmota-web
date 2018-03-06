import ffmpy
#from PIL import Image
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

#def image_files(original):
#    # new_file = Sanitize.get_extension(original, split=True)['name']
#    image = Image.open(original)
#    new_file = original.rsplit('.', 1)[0]
#    sizes = {
#        'thumb': ['{}-thumbnail.jpg'.format(new_file), (128,128)],
#        'small': ['{}-small.jpg'.format(new_file), (256,256)],
#        'medium': ['{}-medium.jpg'.format(new_file), (512,512)],
#        'large': ['{}-large.jpg'.format(new_file), (1024,1024)],
#    }
#
#    for i in sizes:
#        output = sizes[i][0]
#        dimensions = sizes[i][1]
#
#        try:
#            new_image = image.copy()
#            new_image.thumbnail(dimensions)
#            new_image.save(output)
#            print('CONVERSION: successfully processed image {}'.format(output))
#        except:
#            print('CONVERSION: failed to process image {}'.format(output))
#
#    image.close()
