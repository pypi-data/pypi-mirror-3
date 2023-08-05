# This file is part of beets.
# Copyright 2011, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Synchronizes metadata with MusicBrainz based on MBIDs.
"""
import logging
from beets.plugins import BeetsPlugin
from beets import ui
from beets.ui import commands
from beets.autotag import mb

log = logging.getLogger('beets')

def _apply_album():
    xxx

def mbsync(lib):
    # Albums.
    for album in lib.albums():
        if album.mb_albumid:
            newinfo = mb.album_for_id(album.mb_albumid)
            if not newinfo:
                log.warn(u'no match for album %s - %s (%s)' %
                         (album.albumartist, album.album, album.mb_albumid))
                continue

class InfoPlugin(BeetsPlugin):
    def commands(self):
        cmd = ui.Subcommand('mbsync', help='synchronize data with MusicBrainz')
        def func(lib, config, opts, args):
            if args:
                raise ui.UserError('command takes no arguments')
            mbsync(lib)
        cmd.func = func
        return [cmd]
