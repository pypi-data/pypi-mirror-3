import os
import datetime
import hashlib
import errno
import shutil
from omdox import settings
from omdox import feedback
from omdox.render import render

op = os.path

def build(dir, directory, contents_list):
    build_dir = os.path.join(dir, '_build', directory)
    source_dir = os.path.join(dir, directory)
    # make the directories
    try:
        os.makedirs(build_dir)
        feedback.info('[mkdir] created %s' % build_dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise
    # now process the contents
    for content in contents_list:
        # make the content path
        source_path = os.path.join(source_dir, content[0])
        build_path = os.path.join(build_dir, content[0])
        # get the extention
        ext = os.path.splitext(source_path)[1]
        # try for the . extention
        # if this is not a render extention, copy it to new path
        if ext in settings.EXTENTIONS:
            render(source_path, build_path)
            feedback.info('[rendered] %s' % build_path)
        else:
            shutil.copyfile(source_path, build_path)
            feedback.info('[copied] %s' % build_path)


def clean(dir=False):
    # under no cirsumstances do anything of dir is False
    if dir == False:
        return
    # make the build directory if it doesn't exist
    if not os.path.exists('%s/_build' % dir):
        os.mkdir('%s/_build' % dir)
    # delete and remake the builddir
    shutil.rmtree('%s/_build' % dir)


def get_hexdigest(f, block_size=2**20):
    # don't catch the IOError - bubble it up
    f = open(f, 'r')
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    f.close()
    return md5.hexdigest()


def get_contents_dict(dir):
    data = {}
    for i in os.listdir(dir):
        # don't process exlcudes
        if i in settings.EXCLUDED:
            continue
        # populate!
        path = op.join(dir, i)
        if op.isfile(path):
            key = op.relpath(dir).replace("\\", "/")
            hexdigest = get_hexdigest(path)
            try:
                data[key].append((i, hexdigest))
            except KeyError:
                data[key] = [(i, hexdigest)]
        else:
            data.update(get_contents_dict(path))
    return data
