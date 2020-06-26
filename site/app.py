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

from flask import Flask, render_template

from generator.datatypes import AIP

app = Flask(__name__)


@app.route('/')
def hello():
    return 'hello!'


@app.route('/<int:aip_id>')
def aip(aip_id: int):
    """Display a single AIP document."""

    # Load the AIP from disk.
    aip = AIP.load('general/{:04d}'.format(aip_id))

    # Return the single AIP template.
    return render_template('pages/aip.html.j2', aip=aip)
