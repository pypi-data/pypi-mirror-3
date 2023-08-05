from blogofile import __version__
assert __version__ == '0.7.1', \
    "blogodev currently only tested against Blogofile 0.7.1 exactly"

import logging
import os
import sys
import stat
import traceback
import shutil
import tempfile
import time
import argparse
from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions as mako_exceptions

from blogofile.cache import bf
from blogofile import config, site_init, util, server, cache, filter, controller

logging.basicConfig()
logger = logging.getLogger("blogofile")
bf.logger = logger


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--src-dir", dest="src_dir",
                        help="Your site's source directory "
                                 "(default is current directory)",
                        metavar="DIR", default=os.curdir)
    parser.add_argument("-v", "--verbose", dest="verbose",
                                 default=False, action="store_true",
                                 help="Be verbose")
    parser.add_argument("-vv", "--veryverbose", dest="veryverbose",
                                 default=False, action="store_true",
                                 help="Be extra verbose")
    parser.add_argument("PORT", nargs="?", default="8080",
                         help="TCP port to use")
    parser.add_argument("IP_ADDR", nargs="?", default="127.0.0.1",
                         help="IP address to bind to. Defaults to loopback only "
                         "(127.0.0.1). 0.0.0.0 binds to all network interfaces, "
                         "please be careful!")
    args = parser.parse_args()
    return (parser, args)


def main(argv=None, **kwargs):
    parser, args = get_args()

    if args.verbose: #pragma: no cover
        logger.setLevel(logging.INFO)
        logger.info("Setting verbose mode")

    if args.veryverbose: #pragma: no cover
        logger.setLevel(logging.DEBUG)
        logger.info("Setting very verbose mode")

    if not os.path.isdir(args.src_dir): #pragma: no cover
        print("source dir does not exist : %s" % args.src_dir)
        sys.exit(1)
    os.chdir(args.src_dir)

    #The src_dir, which is now the current working directory,
    #should already be on the sys.path, but let's make this explicit:
    sys.path.insert(0, os.curdir)

    config_init(args)

    global output_dir
    output_dir = util.path_join("_site", util.fs_site_path_helper())

    bfserver = server.Server(args.PORT, args.IP_ADDR)
    bfserver.start()
    state = {}
    while not bfserver.is_shutdown:
        try:
            time.sleep(.5)
            _check_output(state)
        except KeyboardInterrupt:
            bfserver.shutdown()
        except:
            print traceback.print_exc()

def config_init(args):
    try:
        config.init("_config.py")
    except config.ConfigNotFoundException: #pragma: no cover
        sys.exit("No configuration found in source dir: {0}".format(args.src_dir))

def _file_mtime(f):
    if not os.path.exists(f):
        return None
    else:
        st = os.stat(f)
        return st[stat.ST_MTIME]

def _check_output(state):
    starting = not(state)
    for src, dest in _walk_files(output_dir, True):
        src_mtime = _file_mtime(src)
        if starting:
            state[src] = src_mtime
        elif src_mtime > state.get(src, 0):
            logger.info("File %s changed since start", src)
            state[src] = src_mtime
            _rebuild()
            break

def _rebuild():
    print("File changes detected, rebuilding...")
    writer = Writer()
    logger.debug("Running user's pre_build() function...")
    config.pre_build()
    try:
        writer.write_site()
        logger.debug("Running user's post_build() function...")
        config.post_build()
    finally:
        logger.debug("Running user's build_finally() function...")
        config.build_finally()

def _walk_files(output_dir, include_src_templates):

    for root, dirs, files in os.walk("."):
        if root.startswith("./"):
            root = root[2:]

        for d in list(dirs):
            #Exclude some dirs
            d_path = util.path_join(root,d)
            if util.should_ignore_path(d_path) and (
                not include_src_templates or 
                not d.startswith('_') or
                d.startswith("_site")
            ):
                dirs.remove(d)

        for t_fn in files:
            t_fn_path = util.path_join(root, t_fn)
            if util.should_ignore_path(t_fn_path):
                #Ignore this file.
                logger.debug("Ignoring file: " + t_fn_path)
                continue
            elif t_fn.endswith(".mako"):
                t_name = t_fn[:-5]
                path = util.path_join(output_dir, root, t_name)
                yield t_fn_path, path
            else:
                f_path = util.path_join(root, t_fn)
                out_path = util.path_join(output_dir, f_path)
                yield f_path, out_path


class Writer(object):

    def __init__(self):
        self.config = config
        #Base templates are templates (usually in ./_templates) that are only
        #referenced by other templates.
        self.base_template_dir = util.path_join(".", "_templates")
        self.output_dir = tempfile.mkdtemp()
        self.template_lookup = TemplateLookup(
                directories=[".", self.base_template_dir],
                input_encoding='utf-8', output_encoding='utf-8',
                encoding_errors='replace')

    def _load_bf_cache(self):
        #Template cache object, used to transfer state to/from each template:
        self.bf = cache.bf
        self.bf.writer = self
        self.bf.logger = logger

    def write_site(self):
        self._load_bf_cache()
        self._init_filters_controllers()
        self._run_controllers()
        self._write_files()
        self._copy_to_site()

    def copyfile(self, src, dest):
        logger.debug("Copying file: " + src)
        shutil.copyfile(src, dest)

    def _copy_to_site(self):
        files_ = []
        self._copytree(self.output_dir, output_dir, files_)
        shutil.rmtree(self.output_dir)
        files_ = set(files_)
        for root, dirs, files in os.walk(output_dir):
            for file_ in files:
                path = os.path.join(root, file_)
                relative_name = path[len(output_dir):]
                if relative_name not in files_:
                    logger.info("Deleting: %s", path)
                    os.remove(path)

    def _copytree(self, src, dst, files_):
        names = os.listdir(src)
        util.mkdir(dst)
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            if os.path.isdir(srcname):
                self._copytree(srcname, dstname, files_)
            else:
                shutil.copy2(srcname, dstname)
            relative_name = os.path.normpath(srcname[len(self.output_dir):])
            files_.append(relative_name)

    def _write_files(self):
        """Write all files for the blog to _site

        Convert all templates to straight HTML
        Copy other non-template files directly"""

        for src, dest in _walk_files(self.output_dir, False):
            if not os.path.exists(os.path.dirname(dest)):
                util.mkdir(os.path.dirname(dest))

            if src.endswith(".mako"):
                #Process this template file
                with open(src) as t_file:
                    template = Template(t_file.read().decode("utf-8"),
                                        output_encoding="utf-8",
                                        lookup=self.template_lookup)
                    #Remember the original path for later when setting context
                    template.bf_meta = {"path":src}

                with self._output_file(dest) as html_file:
                    html = self.template_render(template)
                    #Write to disk
                    html_file.write(html)
            else:
                self.copyfile(src, dest)

    def _init_filters_controllers(self):
        #Run filter/controller defined init methods
        filter.init_filters()
        controller.init_controllers()

    def _run_controllers(self):
        """Run all the controllers in the _controllers directory"""
        controller.run_all()

    def _output_file(self, name):
        return open(name, 'w')

    def template_render(self, template, attrs={}):
        """Render a template"""
        #Create a context object that is fresh for each template render
        self.bf.template_context = cache.Cache(**attrs)
        #Provide the name of the template we are rendering:
        self.bf.template_context.template_name = template.uri
        try:
            #Static pages will have a template.uri like memory:0x1d80a90
            #We conveniently remembered the original path to use instead.
            self.bf.template_context.template_name = template.bf_meta['path']
        except AttributeError:
            pass
        attrs['bf'] = self.bf
        #Provide the template with other user defined namespaces:
        for name, obj in self.bf.config.site.template_vars.items():
            attrs[name] = obj
        try:
            return template.render(**attrs)
        except: #pragma: no cover
            logger.error("Error rendering template")
            print(mako_exceptions.text_error_template().render())
        del self.bf.template_context

    def materialize_template(self, template_name, location, attrs={}):
        """Render a named template with attrs to a location in the _site dir"""
        logger.info("Materialize template: %s", location)
        template = self.template_lookup.get_template(template_name)
        template.output_encoding = "utf-8"
        rendered = self.template_render(template, attrs)
        path = util.path_join(self.output_dir, location)
        #Create the path if it doesn't exist:
        util.mkdir(os.path.split(path)[0])
        with self._output_file(path) as f:
            f.write(rendered)

if __name__ == "__main__":
    main()
