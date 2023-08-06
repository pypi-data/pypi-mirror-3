#!/usr/bin/env python

# Using ionotify we watch our sources of JavaScript in order to know we should
# build when the files change.

import lpjsmin
import pyinotify
import os
import shutil
from convoy.meta import Builder


def copyfile(src, dst):
    """Help copy the original file over to the build location

    This location is based off the customized build_path_callable

    """
    # make sure the directory for it exists
    d = os.path.dirname(dst)
    if not os.path.exists(d):
        os.makedirs(d)
    shutil.copyfile(src, dst)


class YUIBuilder(pyinotify.ProcessEvent):
    """A pyinotify driven file watcher that builds JS files"""
    filters = [
        # ignore test files
        lambda x: x.startswith('test_'),
        # ignore directories
        lambda x: os.path.isdir(x),
        # ignore files that don't end in .js
        lambda x: not x.endswith('.js'),
    ]

    def __init__(self, build_path_callable, build_dir='build',
        meta_jsmodule='CUSTOM_MODULES', update_metajs=True, watch_dir='.'):
        """Build the watcher

        :param build_path_callable: A callable that, given the filename of the
            changed file, will return a new path to locate it in the build
            directory.
        :param build_dir: What directory is the root of the build location.
        :param watch_dir: Where are we watching for file changes, defaults to
            cwd.
        :param update_metajs: Should we update the meta.js file on new files?
        :param meta_jsmodule: What is the var name for the modules processed
            into the meta.js file.

        """
        self.build_path_callable = build_path_callable
        self.build_dir = build_dir
        self.watch_dir = watch_dir
        self.update_metajs = update_metajs
        self.meta_jsmodule = meta_jsmodule

    def process_default(self, event):
        """This implements an API call per the pyinotify Process Event class

        This is common code called for both create and modify events.

        """
        needs_filtering = [f(event.name) for f in self.filters]
        if True in needs_filtering:
            pass
        else:
            new_path = self.build_path_callable(event.pathname,
                    **self.__dict__)
            print "new Path", new_path
            copyfile(event.pathname, new_path)
            lpjsmin.minify(new_path)

            if self.update_metajs and event.mask == pyinotify.IN_CREATE:
                # We now need to update the meta.js file for our new
                # module. We only update it on create since changes to the
                # contents of the file shouldn't change much.
                Builder(
                    name=self.meta_jsmodule,
                    src_dir=os.path.abspath(self.build_dir),
                    output=os.path.join(self.build_dir, 'meta.js'),
                    exclude_regex='-min.js',
                    ext=False,
                    include_skin=False,
                    ).do_build()

    def run(self):
        """Start the watcher with the current settings"""
        print "Watching '%s' for JS changes" % self.watch_dir
        # Instanciate a new WatchManager (will be used to store watches).
        wm = pyinotify.WatchManager()

        # We're watching only modify and create events atm.
        mask = pyinotify.IN_MODIFY | pyinotify.IN_CREATE

        # Associate this WatchManager with a Notifier (will be used to report
        # and process events).
        notifier = pyinotify.Notifier(wm, self)

        # Add a new watch on the watch dir for the events we build in mask.
        wm.add_watch(self.watch_dir, mask, rec=True)
        # Loop forever and handle events.
        notifier.loop()
