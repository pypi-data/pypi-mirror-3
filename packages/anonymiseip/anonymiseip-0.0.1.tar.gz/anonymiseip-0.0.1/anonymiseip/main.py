# Copyright (c) 2012, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""IP Anonymising web service."""

from optparse import OptionParser
from hashlib import sha1
import re
import sys
import threading
from wsgiref.simple_server import make_server

from GeoIP import open as open_db
from GeoIP import GEOIP_MEMORY_CACHE

per_thread = threading.local()

def make_app():
    def app(environ, start_response):
        url = environ['PATH_INFO']
        segments = url.split('/')
        if len(segments) != 3 or segments[1] != 'ipv4':
            start_response('404 NOT FOUND', [])
            return
        if getattr(per_thread, 'db', None) is None:
            per_thread.db = open_db(
                '/usr/share/GeoIP/GeoIP.dat', GEOIP_MEMORY_CACHE)
        source_ip = segments[2]
        base_ip = per_thread.db.range_by_ip(source_ip)[0]
        mask = per_thread.db.last_netmask()
        range_size = 2 ** (32-mask)
        offset = long(sha1(source_ip).hexdigest(), 16) % range_size
        ip_segments = base_ip.split('.')
        base_num = long(ip_segments[0])
        base_num = base_num << 8 | long(ip_segments[1])
        base_num = base_num << 8 | long(ip_segments[2])
        base_num = base_num << 8 | long(ip_segments[3])
        final_num = base_num + offset
        result = "%d.%d.%d.%d" % (
            final_num >> 24,
            final_num >> 16 & 0xff,
            final_num >> 8 & 0xff,
            final_num & 0xff)
        start_response('200 OK', [('Content-Type', 'text/plain')])
        yield result
    return app


def main():
    parser = OptionParser()
    parser.add_option("--host",
            help="The hostname to bind to.", default="0.0.0.0")
    parser.add_option("--port", type=int,
            help="The port to bind to", default=0)
    options, args = parser.parse_args()
    app = make_app()
    # Future: track oopses in this app.
    # app = oops_wsgi.make_app(app, oops_config)
    httpd = make_server(options.host, options.port, app)
    sys.stdout.write(
        "http://%s:%s/\n" % (httpd.server_name, httpd.server_port))
    sys.stdout.flush()
    # Serve until process is killed
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
