import os
import sys

import h5py

from readerHIS import openHIS

def main():
    if len(sys.argv) < 2:
        print('syntax: ' + sys.argv[0] + ' <his file>')
        sys.exit(1)

    his_file = sys.argv[1]
    stem, _ = os.path.splitext(his_file)
    his = openHIS(his_file)
    for idx, section in enumerate(his):
        h5_file = stem + ('-%04d.h5' % idx)

        if os.path.exists(h5_file):
            print('Refusing to write to ' + h5_file + ': file exists')
            sys.exit(1)

        h5 = h5py.File(h5_file)
        dset = h5.create_dataset("Image", section.shape, 'i')
        dset[...] = section
        dset.attrs['comment'] = section.HIS.comment
        dset.attrs['his-header'] = repr(section.HIS.hdr)
        h5.close()

if __name__ == '__main__':
    main()

# vim:sw=4:sts=4:et
