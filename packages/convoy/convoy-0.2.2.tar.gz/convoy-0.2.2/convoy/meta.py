#   Convoy is a WSGI app for loading multiple files in the same request.
#   Copyright (C) 2010-2012  Canonical, Ltd.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import json
import re
import sys
import glob
import optparse


DETAILS_RE = re.compile(
    "YUI\.add\([\'\"\s]*([^\'\"]*)[\'\"\s]*,.*?function.*?"
    "[\'\"\s]*[0-9\.]*[\'\"\s]*"
    "({[^{}a-zA-Z]*(use|requires|optional|after|"
    "supersedes|omit|skinnable)[^a-zA-Z][\s\'\":]*[^{}]*})\s*\);", re.M | re.S)
DETAILS_FIND = re.compile(
    '''(?<!")([a-z]+)(?:\s+)?:''',
    re.M | re.S)
DETAILS_REPLACE = r'"\1":'

LITERAL_RE = re.compile("([\[ ]+)\"([\w\.\+-]+)\"([^:])")
NAME_RE = re.compile("[\.\+-]")


def extract_metadata(src):
    """Extract metadata about an YUI module, given it's source."""
    metadata = []
    for entry in DETAILS_RE.finditer(src):
        name, details, ignore = entry.groups()
        details = details.replace('\'', '"')
        details = DETAILS_FIND.sub(DETAILS_REPLACE, details)
        details = json.loads(details)
        details["name"] = name
        metadata.append(details)
    return metadata


class Builder:

    def __init__(self, name, src_dir, output=None,
                 prefix="", exclude_regex=None, ext=True, include_skin=True):
        """Create a new Builder.

        :param name: The name of the global variable name that will
            contain the modules configuration.
        :param src_dir: The directory containing the source files.
        :param output: The output filename for the module metadata.
        :param prefix: A prefix to be added to the relative path.
        :param exclude_regex: A regex that will exclude file
            paths from the final rollup.  -min and -debug versions
            will still be built.
        :param ext: Default value for the 'ext' setting. Set to
            'False' to use modules with a local combo loader.
        :param include_skin: If False, the generated metadata won't include
            skin modules and all javascript modules will have skinnable=False.
            Defaults to True.
        """
        self.name = name
        self.output = output
        self.prefix = prefix
        self.src_dir = src_dir
        self.exclude_regex = exclude_regex
        self.include_skin = include_skin
        self.ext = ext

    def log(self, msg):
        sys.stdout.write(msg + '\n')

    def fail(self, msg):
        """An error was encountered, abort build."""
        sys.stderr.write(msg + '\n')
        sys.exit(1)

    def file_is_excluded(self, filepath):
        """Is the given file path excluded from the rollup process?"""
        if not self.exclude_regex:
            # Include everything.
            return False

        return re.search(self.exclude_regex, filepath)

    def generate_metadata(self, fnames, root, var_name, out):
        """Extract metadata from a group of files and write it out."""
        metadata = []

        for fname in fnames:
            self.log("Extracting metadata from '%s'" % fname)
            data = open(fname, "r").read()
            meta = extract_metadata(data)
            prefix = ""
            if self.prefix and not prefix.endswith("/"):
                prefix = self.prefix + "/"
            for entry in meta:
                # According to the source of the YUI loader module:
                #
                #   The default path for the YUI library is the
                #   minified version of the files (e.g., event-min.js).
                #
                # To make it easier for everyone, let's use the same
                # convention here, and use the minified path.
                relpath = (
                    prefix + fname.replace(root + os.path.sep, "")
                    ).replace(os.path.sep, "/")
                entry["path"] = "%s-min%s" % (
                    os.path.splitext(relpath))

                entry["type"] = "js"
                entry["ext"] = self.ext
                if self.include_skin and entry.get("skinnable"):
                    self.generate_skin_modules(entry, metadata, root)
            metadata.extend(meta)

        modules = {}

        # Include config keys in literals.
        all_literals = ["use", "requires", "optional", "after", "type",
                        "supersedes", "ext", "path", "css", "js", "skinnable"]
        for meta in metadata:
            name = meta.pop("name")
            modules[name] = meta
            all_literals.append(name)
            all_literals.extend(meta.get("use", ()))
            all_literals.extend(meta.get("requires", ()))
            all_literals.extend(meta.get("after", ()))
            all_literals.append(meta["type"])

        # For each string literal we are interested in, generate a
        # variable declaration for the string literal, to improve
        # minification.
        #
        # The variable name is generated by replacing [".", "+", "-"]
        # with an underscore and then make that the variable name,
        # uppercase.
        #
        # We'll save a mapping of literal -> variable name here for
        # reuse below on the re.sub() helper function.
        literals_map = dict([(literal, NAME_RE.sub("_", literal).upper())
                             for literal in set(all_literals)])

        # This re.sub() helper function operates on the JSON-ified
        # representation of the modules, by looking for string
        # literals that occur over the JSON structure but *not* as
        # attribute names.
        #
        # If a string literal is found that matches the list of
        # literals we have declared as variables above, then replace
        # the it by the equivalent variable, otherwise return the
        # original string.
        def literal_sub(match):
            literal = match.group(2)
            if literal in literals_map:
                return match.group(1) + literals_map[literal] + match.group(3)
            return match.group(0)


        linebreak = ",\n  "
        variables_decl = "var SKIN_SAM_PREFIX = 'skin-sam-'" + linebreak
        if self.prefix:
             variables_decl += "PREFIX = '%s'%s" % (self.prefix, linebreak)
        extra_variables = []
        for literal, variable in sorted(literals_map.iteritems()):
            extra_variable = "%s = %s" % (
                variable, ('"%s"' % literal).replace(
                    '"skin-sam-', 'SKIN_SAM_PREFIX + "'))
            if self.prefix:
                extra_variable = extra_variable.replace(
                    '"%s.' % self.prefix, 'PREFIX + ".')
            extra_variables.append(extra_variable)
        variables_decl += linebreak.join(extra_variables)

        # Default 'after' modules from YUI Loader. Might have to
        # be changed in the future, if YUI itself changes.
        core_css = ["cssreset", "cssfonts",
                    "cssgrids", "cssreset-context",
                    "cssfonts-context",
                    "cssgrids-context"]

        # Append a few more helper variables for our own use.
        variables_decl += ",\n  ".join(
            ["",
             "modules = {}",
             "TRUE = true",
             "FALSE = false",
             "CORE_CSS = %s" % LITERAL_RE.sub(literal_sub,
                                              json.dumps(core_css)),
             "module_info",
             "after_list"])

        modules_decl = []
        for module_name, module_info in sorted(modules.iteritems()):
            module_decl = [
                "modules[%s] = module_info = {}" %
                NAME_RE.sub("_", module_name).upper()]
            for key, value in sorted(module_info.iteritems()):
                if value is True or value is False:
                    value = str(value).upper()
                elif value in ("css", "js"):
                    value = value.upper()
                else:
                    value = LITERAL_RE.sub(literal_sub, json.dumps(value))
                if key == "after" and module_info["type"] == "css":
                    # It's easy to think that doing 'CORE_CSS +  %(values)s'
                    # instead of using concat would work, but it doesn't;
                    # you'll end up with a string instead of a list.
                    module_decl.append("after_list = CORE_CSS");
                    module_decl.append("after_list.concat(%s)" % value);
                    value = "after_list"
                if key == "path":
                    value = value.replace(
                        '"%s/' % self.prefix, 'PREFIX + "/')
                module_decl.append("module_info[%s] = %s" %
                                   (key.upper(), value))
            modules_decl.append(";\n  ".join(module_decl))

        modules_decl = ";\n\n  ".join(modules_decl)

        module_config = open(out, "w")
        try:
            module_config.write("""var %s = (function(){
  %s;

  %s;

  return modules;
})();""" % (var_name, variables_decl, modules_decl))
        finally:
            module_config.close()

    def generate_skin_modules(self, entry, metadata, root):
        # Generate a skin module definition, since YUI assumes that
        # the path starts with the module name, and that breaks with
        # our structure.
        #
        # Follow lazr-js conventions and look for any file in the skin
        # assets directory.
        module_names = []
        by_name = {}

        prefix = ""
        if self.prefix and not prefix.endswith("/"):
            prefix = self.prefix + "/"

        if entry.get("requires"):
            # If the base module requires other modules, extend
            # the after entry with the (expected) skins for those
            # modules to force our skin to be loaded after those.
            after = ["skin-sam-%s" % s
                     for s in entry["requires"]]

        assets = os.path.join(
            os.path.dirname(entry["path"][len(prefix):]), "assets")
        sam = os.path.join(assets, "skins", "sam")
        css_assets = glob.glob(os.path.join(root, sam, "*-skin.css"))

        for fname in css_assets:
            if not os.path.exists(fname):
                # If the file doesn't exist, don't create a module to
                # load it.
                continue

            # Compute a module name for this asset.
            module_name = os.path.basename(fname)[:-len("-skin.css")]
            skin_module_name = "skin-sam-%s" % entry["name"]
            # If the computed module_name does not match the
            # Javascript module name without the namespace, then use
            # it as a postfix to disambiguate possibly multiple
            # modules.
            package = entry["name"].split(".")[-1]
            if module_name != package and len(css_assets) > 1:
                skin_module_name = "%s+%s" % (skin_module_name, module_name)

            css = (fname.replace(root + os.path.sep, "")
                   ).replace(os.path.sep, "/")
            module = {"name": skin_module_name,
                      "after": after[:],
                      "type": "css",
                      "ext": self.ext,
                      "path": prefix + css}
            by_name[skin_module_name] = module
            module_names.append(skin_module_name)
            metadata.append(module)

        # All assets under the skin have been looked at. Now look for
        # a "-core.css" asset, following lazr-js conventions and add
        # it as a requirement for the previously-found assets.
        for module_name in module_names:
            name = os.path.basename(
                by_name[module_name]["path"])[:-len("-skin.css")]
            fname = os.path.join(root, assets, "%s-core.css" % name)
            if not os.path.exists(fname):
                # No core CSS asset exists for this skin, skip
                # generating a module for it.
                continue

            skin_module_name = "%s+core" % module_name
            css = (fname.replace(root + os.path.sep, "")
                   ).replace(os.path.sep, "/")
            module = {"name": skin_module_name,
                      "after": after[:],
                      "type": "css",
                      "ext": self.ext,
                      "path": prefix + css}

            requires = by_name[module_name].setdefault("requires", [])
            requires.append(skin_module_name)
            after = by_name[module_name].setdefault("after", [])
            after.append(skin_module_name)
            metadata.append(module)

    def do_build(self):
        included_files = []

        for root, dirnames, fnames in os.walk(self.src_dir):
            for fname in glob.glob(os.path.join(root, '*.js')):
                if not self.file_is_excluded(fname):
                    included_files.append(fname)

        self.generate_metadata(included_files, self.src_dir,
                               self.name, self.output)


def get_options():
    """Parse the command line options."""
    parser = optparse.OptionParser(
        usage="%prog [options]",
        description=(
            "Create YUI module metadata from extension modules. "
            ))
    parser.add_option(
        '-n', '--name', dest='name', default='LAZR_MODULES',
        help=('The global variable name used to hold the modules config.'))
    parser.add_option(
        '-o', '--output', dest='output',
        help=('The output filename for the module metadata.'))
    parser.add_option(
        '-p', '--prefix', dest='prefix', default="",
        help=('A prefix to be added to the relative path.'))
    parser.add_option(
        '-s', '--srcdir', dest='src_dir',
        help=('The directory containing the src files.'))
    parser.add_option(
        '-e', '--ext', dest='ext', default=False,
        action="store_true",
        help=('Default value for the "ext" configuration setting.'))
    parser.add_option(
        '-x', '--exclude', dest='exclude_regex',
        default=None, metavar='REGEX',
        help=('Exclude any files that match the given regular expressions.'))
    parser.add_option(
        '-k', '--no-skin', dest='no_skin', default=False, action="store_true",
        help=('Do not include skin files in the list of modules and set '
              'skinnable=False for all modules.'))
    return parser.parse_args()


def main():
   options, args = get_options()
   if options.src_dir is None:
       options.src_dir = os.getcwd()
   Builder(
       name=options.name,
       src_dir=os.path.abspath(options.src_dir),
       output=options.output,
       prefix=options.prefix,
       exclude_regex=options.exclude_regex,
       ext=options.ext,
       include_skin=not options.no_skin,
       ).do_build()
