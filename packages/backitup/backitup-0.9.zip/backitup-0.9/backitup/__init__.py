import datetime
import fnmatch
import ftplib
import itertools
import logging
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import zipfile


# Corresponds to allowZip64 default.
ALLOWZIP64 = False
# Maximum number of files to keep in the backup directory.
MAXBACKUPS = 10
# Name of the archive. Change
ARCNAME = 'backup.zip'
MYSQLDUMP = 'mysqldump'
EXCLUDES = '*/.*', '*.pyc'
INCLUDES = '*.htaccess',


log = logging.getLogger('backitup')


def _get_files(path, excludes, includes):
    def isincluded(p):
        p = p.replace('\\', '/')
        for pat in includes:
            if fnmatch.fnmatch(p, pat):
                return True
        for pat in excludes:
            if fnmatch.fnmatch(p, pat):
                return False
        return True
    path = os.path.abspath(path)
    if os.path.isfile(path):
        if isincluded(path):
            return [path]
        return []
    paths = []
    for folder, subs, files in os.walk(path):
        for f in files:
            fullpath = os.path.join(folder, f)
            if isincluded(fullpath):
                paths.append(fullpath)
    return paths


def _timestamped_path(backupdir, arcname):
    """Given a backup folder and archive name, return
    <backupdir>/<arcname basename>_<timestamp>.<archname ext>
    """
    stamp = time.strftime('_%y-%m-%d_%H.%M.%S', time.gmtime())
    head, ext = os.path.splitext(arcname)
    return os.path.join(backupdir, head + stamp + ext)


def _prune_backups(backupdir, maxbackups):
    """Deletes old backups (age determined by filename) from the backup
    directory, so that the remaining number is less than
    maxbackups.

    Will raise if maxbackups is 0 or less, or on failure to remove any
    backup file.
    """
    if maxbackups < 1:
        raise ValueError('maxbackups must be 1 or more, got %s.' % maxbackups)
    try:
        files = os.listdir(backupdir)
    except OSError:
        log.info('No backup dir found, creating.')
        os.mkdir(backupdir)
        return
    if len(files) <= maxbackups:
        log.info('No need to delete any backups.')
        return
    files = list(reversed(sorted(files)))
    toremove = files[maxbackups - 1:]
    log.info('Removing the following backup files: %s', toremove)
    for f in toremove:
        fullpath = os.path.join(backupdir, f)
        os.chmod(fullpath, stat.S_IWRITE)
        os.remove(fullpath)


def _cleanpath(s):
    """Normalizes a path."""
    return s.lower().replace('\\', '/').strip('/')


def _get_relpath_and_size(abspath):
    """Returns a tuple (drive-less abspath, size of file at abspath)."""
    fn = _cleanpath(os.path.splitdrive(abspath)[1])
    return fn, os.path.getsize(abspath)


def _ensure_validity(z):
    """Runs z.testzip and checks result. May be expanded in the future.
    """
    badfile = z.testzip()
    if badfile:
        raise RuntimeError('Bad file found in archive: %s' % badfile)


def _log_zipinfo(info):
    log.debug('Info for   %s:', info.filename)
    log.debug('Comment:   %s', info.comment)
    log.debug('Modified:  %s', datetime.datetime(*info.date_time))
    log.debug('System:    %s %s', info.create_system, '(0 = Windows, 3 = Unix)')
    log.debug('ZIP ver:   %s', info.create_version)
    log.debug('CmpSize:   %s', info.compress_size, 'bytes')
    log.debug('UnCmpSize: %s', info.file_size, 'bytes')


def create_archive(backupdir,
                   srcpaths=(),
                   maxbackups=MAXBACKUPS,
                   more_backups=(),
                   arcname=ARCNAME,
                   excludes=EXCLUDES,
                   includes=INCLUDES,
                   allow_zip_64=ALLOWZIP64):
    """Creates the backup archive.

    :param backupdir: Folder to place the resulting backup.
    :param srcpaths: Paths to files or folders that contain the files to back
      up. Will scan folders recursively.
    :param excludes: Wildcard match strings. Anything that matches any
      pattern in excludes will not be included in the final archive,
      **unless** it matches a pattern in `includes`.
    :param includes: Wildcard match strings. Anything that matches
      any pattern in includes will *always* be included in the final
      archive, even if it matches a pattern in `excludes`.
    :param arcname: Name of the archive (such as 'weeklybackup.zip'),
      which must include the extension.
    :param allow_zip_64: Corresponds to ZipFile's allowZip64.
    :param more_backups: Collection of callables that will
      be invoked with the ZipFile object, after the main
      compression has run. This allows additional steps to
      run, which may generate and archive their own files.
      Mostly useful for backing up data that needs to be
      created on-the-fly, such as sql dumps.
    """
    _prune_backups(backupdir, maxbackups)
    getfiles = lambda p: _get_files(p, excludes, includes)
    allpaths = list(itertools.chain(*map(getfiles, srcpaths)))
    if srcpaths and not allpaths:
        raise RuntimeError('No files found to archive.')
    arcpath = _timestamped_path(backupdir, arcname)
    log.info('Writing %s files to %s', len(allpaths), arcpath)
    z = zipfile.ZipFile(arcpath, 'w', zipfile.ZIP_DEFLATED, allow_zip_64)
    for p in allpaths:
        z.write(p)
    for func in more_backups:
        func(z)
    z.close()
    log.info('Archive complete (%s bytes), finishing up.', os.path.getsize(arcpath))
    z = zipfile.ZipFile(arcpath, allowZip64=allow_zip_64)
    map(_log_zipinfo, z.infolist())
    os.chmod(arcpath, stat.S_IREAD)
    _ensure_validity(z)
    z.close()
    log.info('Archive valid and read-only.')
    return arcpath


def make_backup_mysql(user, password, database, dumpexe=MYSQLDUMP, host='localhost'):
    if not os.path.exists(dumpexe):
        raise RuntimeError('%r does not exist.' % dumpexe)
    def backup_mysql(z):
        # There's a race condition here I'm happily ignoring.
        sqlpath = _timestamped_path(tempfile.gettempdir(), database + '.sql')
        args = [dumpexe,
                '--host=' + host,
                '--user=' + user,
                '--password=' + password,
                '--result-file=' + sqlpath,
                database]
        log.info('Backing up MySQL: %s', args)
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.communicate()
        log.info('Writing sql dump to zip file.')
        z.write(sqlpath)
        os.remove(sqlpath)
        log.info('Removed temp sql dump file.')
    return backup_mysql


def make_upload_ftp(host='', user='', passwd='', cwd=None):
    def upload(arcpath):
        log.info('FTP: Uploading to %s:%s@%s: %s', user, passwd, host, arcpath)
        ftp = ftplib.FTP(host)
        ftp.login(user, passwd)
        if cwd:
            ftp.cwd(cwd)
        ftp.storbinary("STOR " + arcpath, open(arcpath, "rb"))
        log.info('FTP: Upload finished.')
    return upload


#noinspection PyUnresolvedReferences
def make_upload_s3(bucket_name, aws_access_key_id, aws_secret_access_key):
    import boto
    from boto.s3.key import Key
    def upload(arcpath):
        log.info('S3: Uploading %s to bucket %s.', arcpath, bucket_name)
        # connect to the bucket
        conn = boto.connect_s3(aws_access_key_id, aws_secret_access_key)
        bucket = conn.get_bucket(bucket_name)
        # create a key to keep track of our file in the storage
        k = Key(bucket)
        k.key = os.path.basename(arcpath)
        k.set_contents_from_filename(arcpath)
        log.info('S3: Upload finished.')
    return upload


def make_simplecopy(dest):
    def copy(arcpath):
        log.info('Copy: %s to %s', arcpath, dest)
        shutil.copy(arcpath, dest)
        log.info('Copy: Finished.')
    return copy


def upload_all(arcpath, *uploads):
    log.info('Uploading %s to %s places.', arcpath, len(uploads))
    errs = []
    def upload(up):
        try:
            up(arcpath)
        except Exception:
            log.error(traceback.format_exc())
            errs.append(sys.exc_info())
    threads = []
    for u in uploads:
        t = threading.Thread(target=upload, args=[u])
        t.start()
        threads.append(t)
    map(threading.Thread.join, threads)
    if errs:
        firsterr = errs[0]
        raise firsterr[0], firsterr[1], firsterr[2]
