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
import difflib
import textwrap
from unittest import defaultTestLoader

import mocker
from paste.fixture import TestApp

from convoy.combo import combo_app
from convoy.combo import combine_files
from convoy.combo import parse_url


class ComboTestBase(object):

    def makeSampleFile(self, root, fname, content):
        content = textwrap.dedent(content).strip()
        full = os.path.join(root, fname)
        parent = os.path.dirname(full)
        if not os.path.exists(parent):
            os.makedirs(parent)
        return self.makeFile(content=content, path=full)

    def assertTextEquals(self, expected, got):
        expected = textwrap.dedent(expected).strip()
        got = textwrap.dedent(got).strip()
        diff = difflib.unified_diff(expected.splitlines(),
                                    got.splitlines(), lineterm="")
        self.assertEquals(expected, got, "\n" + "\n".join(diff))


class ComboTest(ComboTestBase, mocker.MockerTestCase):

    def test_parse_url_keeps_order(self):
        """Parsing a combo loader URL returns an ordered list of filenames."""
        self.assertEquals(
            parse_url(("http://yui.yahooapis.com/combo?"
                       "3.0.0/build/yui/yui-min.js&"
                       "3.0.0/build/oop/oop-min.js&"
                       "3.0.0/build/event-custom/event-custom-min.js&")),
            ("3.0.0/build/yui/yui-min.js",
             "3.0.0/build/oop/oop-min.js",
             "3.0.0/build/event-custom/event-custom-min.js"))

    def test_combine_files_includes_filename(self):
        """Combining files should include their relative filename."""
        test_dir = self.makeDir()

        self.makeSampleFile(
            test_dir,
            os.path.join("yui", "yui-min.js"),
            "** yui-min **"),
        self.makeSampleFile(
            test_dir,
            os.path.join("oop", "oop-min.js"),
            "** oop-min **"),
        self.makeSampleFile(
            test_dir,
            os.path.join("event-custom", "event-custom-min.js"),
            "** event-custom-min **"),

        expected = "\n".join(("/* yui/yui-min.js */",
                              "** yui-min **",
                              "/* oop/oop-min.js */",
                              "** oop-min **",
                              "/* event-custom/event-custom-min.js */",
                              "** event-custom-min **"))
        self.assertEquals(
            "".join(combine_files(["yui/yui-min.js",
                                   "oop/oop-min.js",
                                   "event-custom/event-custom-min.js"],
                                  root=test_dir)).strip(),
            expected)

    def test_combine_css_makes_relative_path(self):
        """
        Combining CSS files makes URLs in CSS declarations relative to the
        target path.
        """
        test_dir = self.makeDir()

        self.makeSampleFile(
            test_dir,
            os.path.join("widget", "assets", "skins", "sam", "widget.css"),
            """\
            /* widget skin */
            .yui-widget {
               background: url("img/bg.png");
            }
            """)

        self.makeSampleFile(
            test_dir,
            os.path.join("editor", "assets", "skins", "sam", "editor.css"),
            """\
            /* editor skin */
            .yui-editor {
               background: url("img/bg.png");
            }
            """)

        expected = """
            /* widget/assets/skins/sam/widget.css */
            /* widget skin */
            .yui-widget {
               background: url(widget/assets/skins/sam/img/bg.png);
            }
            /* editor/assets/skins/sam/editor.css */
            /* editor skin */
            .yui-editor {
               background: url(editor/assets/skins/sam/img/bg.png);
            }
            """
        self.assertTextEquals(
            "".join(combine_files(["widget/assets/skins/sam/widget.css",
                                   "editor/assets/skins/sam/editor.css"],
                                  root=test_dir)).strip(),
            expected)

    def test_combine_css_leaves_absolute_urls_untouched(self):
        """
        Combining CSS files does not touch absolute URLs in
        declarations.
        """
        test_dir = self.makeDir()

        self.makeSampleFile(
            test_dir,
            os.path.join("widget", "assets", "skins", "sam", "widget.css"),
            """
            /* widget skin */
            .yui-widget {
               background: url("/static/img/bg.png");
            }
            """)

        self.makeSampleFile(
            test_dir,
            os.path.join("editor", "assets", "skins", "sam", "editor.css"),
            """
            /* editor skin */
            .yui-editor {
               background: url("http://foo/static/img/bg.png");
            }
            """)

        expected = """
            /* widget/assets/skins/sam/widget.css */
            /* widget skin */
            .yui-widget {
               background: url("/static/img/bg.png");
            }
            /* editor/assets/skins/sam/editor.css */
            /* editor skin */
            .yui-editor {
               background: url("http://foo/static/img/bg.png");
            }
            """
        self.assertTextEquals(
            "".join(combine_files(["widget/assets/skins/sam/widget.css",
                                   "editor/assets/skins/sam/editor.css"],
                                  root=test_dir)).strip(),
            expected)

    def test_combine_css_leaves_data_uris_untouched(self):
        """
        Combining CSS files does not touch data uris in
        declarations.
        """
        test_dir = self.makeDir()

        self.makeSampleFile(
            test_dir,
            os.path.join("widget", "assets", "skins", "sam", "widget.css"),
            """\
            /* widget skin */
            .yui-widget {
               background: url("data:image/gif;base64,base64-data");
            }
            """)

        self.makeSampleFile(
            test_dir,
            os.path.join("editor", "assets", "skins", "sam", "editor.css"),
            """\
            /* editor skin */
            .yui-editor {
               background: url("data:image/gif;base64,base64-data");
            }
            """)

        expected = """
            /* widget/assets/skins/sam/widget.css */
            /* widget skin */
            .yui-widget {
               background: url("data:image/gif;base64,base64-data");
            }
            /* editor/assets/skins/sam/editor.css */
            /* editor skin */
            .yui-editor {
               background: url("data:image/gif;base64,base64-data");
            }
            """
        self.assertTextEquals(
            "".join(combine_files(["widget/assets/skins/sam/widget.css",
                                   "editor/assets/skins/sam/editor.css"],
                                  root=test_dir)).strip(),
            expected)

    def test_missing_file_is_ignored(self):
        """If a missing file is requested we should still combine others."""
        test_dir = self.makeDir()

        self.makeSampleFile(
            test_dir,
            os.path.join("yui", "yui-min.js"),
            "** yui-min **"),
        self.makeSampleFile(
            test_dir,
            os.path.join("event-custom", "event-custom-min.js"),
            "** event-custom-min **"),

        expected = "\n".join(("/* yui/yui-min.js */",
                              "** yui-min **",
                              "/* oop/oop-min.js */",
                              "/* [missing] */",
                              "/* event-custom/event-custom-min.js */",
                              "** event-custom-min **"))
        self.assertEquals(
            "".join(combine_files(["yui/yui-min.js",
                                   "oop/oop-min.js",
                                   "event-custom/event-custom-min.js"],
                                  root=test_dir)).strip(),
            expected)

    def test_no_parent_hack(self):
        """If someone tries to hack going up the root, he'll get a miss."""
        test_dir = self.makeDir()

        self.makeSampleFile(
            test_dir,
            os.path.join("oop", "oop-min.js"),
            "** oop-min **"),

        root = os.path.join(test_dir, "root", "lazr")
        os.makedirs(root)

        hack = "../../oop/oop-min.js"
        self.assertTrue(os.path.exists(os.path.join(root, hack)))

        expected = "\n".join(("/* ../../oop/oop-min.js */",
                              "/* [missing] */"))
        self.assertEquals(
            "".join(combine_files([hack], root=root)).strip(),
            expected)

    def test_no_absolute_path_hack(self):
        """
        If someone tries to fetch an absolute file, it'll be as if a missing
        file was requested.
        """
        test_dir = self.makeDir()

        hack = "/etc/passwd"
        self.assertTrue(os.path.exists("/etc/passwd"))

        expected = "/* /etc/passwd */\n/* [missing] */"
        self.assertEquals(
            "".join(combine_files([hack], root=test_dir)).strip(),
            expected)

    def test_no_traversing_out_of_root(self):
        """
        If someone were to use .. in the path make sure we don't let them out
        of the root of the combo loader
        """
        test_dir = self.makeDir()

        hack = ".."

        expected = "/* .. */\n/* [missing] */"
        self.assertEquals(
            "".join(combine_files([hack], root=test_dir)).strip(),
            expected)

        # from /tmp/somedir we want to try to walk up to / and into
        # etc/password
        hack = "../../etc/password"
        expected = "/* ../../etc/password */\n/* [missing] */"
        self.assertEquals(
            "".join(combine_files([hack], root=test_dir)).strip(),
            expected)

    def test_combine_css_adds_custom_prefix(self):
        """
        Combining CSS files makes URLs in CSS declarations relative to the
        target path. It's also possible to specify an additional prefix for the
        rewritten URLs.
        """
        test_dir = self.makeDir()

        self.makeSampleFile(
            test_dir,
            os.path.join("widget", "assets", "skins", "sam", "widget.css"),
            """
            /* widget skin */
            .yui-widget {
               background: url("img/bg.png");
            }
            """)
        self.makeSampleFile(
            test_dir,
            os.path.join("editor", "assets", "skins", "sam", "editor.css"),
            """
            /* editor skin */
            .yui-editor {
               background: url("img/bg.png");
            }
            """)

        expected = """
            /* widget/assets/skins/sam/widget.css */
            /* widget skin */
            .yui-widget {
               background: url(/static/widget/assets/skins/sam/img/bg.png);
            }
            /* editor/assets/skins/sam/editor.css */
            /* editor skin */
            .yui-editor {
               background: url(/static/editor/assets/skins/sam/img/bg.png);
            }
            """
        self.assertTextEquals(
            "".join(combine_files(["widget/assets/skins/sam/widget.css",
                                   "editor/assets/skins/sam/editor.css"],
                                  root=test_dir,
                                  resource_prefix="/static/")).strip(),
            expected)

    def test_rewrite_url_normalizes_parent_references(self):
        """URL references in CSS files get normalized for parent dirs."""
        test_dir = self.makeDir()
        files = [
            self.makeSampleFile(
                test_dir,
                os.path.join("yui", "base", "base.css"),
                ".foo{background-image:url(../../img.png)}"),
            ]

        expected = """
            /* yui/base/base.css */
            .foo{background-image:url(img.png)}
            """
        self.assertTextEquals(
            "".join(combine_files(["yui/base/base.css"],
                                  root=test_dir)).strip(),
            expected)


class WSGIComboTest(ComboTestBase, mocker.MockerTestCase):

    def setUp(self):
        self.root = self.makeDir()
        self.app = TestApp(combo_app(self.root))

    def test_combo_app_sets_content_type_for_js(self):
        """The WSGI App should set a proper Content-Type for Javascript."""
        self.makeSampleFile(
            self.root,
            os.path.join("yui", "yui-min.js"),
            "** yui-min **"),
        self.makeSampleFile(
            self.root,
            os.path.join("oop", "oop-min.js"),
            "** oop-min **"),
        self.makeSampleFile(
            self.root,
            os.path.join("event-custom", "event-custom-min.js"),
            "** event-custom-min **"),

        expected = "\n".join(("/* yui/yui-min.js */",
                              "** yui-min **",
                              "/* oop/oop-min.js */",
                              "** oop-min **",
                              "/* event-custom/event-custom-min.js */",
                              "** event-custom-min **"))

        res = self.app.get("/?" + "&".join(
            ["yui/yui-min.js",
             "oop/oop-min.js",
             "event-custom/event-custom-min.js"]), status=200)
        self.assertEquals(res.headers, [("Content-Type", "text/javascript")])
        self.assertEquals(res.body.strip(), expected)

    def test_combo_app_sets_content_type_for_css(self):
        """The WSGI App should set a proper Content-Type for CSS."""
        self.makeSampleFile(
            self.root,
            os.path.join("widget", "skin", "sam", "widget.css"),
            "/* widget-skin-sam */"),

        expected = "/* widget/skin/sam/widget.css */\n/* widget-skin-sam */"

        res = self.app.get("/?" + "&".join(
            ["widget/skin/sam/widget.css"]), status=200)
        self.assertEquals(res.headers, [("Content-Type", "text/css")])
        self.assertEquals(res.body.strip(), expected)

    def test_no_filename_gives_404(self):
        """If no filename is included, a 404 should be returned."""
        res = self.app.get("/", status=404)
        self.assertEquals(res.headers, [("Content-Type", "text/plain")])
        self.assertEquals(res.body, "Not Found")

    def test_combo_respects_path_hints(self):
        """If I add path info into the combo url, convoy should use it."""
        # we want the app to be rooted at /tmp and we'll adjust the paths via
        # url
        app = TestApp(combo_app('/tmp'))

        # create paths we'll store files into. All of them end up in
        # /tmp/xxxxx. We want to point the root of the combo loader at /tmp
        # and use url pathing to route to the right set of files for final
        # usage.
        first_root = self.makeDir()
        second_root = self.makeDir()

        # we need to parse where the actual roots are located to know what
        # path to add to the urls
        first_base = os.path.basename(first_root)
        second_base = os.path.basename(second_root)

        self.makeSampleFile(
            first_root,
            os.path.join("yui", "yui-min.js"),
            "/* yui-min */"),

        self.makeSampleFile(
            second_root,
            os.path.join("yui", "yui-min.js"),
            "/* yui-min-2 */"),

        expected = "\n".join(("/* yui/yui-min.js */",
                              "/* yui-min */"))
        expected2 = "\n".join(("/* yui/yui-min.js */",
                               "/* yui-min-2 */"))

        res = app.get("/%s/?%s" % (first_base,
            "yui/yui-min.js"), status=200)
        self.assertEquals(res.body.strip(), expected)

        res = app.get("/%s/?%s" % (second_base, "&".join(
            ["yui/yui-min.js"])), status=200)
        self.assertEquals(res.body.strip(), expected2)


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
