##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Merge from one fssync repository to another

This differs from merging from Zope in that changes from the source
are not considered changes to the orginal.
"""
import os
import os.path
import shutil

import zope.fssync.fsutil
import zope.fssync.copier

class MergeCopier(zope.fssync.copier.ObjectCopier):
    """
    Copies from a checkout to another checkout, but doesn't add sync
    entries in the destination checkout, since they should already be
    present.
    """

    def copy(self, source, target, children=True):
        if os.path.isdir(source):
            shutil.copymode(source, target)
            self.addEntry(source, target)
        else:
            shutil.copy(source, target)
            self.addEntry(source, target)

    def _copyspecials(self, source, target, getwhat):
        src = getwhat(source)
        if os.path.isdir(src):
            dst = getwhat(target)
            zope.fssync.fsutil.ensuredir(dst)
            copier = MergeCopier(self.sync)
            for name in self.sync.metadata.getnames(src):
                copier.copy(os.path.join(src, name), os.path.join(dst, name))
            self.sync.metadata.flush()

    def _syncadd(self, target, type, factory):
        pass


def same_type(path1, path2):
    if (os.path.isfile(path1) == os.path.isfile(path2) or
        os.path.isdir(path1) == os.path.isdir(path2)):
        return True
    return False

def same_file(path1, path2):
    chunk_size = 32768
    f1 = open(path1)
    f2 = open(path2)
    while True:
        s1 = f1.read(chunk_size)
        s2 = f2.read(chunk_size)
        if s1 != s2:
            return False
        if not s1:
            break
    f1.close()
    f2.close()
    return True

def same_entries(path1, path2, metadata):
    names1 = metadata.getnames(path1)
    names2 = metadata.getnames(path2)
    if names1 != names2:
        return False
    for name in names1:
        f1 = os.path.join(path1, name)
        f2 = os.path.join(path2, name)
        if not same_file(f1, f2):
            return False
    return True

def same_specials(path1, path2, metadata):
    extra1 = zope.fssync.fsutil.getextra(path1)
    extra2 = zope.fssync.fsutil.getextra(path2)
    if os.path.exists(extra1) != os.path.exists(extra2):
        return False
    if os.path.exists(extra1) and os.path.exists(extra2):
        if not same_entries(extra1, extra2, metadata):
            return False

    annotations1 = zope.fssync.fsutil.getannotations(path1)
    annotations2 = zope.fssync.fsutil.getannotations(path2)
    if os.path.exists(annotations1) != os.path.exists(annotations2):
        return False
    if os.path.exists(annotations1) and os.path.exists(annotations2):
        if not same_entries(annotations1, annotations2, metadata):
            return False

    return True



def merge(source, target, sync):
    """
    Merge difference from source into target. Treat differences as
    local changes in target. Don't delete anything from target, only
    add things from source. Only merge stuff from target if it is
    actually in the repository (thus don't copy temp files, svn files,
    etc.)
    """
    metadata = sync.metadata
    object_copier = zope.fssync.copier.ObjectCopier(sync)
    merge_copier = MergeCopier(sync)

    for root, dirs, files in os.walk(source):
        if '@@Zope' in dirs:
            dirs.remove('@@Zope')
        for filename in ([''] + files):
            source_path = os.path.join(root, filename)
            if metadata.getentry(source_path):
                directory = root[len(source) + 1:]
                target_path = os.path.join(target, directory, filename)
                if not metadata.getentry(target_path):
                    object_copier.copy(source_path, target_path, False)
                elif not same_type(source_path, target_path):
                    print 'C %s' % target_path
                    metadata.getentry(target_path)['conflict'] = True
                    metadata.flush()
                elif os.path.isfile(source_path):
                    if (not same_file(source_path, target_path) or
                        not same_specials(source_path, target_path, metadata)):
                        print 'M %s' % target_path
                        merge_copier.copy(source_path, target_path, False)
                elif os.path.isdir(source_path):
                    if not same_specials(source_path, target_path, metadata):
                        print 'M %s' % target_path
                        merge_copier.copy(source_path, target_path, False)
