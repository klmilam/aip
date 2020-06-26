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

from typing import List, Optional, Set
import dataclasses
import datetime
import io
import os

import yaml

AIP_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'aip'),
)


@dataclasses.dataclass
class Change:
    date: datetime.date
    message: str

    def __hash__(self):
        return hash(str(self))

    def __lt__(self, other: 'Change'):
        # We sort changes in reverse-cron, so a later date is "less" here.
        return self.date > other.date

    def __str__(self):
        return f'{self.date.isoformat()}: {self.message}'


@dataclasses.dataclass
class Heading:
    level: int
    title: str


@dataclasses.dataclass
class AIP:
    id: int
    state: str
    created: datetime.date
    content: str = ''
    scope: Optional[str] = None
    toc: List[Heading] = dataclasses.field(default_factory=list)
    changelog: Set[Change] = dataclasses.field(default_factory=set)

    @classmethod
    def load(cls, directory: str) -> 'AIP':
        """Load an AIP object from the given directory and return it."""
        # First, get the meta file and create the AIP object based on it.
        abs_dir = os.path.join(AIP_DIR, directory)
        meta = yaml.load(io.open(os.path.join(abs_dir, 'meta.yaml'), 'r'))
        aip = AIP(**meta)

        # Next, iterate over the Markdown contents and injest them.
        for f in sorted([os.path.join(abs_dir, i) for i
                         in os.listdir(abs_dir) if i.endswith('*.md')]):
            aip.injest_content(f)

            # Check for an equivalent YAML file and load it if there is one.
            if os.path.exists(y := f.replace('.md', '.yaml')):
                aip.injest_changelog(y)

        # Done; return the AIP object.
        return aip

    def injest_content(self, filename: str):
        """Injest a fragment of an AIP into the object.

        This both appends the content and adds the appropriate header to
        the table of contents.
        """
        snippet: str = io.open(filename, 'r').read()
        self.content += snippet
        line = snippet.lstrip().splitlines()[0]
        if (level := line.count('#')) > 0:
            self.toc.append(Heading(level=level, title=line.lstrip('# ')))

    def injest_changelog(self, filename: str):
        """Injest a fragment of an AIP changelog into the object."""
        conf = yaml.load(io.open(filename, 'r'))
        for cl in conf.get('changelog', ()):
            self.changelog.add(Change(**cl))

    @property
    def updated(self):
        """Return the most recent date on the changelog.

        If there is no changelog, return the created date instead.
        """
        if self.changelog:
            return sorted(self.changelog)[0].date
        return self.created
