# ***WARNING***
# Running this file  will delete all files and directories from the micropython device it's running on
# If you run  keep_this=False it will delete this file as well.

# see https://docs.micropython.org/en/latest/library/os.html for os function list
#https://gist.github.com/romilly/5a1ff86d1e4d87e084b76d5651f23a40
import os


def _delete_all(directory='lib', keep_this=True):
    try:
        import machine
    except:
        # not a micropython board so exit gracefully
        print('Not a micro-python board! Leaving it well alone.')
        return
    for fi in os.ilistdir(directory):
        fn, ft = fi[0:2] # can be 3 or 4 items returned!
        if fn == 'secrets.py' or fn == 'main.py' or fn == '_nuke.py':
            continue
        fp = '%s/%s' % (directory, fn)
        print('removing %s' % fp) 
        if ft == 0x8000:
            os.remove(fp)
        else:
            _delete_all(fp)
            os.rmdir(fp)


_delete_all()
