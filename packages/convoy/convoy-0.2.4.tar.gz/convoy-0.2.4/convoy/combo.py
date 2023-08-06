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


import cgi
import os
import re
import urlparse


CHUNK_SIZE = 2 << 12
URL_RE = re.compile("url\([ \"\']*([^ \"\']+)[ \"\']*\)")
URL_PARSE = re.compile("/([^/]*).*?$")


def relative_path(from_file, to_file):
    """Return the relative path between from_file and to_file."""
    dir_from, base_from = os.path.split(from_file)
    dir_to, base_to = os.path.split(to_file)
    path = os.path.relpath(dir_to, dir_from)
    if path == ".":
        return base_to
    return os.path.join(path, base_to)


def parse_url(url):
    """Parse a combo URL.

    Returns the list of arguments in the original order.
    """
    scheme, loc, path, query, frag = urlparse.urlsplit(url)
    return parse_qs(query)


def parse_qs(query):
    """Parse a query string.

    Returns the list of arguments in the original order.
    """
    params = cgi.parse_qsl(query, keep_blank_values=True)
    return tuple([param for param, value in params])


def combine_files(fnames, root, resource_prefix="", rewrite_urls=True):
    """Combine many files into one.

    Returns an iterator with the combined content of all the
    files. The relative path to root will be included as a comment
    between each file.
    """

    resource_prefix = resource_prefix.rstrip("/")
    for fname in fnames:
        file_ext = os.path.splitext(fname)[-1]
        basename = os.path.basename(fname)
        full = os.path.abspath(os.path.join(root, fname))
        yield "/* " + fname + " */\n"
        if not full.startswith(root) or not os.path.exists(full):
            yield "/* [missing] */\n"
        else:
            with open(full, "r") as f:
                if file_ext == ".css" and rewrite_urls:
                    file_content = f.read()
                    src_dir = os.path.dirname(full)
                    relative_parts = relative_path(
                        os.path.join(root, basename), src_dir).split(
                        os.path.sep)

                    def fix_relative_url(match):
                        url = match.group(1)
                        # Don't modify absolute URLs or 'data:' urls.
                        if (url.startswith("http") or
                            url.startswith("/") or
                            url.startswith("data:")):
                            return match.group(0)
                        parts = relative_parts + url.split("/")
                        result = []
                        for part in parts:
                            if part == ".." and result and result[-1] != "..":
                                result.pop(-1)
                                continue
                            result.append(part)
                        return "url(%s)" % "/".join(
                            filter(None, [resource_prefix] + result))
                    file_content = URL_RE.sub(fix_relative_url, file_content)
                    yield file_content
                    yield "\n"
                else:
                    while True:
                        chunk = f.read(CHUNK_SIZE)
                        if not chunk:
                            yield "\n"
                            break
                        yield chunk


def combo_app(root, resource_prefix="", rewrite_urls=True):
    """A simple YUI Combo Service WSGI app.

    Serves any files under C{root}, setting an appropriate
    C{Content-Type} header.
    """
    root = os.path.abspath(root)

    def app(environ, start_response, root=root):
        # Path hint uses the rest of the url to map to files on disk based off
        # the root specified to convoy.
        path_hint = environ['PATH_INFO'].strip('/')
        fnames = parse_qs(environ["QUERY_STRING"])
        content_type = "text/plain"
        if fnames:
            if fnames[0].endswith(".js"):
                content_type = "text/javascript"
            elif fnames[0].endswith(".css"):
                content_type = "text/css"
        else:
            start_response("404 Not Found", [("Content-Type", content_type)])
            return ("Not Found",)

        # Take any prefix in the url route into consideration for the root to
        # find files.
        updated_root = os.path.join(root, path_hint)
        # Enforce that the updated root is not outside the original root.
        absroot = os.path.abspath(updated_root)
        if not absroot.startswith(os.path.abspath(root)):
            start_response("400 Bad Request", [("Content-Type", content_type)])
            return ("Bad Request",)
        else:
            start_response("200 OK", [("Content-Type", content_type)])

        return combine_files(fnames, updated_root, resource_prefix,
                             rewrite_urls=rewrite_urls)
    return app
