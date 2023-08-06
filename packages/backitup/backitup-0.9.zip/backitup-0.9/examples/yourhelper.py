"""Example backup script setup file.
This module is meant to be imported and used via small python
script files invoked via the commandline or a cronjob,
but you can write a commandline wrapper if you want.

Customize this for your needs or just let it inspire you!
"""

import logging

import backitup


# Set up logging so it goes to console.
backitup.log.addHandler(logging.StreamHandler())
backitup.log.addHandler(logging.FileHandler(
    r'C:\Users\<username>\Documents\backups.log'))
backitup.log.setLevel(logging.INFO)


# If you are using AWS, you can set it up here.
awsaccess = '<access key here>'
awssecret = '<secret here>'
awsbucket = '<bucket for your backups>'

# FTP details. As a personal note, Dreamhost shared hosting gives you a
# 'backup user' you can put any personal data on.
ftplogin = 'hanjin.dreamhost.com', 'username', 'password', 'personalbackups'

# Let's make backups locally, may as well.
backupdir = r'C:\Users\<username>\Documents\Backups'
# We can also put them into a self-syncing folder that will upload
# to dropbox, google drive, etc.
backupgdrive = r"C:\Users\<username>\Google Drive\personalbackups"

uploads = [
    backitup.make_upload_s3(awsbucket, awsaccess, awssecret),
    backitup.make_upload_ftp(*ftplogin),
    backitup.make_simplecopy(backupgdrive),
    ]


def run(arcname, *sources):
    """Creates an archive with arcname in the predefined backup folder from
    `sources`, and uploads it to predefined places.
    """
    arcpath = backitup.create_archive(
        sources, backupdir, arcname=arcname, maxbackups=5)
    backitup.upload_all(arcpath, *uploads)
