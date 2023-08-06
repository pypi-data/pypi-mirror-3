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
from unittest import defaultTestLoader, TestCase

import mocker

from convoy.meta import Builder, extract_metadata


class TestBuilder(Builder):
    """A special CSSComboFile that doesn't log to the stdout."""

    def log(self, msg):
        pass


class ExtractMetadataTest(TestCase):

    def test_extract_single_module(self):
        """
        Extracting the metadata of a file containing a single module
        should successfully extract it's requirements.
        """
        metadata = extract_metadata("""\
        YUI.add('lazr.base', function(Y){
           Y.log('Hello World');
        }, '0.1', {"requires": ["node", "base"]});
        """)

        self.assertEquals(len(metadata), 1)
        self.assertEquals(metadata[0]["name"], "lazr.base")
        self.assertEquals(metadata[0]["requires"], ["node", "base"])

    def test_extract_multiple_modules(self):
        """
        Extracting the metadata of a file that has more than one
        module registered should find all the registrations.
        """
        metadata = extract_metadata("""\
        YUI.add('lazr.base', function(Y){
           Y.log('Hello World');
        }, '0.1', {"requires": ["node", "base"]});
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, '0.1', {"requires": ["node", "anim", "event"]});
        """)

        self.assertEquals(len(metadata), 2)

        self.assertEquals(metadata[0]["name"], "lazr.base")
        self.assertEquals(metadata[0]["requires"], ["node", "base"])

        self.assertEquals(metadata[1]["name"], "lazr.anim")
        self.assertEquals(metadata[1]["requires"], ["node", "anim", "event"])

    def test_extract_multi_line(self):
        """
        If the module registration is split between more than one
        line, we should still be able to extract it.
        """
        metadata = extract_metadata("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, '0.1', {"requires": ["node", "anim",
                              "event"]});
        """)

        self.assertEquals(len(metadata), 1)
        self.assertEquals(metadata[0]["name"], "lazr.anim")
        self.assertEquals(metadata[0]["requires"], ["node", "anim", "event"])

    def test_extract_odd_spacing(self):
        """
        Extracting metadata should work just fine if you have odd
        spacing between the requirements.
        """
        metadata = extract_metadata("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, '0.1', {"requires": [ "node" ,"anim"  ,  "event" ]});
        """)

        self.assertEquals(len(metadata), 1)
        self.assertEquals(metadata[0]["name"], "lazr.anim")
        self.assertEquals(metadata[0]["requires"], ["node", "anim", "event"])

    def test_extract_with_use(self):
        """
        Having both 'use' and 'require in the same declaration should
        not break our parser.
        """
        metadata = extract_metadata("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, '0.1', {"use": ["dom"], "requires": [ "node" ,"anim"  ,  "event" ]});
        """)

        self.assertEquals(len(metadata), 1)
        self.assertEquals(metadata[0]["name"], "lazr.anim")
        self.assertEquals(metadata[0]["requires"], ["node", "anim", "event"])
        self.assertEquals(metadata[0]["use"], ["dom"])

    def test_extract_with_requires_before_use(self):
        """
        The order between 'use' and 'requires' should not matter.
        """
        metadata = extract_metadata("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, '0.1', {"requires": [ "node" ,"anim"  ,  "event" ], "use": ["dom"]});
        """)

        self.assertEquals(len(metadata), 1)
        self.assertEquals(metadata[0]["name"], "lazr.anim")
        self.assertEquals(metadata[0]["requires"], ["node", "anim", "event"])
        self.assertEquals(metadata[0]["use"], ["dom"])

    def test_extract_requires_in_new_line(self):
        """
        Even if the metadata is split between multiple lines, we
        should still be able to extract it.
        """
        metadata = extract_metadata("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, '0.1', {
        "requires": [
          "node" ,"anim"  ,  "event"
        ],
        "use": [
          "dom"
        ]});
        """)

        self.assertEquals(len(metadata), 1)
        self.assertEquals(metadata[0]["name"], "lazr.anim")
        self.assertEquals(metadata[0]["requires"], ["node", "anim", "event"])
        self.assertEquals(metadata[0]["use"], ["dom"])

    def test_extract_metadata_not_metadata(self):
        """
        Don't get metadata from things that ARE NOT metadata.
        """
        metadata = extract_metadata("""
        YUI.add('test', function(Y) {
            this._dds[h[i]] = new YAHOO.util.DragDrop(this._handles[h[i]], this.get('id') + '-handle-' + h, { useShim: this.get('useShim') });
        }, '1.0', {requires: ['dom']});
        """)

        self.assertEquals(metadata[0]["requires"], ["dom"])

    def test_extract_metadata_single_quotes(self):
        """
        If the javascript is using object literals, we should adjust for
        simplejson.
        """
        metadata = extract_metadata("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, '0.1', {
        requires: [
          'node' ,'anim'  ,  'event'
        ],
        use: [
          'dom'
        ]});
        """)

        self.assertEquals(len(metadata), 1)
        self.assertEquals(metadata[0]["name"], "lazr.anim")
        self.assertEquals(metadata[0]["requires"], ["node", "anim", "event"])
        self.assertEquals(metadata[0]["use"], ["dom"])


    def test_extract_has_no_quotes(self):
        """
        If the javascript is using object literals, we should adjust for
        simplejson.
        """
        metadata = extract_metadata("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, '0.1', {
        requires: [
          "node" ,"anim"  ,  "event"
        ],
        use: [
          "dom"
        ]});
        """)

        self.assertEquals(len(metadata), 1)
        self.assertEquals(metadata[0]["name"], "lazr.anim")
        self.assertEquals(metadata[0]["requires"], ["node", "anim", "event"])
        self.assertEquals(metadata[0]["use"], ["dom"])

    def test_extract_has_single_quotes(self):
        """
        If the javascript is using single quotes, we should adjust for
        simplejson.
        """
        metadata = extract_metadata("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, '0.1', {
        'requires': [
          "node" ,"anim"  ,  "event"
        ],
        use: [
          "dom"
        ]});
        """)

        self.assertEquals(len(metadata), 1)
        self.assertEquals(metadata[0]["name"], "lazr.anim")
        self.assertEquals(metadata[0]["requires"], ["node", "anim", "event"])
        self.assertEquals(metadata[0]["use"], ["dom"])

    def test_extract_has_use(self):
        """
        If the javascript is has the word 'cause' the regex shouldn't match
        use in it.
        """
        metadata = extract_metadata("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, '0.1', {
        'requires': [
          "node" ,"anim"  ,  "event"
        ],
        use: [
          "cause",
          "dom"
        ]});
        """)

        self.assertEquals(len(metadata), 1)
        self.assertEquals(metadata[0]["name"], "lazr.anim")
        self.assertEquals(metadata[0]["requires"], ["node", "anim", "event"])
        self.assertEquals(metadata[0]["use"], ["cause", "dom"])

    def test_extract_with_use_and_no_requires(self):
        """
        No failure should happen if we have 'use' but no 'requires'.
        """
        metadata = extract_metadata("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, '0.1', {"use": ["dom"]});
        """)

        self.assertEquals(len(metadata), 1)
        self.assertEquals(metadata[0]["name"], "lazr.anim")
        self.assertEquals(metadata[0]["use"], ["dom"])

    def test_extract_with_all_options(self):
        """
        A very complex registration, with all the options. We should
        be able to parse all of it.
        """
        metadata = extract_metadata("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
           X = Y.bind(function(Y){
               Y.log('goodbye world');
           }, Y);
        }, '0.1', {"use": ["dom"], "omit": ["nono"],
                   "optional": ["meh"],
                   "supersedes": ["old-anim"],
                   "after": ["lazr.base"]});
        """)

        self.assertEquals(len(metadata), 1)
        self.assertEquals(metadata[0]["name"], "lazr.anim")
        self.assertEquals(metadata[0]["use"], ["dom"])
        self.assertEquals(metadata[0]["omit"], ["nono"])
        self.assertEquals(metadata[0]["optional"], ["meh"])
        self.assertEquals(metadata[0]["supersedes"], ["old-anim"])
        self.assertEquals(metadata[0]["after"], ["lazr.base"])

class GenerateMetadataTest(mocker.MockerTestCase):

    def test_generate_metadata_simple(self):
        """
        Verify that the builder can extract and generates a metadata
        file in the expected format.
        """
        root = self.makeDir()
        anim = self.makeDir(path=os.path.join(root, "anim"))
        self.makeFile("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, "0.1", {"use": ["dom"]});
        """, basename="anim.js", dirname=anim)

        output = self.makeFile("")
        builder = TestBuilder(name="LAZR_CONFIG", src_dir=root,
                              output=output, exclude_regex="")
        builder.do_build()

        got = open(output, "r").read()
        prefix = got[:18]
        modules = "\n\n".join(got.split("\n\n")[1:-1])
        self.assertEquals(prefix, "var LAZR_CONFIG = ")
        self.assertTrue('[PATH] = "anim/anim-min.js"' in modules)
        self.assertFalse('[SKINNABLE] = FALSE' in modules)
        self.assertTrue('[TYPE] = JS' in modules)
        self.assertTrue('[USE] = [DOM]' in modules)
        self.assertTrue('[EXT] = TRUE' in modules)

    def test_extract_skinnable(self):
        """
        If a module is skinnable, we'll generate the module
        registration for it's skin ourselves, to prevent YUI from
        auto-generating one, since it assumes the skin path starts
        with the module name.
        """
        root = self.makeDir()
        anim = self.makeDir(path=os.path.join(root, "anim"))
        self.makeFile("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, "0.1", {"use": ["dom"], "requires": ["widget"], "skinnable": true});
        """, basename="anim.js", dirname=anim)

        skin = self.makeDir(path=os.path.join(anim, "assets", "skins", "sam"))
        self.makeFile("""\
        /* anim-skin.css */
        """, basename="anim-skin.css", dirname=skin)

        output = self.makeFile("")
        builder = TestBuilder(name="LAZR_CONFIG", src_dir=root,
                              output=output, exclude_regex="",
                              prefix="lazr")
        builder.do_build()

        got = open(output, "r").read()
        prefix = got[:18]
        modules = "\n\n".join(got.split("\n\n")[1:-1])
        self.assertEquals(prefix, "var LAZR_CONFIG = ")
        self.assertTrue(
            '[PATH] = PREFIX + '
            '"/anim/assets/skins/sam/anim-skin.css"' in modules)
        self.assertTrue(
            '[PATH] = PREFIX + "/anim/anim-min.js"' in modules)
        self.assertTrue('[SKINNABLE] = TRUE' in modules)
        self.assertTrue('[TYPE] = JS' in modules)
        self.assertTrue('[TYPE] = CSS' in modules)
        self.assertTrue('[USE] = [DOM]' in modules)
        self.assertTrue('[REQUIRES] = [WIDGET]' in modules)
        self.assertTrue(('after_list = CORE_CSS') in modules)
        self.assertTrue(('after_list.concat([SKIN_SAM_WIDGET])') in modules)
        self.assertTrue(('[AFTER] = after_list') in modules)
        self.assertTrue('[EXT] = TRUE' in modules)

    def test_extract_no_prefix_doesnt_add_prefix(self):
        """
        If a prefix is not specified, it won't be prepended to the filename.
        """
        root = self.makeDir()
        anim = self.makeDir(path=os.path.join(root, "anim"))
        self.makeFile("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, "0.1", {"use": ["dom"], "requires": ["widget"], "skinnable": true});
        """, basename="anim.js", dirname=anim)

        skin = self.makeDir(path=os.path.join(anim, "assets", "skins", "sam"))
        self.makeFile("""\
        /* anim-skin.css */
        """, basename="anim-skin.css", dirname=skin)

        output = self.makeFile("")
        builder = TestBuilder(name="LAZR_CONFIG", src_dir=root,
                              output=output, exclude_regex="",
                              prefix=None)
        builder.do_build()

        got = open(output, "r").read()
        prefix = got[:18]
        modules = "\n\n".join(got.split("\n\n")[1:-1])
        self.assertEquals(prefix, "var LAZR_CONFIG = ")
        self.assertFalse('  PREFIX =' in got, got)
        self.assertTrue(
            '[PATH] = "anim/assets/skins/sam/anim-skin.css"' in modules)
        self.assertTrue(
            '[PATH] = "anim/anim-min.js"' in modules)
        self.assertTrue('[SKINNABLE] = TRUE' in modules)
        self.assertTrue('[TYPE] = JS' in modules)
        self.assertTrue('[TYPE] = CSS' in modules)
        self.assertTrue('[USE] = [DOM]' in modules)
        self.assertTrue('[REQUIRES] = [WIDGET]' in modules)
        self.assertTrue(('after_list = CORE_CSS') in modules)
        self.assertTrue(('after_list.concat([SKIN_SAM_WIDGET])') in modules)
        self.assertTrue(('[AFTER] = after_list') in modules)
        self.assertTrue('[EXT] = TRUE' in modules)

    def test_extract_no_prefix_no_directory(self):
        """
        If a prefix is not specified, and the filename is directly at the root,
        things don't blow up.
        """
        root = self.makeDir()
        self.makeFile("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, "0.1", {"use": ["dom"], "requires": ["widget"], "skinnable": true});
        """, basename="anim.js", dirname=root)

        output = self.makeFile("")
        builder = TestBuilder(name="LAZR_CONFIG", src_dir=root,
                              output=output, exclude_regex="",
                              prefix=None)
        builder.do_build()

        got = open(output, "r").read()
        prefix = got[:18]
        modules = "\n\n".join(got.split("\n\n")[1:-1])
        self.assertEquals(prefix, "var LAZR_CONFIG = ")
        self.assertFalse('  PREFIX =' in got, got)
        self.assertTrue(
            '[PATH] = "anim-min.js"' in modules)
        self.assertTrue('[TYPE] = JS' in modules)
        self.assertTrue('[USE] = [DOM]' in modules)
        self.assertTrue('[REQUIRES] = [WIDGET]' in modules)
        self.assertTrue('[EXT] = TRUE' in modules)

    def test_extract_skinnable_with_lazr_conventions(self):
        """
        LazrJS conventionally uses a "-core.css" file to load core CSS rules,
        and a "-skin.css" file to store skinnable rules.

        If we find this filesystem structure, let's generate different
        CSS modules and hook them up accordingly. The filename doesn't
        need to match the module name.
        """
        root = self.makeDir()
        anim = self.makeDir(path=os.path.join(root, "anim"))
        self.makeFile("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, "0.1", {"use": ["dom"], "requires": ["widget"], "skinnable": true});
        """, basename="anim.js", dirname=anim)

        assets = self.makeDir(path=os.path.join(anim, "assets"))
        self.makeFile("""\
        /* purty-anim-core.css */
        """, basename="purty-anim-core.css", dirname=assets)

        skin = self.makeDir(path=os.path.join(assets, "skins", "sam"))
        self.makeFile("""\
        /* purty-anim-skin.css */
        """, basename="purty-anim-skin.css", dirname=skin)

        output = self.makeFile("")
        builder = TestBuilder(name="LAZR_CONFIG", src_dir=root,
                              output=output, exclude_regex="",
                              prefix="lazr")
        builder.do_build()

        got = open(output, "r").read()
        prefix = got[:18]
        blocks = got.split("\n\n")
        modules = "\n\n".join(blocks[1:-1])
        self.assertEquals(prefix, "var LAZR_CONFIG = ")

        self.assertTrue(
            '[PATH] = PREFIX + "/anim/assets/purty-anim-core.css"' in modules)
        self.assertTrue(
            '[PATH] = PREFIX + "/anim/assets/skins/sam/purty-anim-skin.css"'
            in modules)
        self.assertTrue(
            '[PATH] = PREFIX + "/anim/anim-min.js"' in modules)
        self.assertTrue('[SKINNABLE] = TRUE' in modules)
        self.assertTrue('[TYPE] = JS' in modules)
        self.assertTrue('[TYPE] = CSS' in modules)
        self.assertTrue('[USE] = [DOM]' in modules)
        self.assertTrue('[REQUIRES] = [WIDGET]' in modules)
        self.assertTrue('[REQUIRES] = [SKIN_SAM_LAZR_ANIM_CORE]' in modules)
        self.assertTrue(('after_list = CORE_CSS') in modules)
        self.assertTrue(
            ('after_list.concat([SKIN_SAM_WIDGET, SKIN_SAM_LAZR_ANIM_CORE])')
            in modules)
        self.assertTrue(('[AFTER] = after_list') in modules)
        self.assertTrue('[EXT] = TRUE' in modules)

    def test_literal_variables_available(self):
        """
        All literals should be specified as var strings.
        """
        root = self.makeDir()
        anim = self.makeDir(path=os.path.join(root, "anim"))
        self.makeFile("""\
        YUI.add('lazr.anim', function(Y){
           Y.log('Hello World');
        }, "0.1", {
            "after": [],
            "ext": false,
            "optional": ["midget"],
            "path": "/path/to/module",
            "requires": ["widget"],
            "skinnable": true,
            "supersedes": [],
            "use": ["dom"]
        });
        """, basename="anim.js", dirname=anim)

        output = self.makeFile("")
        builder = TestBuilder(name="LAZR_CONFIG", src_dir=root,
                              output=output, exclude_regex="",
                              prefix="lazr")
        builder.do_build()

        got = open(output, "r").read()
        self.assertIn('AFTER = "after",', got)
        self.assertIn('EXT = "ext",', got)
        self.assertIn('OPTIONAL = "optional",', got)
        self.assertIn('PATH = "path",', got)
        self.assertIn('REQUIRES = "requires",', got)
        self.assertIn('SKINNABLE = "skinnable",', got)
        self.assertIn('SUPERSEDES = "supersedes",', got)
        self.assertIn('USE = "use",', got)


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
