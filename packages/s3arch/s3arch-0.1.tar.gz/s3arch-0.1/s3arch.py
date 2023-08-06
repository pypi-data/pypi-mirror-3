import logging
import os
import shutil
import tarfile

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import boto


class S3Archiver(object):

    def __init__(self, key=None, secret=None):
        self.conn = boto.connect_s3(key, secret)

    def archive(self, bucket, path, compress=False):

        # make root path, if it does not exist
        if not os.path.exists(path):
            os.mkdir(path)

        bckt = self.conn.get_bucket(bucket)
        count = 0

        for item in bckt.list():

            # build local path
            local_path = os.path.join(path, item.key)

            # find local dir and create intermediate dirs
            # if they don't exist
            local_dir = os.path.dirname(local_path)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)

            if not os.path.isdir(local_path):
                with open(local_path, 'w') as local_file:
                    item.get_contents_to_file(local_file)
                    logging.info("copying %s:%s" % (bucket, item.key))
                    count += 1

        if compress:
            tarpath = "%s.tar.gz" % path
            with tarfile.open(tarpath, "w:gz") as tar:
                tar.add(path, arcname=path.split(os.sep)[-1], recursive=True)
            shutil.rmtree(path)
            logging.info('compressed archive and removed working directory')

        logging.info('archived %d files in %s' % (count, bucket))


def main():

    import argparse

    parser = argparse.ArgumentParser(description='Create local archives of one or more S3 buckets')

    parser.add_argument('buckets', metavar='BUCKET', nargs='+',
                        help='buckets to archive')

    parser.add_argument('-k', '--key', dest='s3key', metavar='KEY', action='store',
                        help='S3 key')
    parser.add_argument('-s', '--secret', dest='s3secret', metavar='SECRET', action='store',
                        help='S3 secret key')
    parser.add_argument('-o', '--outputdir', dest='outputdir', metavar='PATH', action='store',
                        help='directory in which the archives will be placed (default is current directory)')
    parser.add_argument('-p', '--prefix', dest='prefix', action='store',
                        help='prefix added to the local bucket directory name (and tar archive if -z)')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        help='verbose output to stdout')
    parser.add_argument('-z', dest='compress', action='store_true',
                        help='compress backup with gzip')

    args = parser.parse_args()

    #
    # configure logging
    #

    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=level)

    #
    # configure output directory
    #

    if args.outputdir:
        outputdir = os.path.expandvars(os.path.expanduser(args.outputdir))
    else:
        outputdir = os.path.abspath(os.path.dirname(__file__))

    if not os.path.exists(outputdir):
        parser.error('output directory does not exist')

    #
    # create archiver and archive each specified bucket
    #

    archiver = S3Archiver(args.s3key, args.s3secret)

    for bucket in args.buckets:

        # create output path
        dirname = "%s%s" % (args.prefix, bucket) if args.prefix else bucket
        path = os.path.join(outputdir, dirname)

        archiver.archive(bucket, path, args.compress)


if __name__ == "__main__":
    main()
