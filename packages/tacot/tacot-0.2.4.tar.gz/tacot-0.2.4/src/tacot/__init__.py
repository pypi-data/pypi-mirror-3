# -*- coding: utf-8 -*-
import os, glob, shutil
import time
import fnmatch
import codecs
import argparse
from StringIO import StringIO

from mako.template import Template
from mako.lookup import TemplateLookup

from tacot.manifest import Manifest, findall

def load_ignore(path):
    patterns = []
    if os.path.exists(path):
        f = open(path, "r")
        for line in f:
            line = line.strip()
            if line:
                patterns.append(line)

        f.close()

    return patterns

def get_files_to_process(root_path, ignore):
    ignore.patterns.append('.*')
    root_path_len = len(root_path)
    for abs_path, dirnames, filenames in os.walk(root_path):
        relative_path = abs_path[root_path_len:].strip('/')
        for f in filenames:
            abs_file_path = os.path.join(abs_path, f)
            relative_file_path = os.path.join(relative_path, f)

            if not ignore.is_match(abs_file_path, relative_file_path):
                yield p

class RootPath(object):
    def __init__(self, root_path):
        self.root_path = [root_path.strip("/")]
        if self.root_path[0] == '.':
            self.root_path = []

    def __call__(self, path):
        return "/".join(self.root_path + [path.lstrip("/")])

def file_to_process_iter(root_path, manifest_file_path):
    manifest = Manifest()
    manifest.findall(root_path.rstrip('/') + '/')

    if os.path.exists(manifest_file_path):
        manifest.read_template(unicode(manifest_file_path))
    else:
        manifest.read_template(StringIO("global-include *\nprune _build/\nprune includes/\nexclude .manifest"))

    return manifest.files

LAST_MTIME = 0

def files_changed(root_path, build_path):
    """Return True if the files have changed since the last check"""

    def file_times():
        """Return the last time files have been modified"""
        current_folder = None
        for file in findall(root_path):
            p = os.path.join(root_path, file.lstrip("/"))
            if p.startswith(build_path):
                continue

            if os.path.dirname(p) != current_folder:
                current_folder = p
                yield os.stat(os.path.dirname(p)).st_mtime

            yield os.stat(p).st_mtime

    global LAST_MTIME
    mtime = max(file_times())
    if mtime > LAST_MTIME:
        LAST_MTIME = mtime
        return True
    return False

def process(root_path, build_path, manifest_file_path):
    template_lookup = TemplateLookup(directories=[root_path], output_encoding='utf-8', encoding_errors='replace')

    print("Please wait, tacot process files :\n")
    for source_filepath in file_to_process_iter(root_path, manifest_file_path):
        dest_filepath = os.path.join(build_path, source_filepath)
        print(source_filepath)

        if not os.path.exists(os.path.dirname(dest_filepath)):
            os.makedirs(os.path.dirname(dest_filepath))

        if fnmatch.fnmatch(source_filepath, "*.html"):
            f = codecs.open(source_filepath, "r", "utf8")
            data = f.read()
            f.close()
            t = Template(data, lookup=template_lookup, uri=source_filepath)
            f = codecs.open(dest_filepath, "w", "utf8")
            f.write(t.render_unicode(
                root_path=RootPath(os.path.relpath(root_path, os.path.dirname(source_filepath))),
                current_page=source_filepath,
                g=type("Global", (object,), {})
            ))
            f.close()
        else:
            shutil.copy(source_filepath, dest_filepath)

def main():
    parser = argparse.ArgumentParser(
        description="""A tool to generate a static web site, with Mako templates."""
    )
    parser.add_argument(
        dest="path", nargs="?", default=os.getcwd(),
        help="""Path where to find the content files"""
    )
    parser.add_argument(
        "-o", "--output", 
        dest="output", default=os.path.join(os.getcwd(), "_build"),
        help="""Where to output the generated files. If not specified, a directory """
             """will be created, named "_build" in the current path (_build by default)."""
    )
    parser.add_argument(
        "-m", "--manifest",
        dest="manifest", default='.manifest',
        help="""Manifest config file (.manifest by default)"""
    )
    parser.add_argument(
        "-r", "--autoreload", 
        dest="autoreload", action="store_true",
        help="Relaunch tacot each time a modification occurs on the content files"
    )

    options = parser.parse_args()

    root_path = options.path
    build_path = options.output
    manifest_file_path = os.path.join(options.path, options.manifest)

    if options.autoreload:
        while True:
            try:
                if files_changed(root_path, build_path):
                    process(
                        root_path,
                        build_path,
                        manifest_file_path
                    )
                    
                time.sleep(.5)  # sleep to avoid cpu load
            except KeyboardInterrupt:
                break

    else:
        process(
            root_path,
            build_path,
            manifest_file_path
        )
