# Copyright (c) 2018 ISP RAS (http://www.ispras.ru)
# Ivannikov Institute for System Programming of the Russian Academy of Sciences
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import sys

from clade.extensions.abstract import Extension
from clade.extensions.utils import parse_args


class Typedefs(Extension):
    requires = ["Info"]

    def __init__(self, work_dir, conf=None):
        if not conf:
            conf = dict()

        super().__init__(work_dir, conf)

        self.typedefs = dict()
        self.typedefs_suffix = ".typedefs.json"

    def parse(self, cmds_file):
        if self.is_parsed():
            self.log("Skip parsing")
            return

        self.parse_prerequisites(cmds_file)

        self.__process_typedefs()
        self.dump_data_by_key(self.typedefs, self.typedefs_suffix)
        self.log("Finish")

    def __process_typedefs(self):
        self.log("Processing typedefs")

        regex = re.compile(r"^declaration: typedef ([^\n]+); path: ([^\n]+)")
        typedefs = self.typedefs

        for line in self.extensions["Info"].iter_typedefs():
            m = regex.match(line)
            if m:
                declaration, scope_file = m.groups()

                if scope_file not in self.typedefs:
                    typedefs[scope_file] = [declaration]
                elif declaration not in typedefs[scope_file]:
                    typedefs[scope_file].append(declaration)

    def load_typedefs(self, files=None):
        return self.load_data_by_key(self.typedefs_suffix, files)


def parse(args=sys.argv[1:]):
    conf = parse_args(args)

    c = Typedefs(conf["work_dir"], conf=conf)
    c.parse(conf["cmds_file"])
