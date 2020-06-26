# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import dataclasses
import re

from flask import Flask, render_template, request, Response
from scss.compiler import compile_file
import jinja2

from generator import datatypes


app = Flask(__name__)
site = datatypes.Site.load()
app.jinja_env.filters['relative_url'] = site.relative_url
app.jinja_env.undefined = jinja2.StrictUndefined


@app.route('/')
def hello():
    return 'hello!'


@app.route('/<int:aip_id>')
def aip(aip_id: int):
    """Display a single AIP document."""

    # Load the AIP from disk.
    aip = datatypes.AIP.load('general/{:04d}'.format(aip_id))

    # Return the single AIP template.
    return render_template('pages/aip.html.j2',
        aip=aip,
        site=dataclasses.replace(site, path=request.path),
    )


@app.route('/static/css/<path:css_file>')
def scss(css_file: str):
    """Compile the given SCSS file and return it."""
    scss_file = re.sub(r'\.css$', '.scss', css_file)
    return Response(compile_file(f'scss/{scss_file}'), mimetype='text/css')
