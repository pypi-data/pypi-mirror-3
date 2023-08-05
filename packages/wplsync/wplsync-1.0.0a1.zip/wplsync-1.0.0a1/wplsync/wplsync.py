# (c) 2011 Martin Wendt; see http://wplsync.googlecode.com/
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Synchronize Media Playlists with a target folder.

- ...

- Add reference here
  http://superuser.com/questions/330155/how-to-export-music-files-of-a-playlist-into-one-folder

http://lifehacker.com/231476/alpha-geek-whip-your-mp3-library-into-shape-part-ii-+-album-art

TODO:
- check max path length 256
- print and check max size (16GB)
- sync Album Art "Folder.jpg" or "AlbumArtSmall.jpg". 
  ??? Also display album "AlbumArt_WMID_Large.jpg" or "AlbumArt_WMID_Small.jpg"

  use tid/cid ?
  <media src="..\..\lib\_Vinyl\Violent Femmes\Violent Femmes\07_Violent Femmes_Promise.mp3" 
      cid="{8DD5DDEF-4BDC-42E8-96DA-242A3D006FE9}" 
      tid="{CD14CA62-3D3E-4279-A2ED-6227D72B4EC8}"/>
   
  
- '-i' ignore errors
- '-f' force-update, even if target is newer
- --copy-playlists
- --allow-externals
 
Project home: http://wplsync.googlecode.com/  
"""
from optparse import OptionParser
import os
from fnmatch import fnmatch
from xml.etree import ElementTree as ET
from _version import __version__
import filecmp
import shutil
import time
import sys


DEFAULT_OPTS = {
    # fnmatch patterns (see http://docs.python.org/library/fnmatch.html)
    # Media files that will be synced
    "media_file_patterns": ["*.aif",
                            "*.m3u",
                            "*.m4a",
                            "*.m4p",                            
                            "*.mp3",
                            "*.mpa",
                            "*.oga",
                            "*.ogg",
                            "*.pcast",
                            "*.ra",
                            "*.wav", 
                            "*.wma",
                            ],
    # Other files that will be synced, but removed if target folder is otherwise
    # empty
    "copy_file_patterns": ["Folder.jpg", 
                           "AlbumArtSmall.jpg",
                           ],
    # Temporary files, that can savely be deleted in target folders
    "transient_file_patterns": [".DS_Store",
                                "desktop.ini",
                                "Thumbs.db",
                                ],
}

SYNC_FILE_PATTERNS = DEFAULT_OPTS["media_file_patterns"] + DEFAULT_OPTS["copy_file_patterns"]
PURGE_FILE_PATTERNS = DEFAULT_OPTS["transient_file_patterns"] + DEFAULT_OPTS["copy_file_patterns"]

def create_info_dict():
    res = {"root_folder": None,
           "file_list": [], # relative paths, ordered by scan occurence
           "file_map": {}, # key: rel_path, value: info_dict
           "folder_map": {}, # key: re_path, value: True
           "byte_count": 0,
           "ext_map": {},
           "error_files": [],
           "skip_count": 0,
           "process_count": 0,
           "error_count": 0
          }
    return res


def canonical_path(p, encoding=None):
    res = os.path.normcase(os.path.normpath(os.path.abspath(p)))
    if encoding and not isinstance(res, unicode):
        res = res.decode(encoding)
    return res


def check_path_independent(p1, p2):
    """Return True if p1 and p2 don't overlap."""
    p1 = canonical_path(p1) + "/"
    p2 = canonical_path(p2) + "/"
    return not (p1.startswith(p2) or p2.startswith(p1)) 


def match_pattern(fspec, patterns):
    """Return True, if fspec matches at least on pattern in the list."""
    for pat in patterns:
        if fnmatch(fspec, pat):
            return True
    return False

    
def copy_file(opts, src, dest):
    assert os.path.isfile(src)
    assert not dest.startswith(opts.source_folder) # Never change the source folder
    dir = os.path.dirname(dest)
    if not opts.dry_run:
        if not os.path.exists(dir):
            os.makedirs(dir)
        shutil.copy2(src, dest)
    return

        
def delete_file(opts, fspec):
    assert os.path.isfile(fspec)
    assert opts.delete_orphans
    assert not fspec.startswith(opts.source_folder) # Never change the source folder
    if not opts.dry_run:
        os.remove(fspec)
    return

        
def compare_files(opts, fspec1, fspec2):
    """Compare two files (contains a fix for Windows)."""
    try:
#        source_modified = os.path.getmtime(fspec1)
#        target_modified = os.path.getmtime(fspec2)
#        print "src", time.ctime(source_modified), "target", time.ctime(target_modified), "dif:", target_modified-source_modified
        # FIX for Windows:
        # when using float times, both files my differ by a small value: 
        #    src Sat Oct 22 11:22:27 2011 target Sat Oct 22 11:22:27 2011 dif: 0.0
        #    src Sat Oct 22 11:22:27 2011 target Sat Oct 22 11:22:27 2011 dif: -4.76837158203e-07
        #    src Sat Oct 22 11:22:27 2011 target Sat Oct 22 11:22:27 2011 dif: -9.53674316406e-07
        # even if fspec2 was copied from fspec1 using shutil.copy2(). 
        # This causes filecmp.cmp() to perform a byte comparison even in shallow 
        # mode, which is SLOW.         
        prev = os.stat_float_times()
        os.stat_float_times(False)
        return filecmp.cmp(fspec1, fspec2, shallow=True)
    finally:
        os.stat_float_times(prev)
    return

        
def purge_folders(opts, target_map):
    """Delete all child folders that are empty or only contain transient files."""
    root_folder = target_map["root_folder"]
    assert isinstance(root_folder, unicode)
    assert os.path.isdir(root_folder)
    assert opts.delete_orphans
    assert not root_folder.startswith(opts.source_folder) # Never change the source folder
    if opts.verbose >= 1:
        print "Purge folders in %s ..." % root_folder

    if len(target_map["file_list"]) == 0:
        print("The target folder does not contain media files. "
              "This could result in removing the complete root_folder; aborted.")
        return

    purge_folders = []
    for folder, subfolders, filenames in os.walk(root_folder):
        # Check if this folder contains non-transient files
        can_purge = True
        for filename in filenames:
            if not match_pattern(filename, PURGE_FILE_PATTERNS):
                can_purge = False
                break
        # If ONLY transient files are found, remove them.        
        if can_purge:
            for filename in filenames:
                fspec = os.path.join(folder, filename)
                if match_pattern(filename, PURGE_FILE_PATTERNS):
                    if opts.verbose >= 2:
                        print "Purge transient file %s" % fspec
                    delete_file(opts, fspec)
            # Add this folder to the purge list.
            # (We don't need to do this for parents, since os.removedirs will
            # get them anyway.)
            if len(subfolders) == 0:
                purge_folders.append(folder)
    # Now remove empty leaves and all parents (if they are empty then)
    for folder in purge_folders:
        if opts.verbose >= 1:
            print "Remove empty folder %s" % folder
        assert os.path.isdir(folder)
        assert not folder.startswith(opts.source_folder) # Never change the source folder
        if not opts.dry_run:
            os.removedirs(folder)
    return

        
def add_file_info(opts, info_dict, fspec):
    """Append fspec to info_dict, if it is a valid media file."""
    assert os.path.isabs(fspec)
    assert isinstance(fspec, unicode)

    info_dict["process_count"] += 1
    # Get path relative to the synced folder
    ext = os.path.splitext(fspec)[-1].lower()

    if not os.path.isfile(fspec):
        # Playlist reference cannot be resolved
        info_dict["skip_count"] += 1
        info_dict["error_count"] += 1
        if opts.verbose >= 1:
            print "File not found: '%s'" % fspec
        return False
    
    if not fspec.startswith(info_dict["root_folder"]):
        info_dict["skip_count"] += 1
        if opts.verbose >= 1:
            print "External file (not inside root folder): '%s'" % fspec
        return False
    
    try:
        rel_path = os.path.relpath(fspec, info_dict["root_folder"])
    except:
        # Probably a reference to an external device, like '//diskstation'
        info_dict["skip_count"] += 1
        info_dict["error_count"] += 1
        if opts.verbose >= 1:
            print "Could not make relative path for: '%s'" % fspec
        return False

    # Ignore duplicates
    if rel_path in info_dict["file_map"]:
        info_dict["skip_count"] += 1
        info_dict["error_count"] += 1
        if opts.verbose >= 1:
            print "Duplicate reference for '%s'" % fspec
        return False

    # Skip files with unsupported extensions
    if match_pattern(fspec, SYNC_FILE_PATTERNS):
        info_dict["ext_map"][ext] = False
    else:
        info_dict["ext_map"][ext] = True
        info_dict["skip_count"] += 1
        if opts.verbose >= 3:
            print "Skipping %s" % fspec
        return False

    # Copy media files (and album art, ...)
    size = os.path.getsize(fspec)
    info_dict["byte_count"] += size
    info = {"fspec": fspec,
            "rel_path": rel_path,
            "size": size,
#            "modified": os.path.getmtime(fspec),
#            "created": os.path.getctime(fspec),
            }
    info_dict["file_map"][rel_path] = info
    # Maintain a list in addition to the map, so we can keep the scan order
    info_dict["file_list"].append(rel_path)
    return True


def read_folder_files(opts, folder_path):
    assert isinstance(folder_path, unicode)
    if opts.verbose >= 1:
        print 'Reading folder "%s" ...' % (folder_path, )
    res = create_info_dict()
    res["root_folder"] = folder_path

    for dirname, _dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            fspec = os.path.join(dirname, filename)
            add_file_info(opts, res, fspec)
    return res


def read_playlist_wpl(opts, playlist_path, info):
    """Read a WPL playlist and add file info to dictionary."""
    # TODO: this assert may be removed
    assert playlist_path.startswith(opts.source_folder)
    assert os.path.isabs(playlist_path)
    
    if opts.verbose >= 1:
        print 'Parsing playlist "%s" ...' % (playlist_path, )
    tree = ET.parse(playlist_path)
    
    try:
        generator  = tree.find("head/meta[@name='Generator']").attrib["content"]
    except SyntaxError:
        generator  = None # requires ElementTree 1.3+
    title = tree.find('head/title').text
    if opts.verbose >= 1:
        print 'Scanning playlist "%s" (%s)...' % (title, generator)
    playlist_folder = os.path.dirname(playlist_path)
    for media in tree.find("body/seq"):
        fspec = media.attrib["src"]
        # If the fspec was given relative, it is relative to the playlist
        if not os.path.isabs(fspec):
            fspec = os.path.join(playlist_folder, fspec)
            fspec = canonical_path(fspec, "UTF-8")
        add_file_info(opts, info, fspec)
    # TODO: faster sequential approach:
    # iparse = ET.iterparse(playlist_path, ["end", ])
    # for event, elem in iparse:
    #     if event == "end" and elem.tag == "media":
    #         print elem.attrib["src"]
    return


def read_source_files(opts):
    """Read source files (either complete folder or using given playlists)."""
    if len(opts.playlist_paths) == 0:
        return read_folder_files(opts, opts.source_folder)
    res = create_info_dict()
    res["root_folder"] = opts.source_folder
    for pl in opts.playlist_paths:
        ext = os.path.splitext(pl)[-1].lower()
        if ext == ".wpl":
            read_playlist_wpl(opts, pl, res)
        else:
            raise NotImplementedError("Unsupported playlist extension: %r" % ext)
    return res


def sync_file_lists(opts, source_map, target_map):
    """Unify leading spaces and tabs and strip trailing whitespace.
    
    """
    # Pass 1: find and delete orphans
    # (before copying, so target space will be freed up)
    orphans = []
    for rel_path, target_info in target_map["file_map"].iteritems():
        src_info = source_map["file_map"].get(rel_path)
        if not src_info:
            orphans.append(target_info)

    if opts.delete_orphans:
        for o in orphans:
            fspec = o["fspec"]
            if opts.verbose >= 2:
                print 'DELETE: %s' % fspec
            delete_file(opts, fspec)

    # Pass 2: copy files
    identical_count = 0
    modified_count = 0
    new_count = 0
    for rel_path in source_map["file_list"]:
        src_info = source_map["file_map"][rel_path]
        target_info = target_map["file_map"].get(rel_path)
        if target_info:
            if compare_files(opts, src_info["fspec"], target_info["fspec"]):
                # Identical
                identical_count += 1
                if opts.verbose >= 3:
                    print 'UNCHANGED: %s' % rel_path
            else:
                # Modified
                modified_count += 1
                if opts.verbose >= 2:
                    print 'UPDATE: %s' % rel_path
                # Copy with file dates
                copy_file(opts, src_info["fspec"], target_info["fspec"])
        else:
            # New
            new_count += 1
            if opts.verbose >= 2:
                print 'CREATE: %s' % rel_path
            target_fspec = os.path.join(opts.target_folder, rel_path)
            copy_file(opts, src_info["fspec"], target_fspec)

    if opts.verbose >= 1:
        print('Synchronized %s files. Created: %s, updated: %s, deleted: %s, unchanged: %s.' 
              % (len(source_map["file_map"]), new_count, modified_count, len(orphans), identical_count))

    # Pass 3: purge empty folders
    if opts.delete_orphans:
        purge_folders(opts, target_map)

    return


def run():
    # Create option parser for common and custom options
    parser = OptionParser(prog="wplsync", # Otherwise 'wplsync-script.py' gets displayed on windows
                          version=__version__,
                          usage="usage: %prog [options] SOURCE_FOLDER TARGET_FOLDER [PLAYLIST [, PLAYLIST...]]",
                          description="Synchronize two media folders, optionally filtered by playlists.",
                          epilog="See also http://wplsync.googlecode.com")

    parser.add_option("-x", "--execute",
                      action="store_false", dest="dry_run", default=True,
                      help="turn off the dry-run mode (which is ON by default), " 
                      "that would just print status messages but does not change "
                      "anything")
    parser.add_option("-q", "--quiet",
                      action="store_const", const=0, dest="verbose", 
                      help="don't print status messages to stdout (verbosity 0)")
    parser.add_option("-v", "--verbose",
                      action="count", dest="verbose", default=1,
                      help="increment verbosity to 2 (use -vv for 3, ...)")
#    parser.add_option("", "--ignore-errors",
#                      action="store_true", dest="ignoreErrors", default=False,
#                      help="ignore errors during processing")
#    parser.add_option("-c", "--copy-playlists",
#                      action="store_true", dest="copy_playlists", default=False,
#                      help="also copy all playlists that are passed as arguments")
    parser.add_option("-d", "--delete",
                      action="store_true", dest="delete_orphans", default=False,
                      help="delete target files that don't exist in PLAYLIST")
#    parser.add_option("-e", "--allow-externals",
#                      action="store_true", dest="include_externals", default=False,
#                      help="allow source files outside SOURCE_FOLDER and copy them to TAGRGET_FOLDER/external. "
#                      "Note that the target playlists may not work as axpected in this case.")
    
    # Parse command line
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("missing required SOURCE_FOLDER")
    elif len(args) < 2:
        parser.error("missing required TARGET_FOLDER")
    elif not os.path.isdir(args[0]):
        parser.error("SOURCE_FOLDER must be a folder")
    elif not os.path.isdir(args[1]):
        parser.error("TARGET_FOLDER must be a folder")

    options.source_folder = canonical_path(args[0], sys.getfilesystemencoding())
    options.target_folder = canonical_path(args[1], sys.getfilesystemencoding())

    if not check_path_independent(options.source_folder, options.target_folder):
        parser.error("SOURCE_FOLDER and TARGET_FOLDER must not overlap")

    options.playlist_paths = []
    for pl in args[2:]:
        pl = canonical_path(pl)
        if not os.path.isfile(pl):
            parser.error("'%s' must be a playlist file" % pl)
        options.playlist_paths.append(pl)

    start_time = time.time()
    try:
        # Call processor
        source_info = read_source_files(options)
        target_info = read_folder_files(options, options.target_folder)

        if options.verbose >= 1:
            print "Source: %s files, %s valid in %s folders." % (source_info["process_count"],
                                                  len(source_info["file_map"]),
                                                  len(source_info["folder_map"])
                                                  )
            if options.verbose >= 3:
                ext_list = sorted(source_info["ext_map"].keys())
                print "    Extensions: %s" % ext_list
            print "Target: %s files, %s valid in %s folders." % (target_info["process_count"],
                                                  len(target_info["file_map"]),
                                                  len(target_info["folder_map"])
                                                  )
        sync_file_lists(options, source_info, target_info)
    except KeyboardInterrupt:
        print >>sys.stderr, "Interrupted!"

    if options.verbose >= 1:
        print "Elapsed: %.2f seconds." % (time.time() - start_time)
    if options.dry_run and options.verbose >= 1:
        print("\n*** Dry-run mode: no files have been modified!\n"
              "*** Use -x or --execute to process files.")


if __name__ == "__main__":
    run()
