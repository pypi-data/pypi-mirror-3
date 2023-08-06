import os
import hashlib
from uuid import uuid4
from django.conf import settings


def random_filename(directory, ext=None, root=settings.MEDIA_ROOT):
    """Gets a random untaken filename based on a root, a subdirectory path,
    returns the full path, the filename, and the subdirectory + filename.
    """
    path = ''
    if not os.path.exists(root + directory):
        os.mkdir(root + directory)
    while path == '' or os.path.exists(path):
        filename = hashlib.sha1(str(uuid4())).hexdigest()
        if ext:
            filename += '.' + ext
        path = '%s%s%s' % (
            root,
            directory,
            filename
        )
    return path, filename, directory + filename


import re


def slugify(inStr):
    removelist = ["a", "an", "as", "at", "before", "but", "by", "for", "from",
        "is", "in", "into", "like", "of", "off", "on", "onto", "per", "since",
        "than", "the", "this", "that", "to", "up", "via", "with"]
    for a in removelist:
        aslug = re.sub(r'\b' + a + r'\b', '', inStr)
    aslug = re.sub('[^\w\s-]', '', aslug).strip().lower()
    aslug = re.sub('\s+', '-', aslug)
    return aslug
