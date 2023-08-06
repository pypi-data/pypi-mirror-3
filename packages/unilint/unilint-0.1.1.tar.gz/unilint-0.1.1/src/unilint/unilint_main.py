from __future__ import print_function
import os
from optparse import OptionParser

from unilint.__version__ import VERSION
from unilint.common import UnilintException
from unilint.unilint_plugin import UnilintPluginInitException
from unilint.custom_format import FLAGS, print_formatted

from unilint.common import run_shell_command

PLUGINS = {}
FORMATTERS = {}

LEVEL_ALL = "all"
LEVEL_STYLE = "style"
LEVEL_WARNING = "warning"
LEVEL_ERROR = "error"

LEVELS = {LEVEL_ALL: 0, LEVEL_STYLE: 10, LEVEL_WARNING: 20, LEVEL_ERROR: 30}


def register_formatter(f_id, formatter_function):
    FORMATTERS[f_id] = formatter_function


def register_plugin(plugin):
    pid = plugin.get_id()
    if pid is None or pid == '':
        raise UnilintException('Invalid plugin id %s'%(pid))
    PLUGINS[pid] = plugin


def extend_maybe(some_container, other_container):
    """extends list or dict with list values with other list or dict unless other is None"""
    if other_container is not None:
        if type(some_container) == dict:
            for key, val in other_container.items():
                if key in some_container:
                    some_container[key].extend(val)
                else:
                    some_container[key] = val
        else:
            some_container.extend(other_container)


def resolve_plugins(selected_plugins_string, deselected_plugins_string, quiet=False):
    """
    Takes in a comma separated String or none, returns a dict str->plugin_instance
    """
    result_plugin_ids = []
    if selected_plugins_string is not None and selected_plugins_string != '':
        selected_plugins_ids = selected_plugins_string.split(',')

        for plugin_id in selected_plugins_ids:
            if plugin_id.strip()=='':
                continue
            if not plugin_id in PLUGINS:
                raise UnilintException('Unknown plugin: %s'%plugin_id)
            result_plugin_ids.append(plugin_id)
    else:
        deselected_plugins_ids = []
        if deselected_plugins_string is not None:
            deselected_plugins_ids = deselected_plugins_string.split(',')

        for plugin_id in PLUGINS:
            if (plugin_id not in deselected_plugins_ids
                and PLUGINS[plugin_id].is_enabled_by_default()):
                result_plugin_ids.append(plugin_id)

    dependencies = []
    for plugin_id in result_plugin_ids:
        deps = PLUGINS[plugin_id].get_depends()
        if deps is not None:
            for dep in deps:
                if not dep in PLUGINS:
                    raise UnilintException('Unknown plugin dependency: %s of %s'%(dep, plugin_id))
                if not dep in result_plugin_ids and not dep in dependencies:
                    dependencies.append(dep)
    for dep_id in dependencies:
        result_plugin_ids.append(dep_id)

    selected_plugins = {}
    for plugin_id in result_plugin_ids:
        try:
            selected_plugins[plugin_id] = PLUGINS[plugin_id](run_shell_command)
        except UnilintPluginInitException as upie:
            if not quiet:
                print("plugin %s failed to activate: %s"%(plugin_id, str(upie)))
    return selected_plugins


def print_issues(options, issues, path):
    if options.formatter is not None:
        FORMATTERS[options.formatter](options, issues, path)
    elif options.format is not None:
        print_formatted(options.format, issues, path)


def order_issues(issues):
    def keyfun(iss):
        return "%s%s"%(iss.path, str(iss.line_number_start).rjust(5, '0'))
    return sorted(issues, key=keyfun)


def check_path(path, basepath, options, subdirs=None, files=None, cleared_paths=None, is_folder=True):
    issues = []
    categorized_resources = {}
    if cleared_paths is None:
        cleared_paths = {}

    for plugin_id in options.selected_plugins:
        new_categories = options.selected_plugins[plugin_id].categorize_type(options, path, subdirs, files)
        extend_maybe(categorized_resources, new_categories)

    for resource, categories in categorized_resources.items():
        if 'generated' in categories:
            if not options.check_generated:
                continue
        if 'test' in categories:
            if not options.check_tests:
                continue
        if options.debug:
            print("processing: %s as %s"%(resource, categories))
        for plugin_id in options.selected_plugins:
            result = options.selected_plugins[plugin_id].check_resource(options, resource, categories)
            extend_maybe(issues, result)
            if result is not None and is_folder:
                if not plugin_id in cleared_paths:
                    cleared_paths[plugin_id] = [path]
                else:
                    cleared_paths[plugin_id].append(path)
            if result is not None and not options.ordered and not options.raw:
                # get the output to the user as quickly as possible
                print_issues(options, result, basepath)
    return issues, cleared_paths


def run_cmd(path, options, args):
    if options.show_plugins is True:
        print('\n'.join(PLUGINS.keys()))
        return 0

    if options.version:
        options.selected_plugins = resolve_plugins(options.selected_plugins,
                                                   options.deselected_plugins,
                                                   quiet=True)

        print("unilint %s"%(VERSION))
        for _, plugin in options.selected_plugins.items():
            meta = plugin.get_meta_information()
            if meta is not None and meta != '':
                print(meta)
        return 0

    options.selected_plugins = resolve_plugins(options.selected_plugins,
                                               options.deselected_plugins)

    if options.debug:
        print('linting from %s'%path)
        print('Activated plugins %s'%options.selected_plugins.keys())

    if len(PLUGINS) == 0:
        raise UnilintException('No plugins registered with unilint')

    if path is None:
        if len(args) == 0:
            raise UnilintException('Unable to use cwd as path')
        else:
            raise UnilintException('Unable to run on %s'%args[0])

    if os.path.isdir(path):
        issues = []
        ignoreddirs = []
        cleared_paths = {} # stores for each plugin the parent folders this plugin is done with

        for (parentdir, subdirs, files) in os.walk(path):

            if os.path.basename(parentdir) in ['build', '.svn', 'CVS', '.hg', '.git']:
                # inserting, to make string search faster
                ignoreddirs.insert(0, parentdir)
                continue
            if 'egg-info' in parentdir:
                # inserting, to make string search faster
                ignoreddirs.insert(0, parentdir)
                continue

            ignore = False
            for ignored in ignoreddirs:
                if parentdir.startswith(ignored):
                    ignore = True
                    break
            if ignore is True:
                continue
            if len(files) == 0 and len(subdirs)==0:
                continue

            new_issues, cleared_paths = check_path(parentdir, path, options, subdirs, files, cleared_paths=cleared_paths)
            if not options.raw:
                extend_maybe(issues, new_issues)
                if options.ordered:
                    dir_issues = order_issues(new_issues)
                    print_issues(options, dir_issues, path)
    else:
        # is file
        issues, _ = check_path(path, os.path.dirname(path), options=options, is_folder=False)
        print_issues(options, issues, path)

    return 0


def get_unilint_parser(usage):
    parser = OptionParser(usage=usage)
    parser.add_option("-v", "--verbose", dest="verbose", default=False,
                      help="verbose output.",
                      action="store_true")
    parser.add_option("--version", dest="version", default=False,
                      help="print version and meta information",
                      action="store_true")
    parser.add_option("--debug", dest="debug", default=False,
                      help="debug output.",
                      action="store_true")
    parser.add_option("-l", "--level", dest="level", default=LEVEL_ERROR,
                      help="A number or one of %s."%(','.join(["%s(=%s)"%(k, v) for k, v in LEVELS.items()])),
                      action="store")
    parser.add_option("-p", "--plugins", dest="show_plugins", default=False,
                      help="List Available plugins",
                      action="store_true")
    parser.add_option("-s", "--select-plugins", dest="selected_plugins", default=None,
                      help="Choose plugins by comma separated id, all others deselected",
                      action="store")
    parser.add_option("-d", "--deselect-plugins", dest="deselected_plugins", default=None,
                      help="Choose plugins by comma separated id, ignored with --select-plugins",
                      action="store")
    parser.add_option("-t", "--tests", dest="check_tests", default=False,
                      help="Also check unit tests",
                      action="store_true")
    parser.add_option("-g", "--generated", dest="check_generated", default=False,
                      help="Also check generated Files",
                      action="store_true")
    parser.add_option("--format", dest="format", default=None,
                      help="Custom line format using flags %s"%','.join(FLAGS),
                      action="store")
    parser.add_option("-f", "--formatter", dest="formatter", default="brief",
                      help="One of: %s"%','.join(FORMATTERS.keys()),
                      action="store")
    parser.add_option("-o", "--ordered", dest="ordered", default=False,
                      help="Orders issues by file and line",
                      action="store_true")
    parser.add_option("-r", "--raw", dest="raw", default=False,
                      help="Just prints the output of the checker as is",
                      action="store_true")
    return parser


def evaluate_options(options, args):
    path = os.getcwd()
    if len(args) > 0:
        if len(args) > 1:
            raise UnilintException('Too many arguments')

        path = os.path.join(path, args[0])
        if os.path.exists(path):
            path = args[0]
        else:
            path = None

        if options.formatter not in FORMATTERS.keys():
            raise UnilintException("Unknown Formatter: %s"%options.formatter)

    try:
        options.level = int(options.level)
    except ValueError:
        if not options.level in LEVELS:
            raise UnilintException('Unknown level: %s\nAvailable: %s'%(options.level, LEVELS))

        else:
            options.level = LEVELS[options.level]

    return options, args, path


def unilint_main(argv):
    prog = argv[0]
    args = argv[1:]

    parser = get_unilint_parser("usage: %s [OPTIONS] [PATH]"%prog)
    (options, args) = parser.parse_args(args)

    options, args, path = evaluate_options(options, args)

    return run_cmd(path, options, args)

