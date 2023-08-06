jsautobuild documentation
==========================

This is meant to be used to help you write your own watching js builder
script. It provides the hooks and the pyinotify inclusion. You can tweak it to
your own specific application as required.

Usage
------
You need to build a simple script to use the builder. Below is an example
script that helps copy changed JS files to a build directory.

::

    import os

    from jsautobuild import YUIBuilder


    def lp_path_builder(changed_path, **builder_props):
        """The custom bit of LP code that determines where files get moved to"""
        # to start out let's assume your CWD is where we're referencing things from
        CWD = os.getcwd()
        JSDIR = os.path.join(CWD, builder_props['build_dir'])
        RENAME = re.compile("^.*lib/lp/(.*)/javascript")

        match = RENAME.search(changed_path)
        js_dir = match.groups()[0]
        return os.path.join(JSDIR, RENAME.sub(js_dir, changed_path))


    if __name__ == "__main__":
        build_dir = 'build/js/lp'
        meta_name = 'LP_MODULES'
        watch_dir = 'lib'

        builder = YUIBuilder(lp_path_builder,
                build_dir,
                watch_dir=watch_dir,
                meta_jsmodule=meta_name)

        builder.run()

Options
-------
:build_callable:
You need a function that will accept the filename of the JS file that has
changed, and then return back the proper location of that file in the build
directory.

:build_dir:
What is the root directory all build files are heading to. This is also used
for the meta.js generate code. It'll build a list of all modules in this build
directory.

:meta_jsmodule:
What is the Javascript global variable name you want the meta file to be
generated to. You'll use this in your own application to feed the module list
to the YUI combo loader.

:update_metajs:
**default True**
Should we rebuild the meta.js whenever a new .js file is created.

:watch_dir:
**default .**
This is the directory that is watched for all file changes and triggers the
build of js files. By default it'll watch the current working directory and
anything below that.
