"""Check that all images of a directory are used in a website. Also
report images which are used more than once, and images which are do
not come from the directory.

FIXME: it works but may not be reliable. It will be enhanced/rewritten
(use getopt, change REGEXP, etc.)

$Id: checkimages.py 19 2007-09-06 08:00:06Z damien.baty $
"""


import os
import re
import sys


REGEXP = re.compile('/images/(.*?\.jpg)')

USAGE = """\
%s <sources-dir> <image-dir>
""" % sys.argv[0]


def main():
    if len(sys.argv) != 3:
        print USAGE
        sys.exit(1)

    referenced = {}
    sources_dir = sys.argv[1]
    images_dir = sys.argv[2]

    ## List image links in source files
    for dirpath, _, filenames in os.walk(sources_dir):
        for filename in filenames:
            if not filename.endswith('.txt'):
                continue
            path = os.sep.join((dirpath, filename))
            images = REGEXP.findall(open(path).read())
            for image in images:
                ref = referenced.get(image, [])
                ref.append(path)
                referenced[image] = ref

    ## List images in image directory
    images = os.listdir(images_dir)

    ## List images which are not referenced in source files
    not_referenced = []
    for image in images:
        if not referenced.has_key(image):
            not_referenced.append(image)

    ## List images which are referenced in a source file but do not
    ## exist in the image directory
    unknown = {}
    for image, filenames in referenced.items():
        if image not in images:
            unknown[image] = filenames

    print '%d images.' % len(images)

    if not_referenced:
        print 'Images below are not used in source files.'
        print '\n'.join(not_referenced)

    if unknown:
        print 'Images below are used but were not found in image '\
            'directory.'
        for image, filenames in unknown.items():
            print '"%s", used in %s' % (image, ', '.join(filenames))


if __name__ == '__main__':
    main()
