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

from clade.extensions.src_graph import SrcGraph


def test_src_graph(tmpdir, cmds_file):
    conf = {"CmdGraph.requires": ["CC", "MV"]}

    c = SrcGraph(tmpdir, conf)
    c.parse(cmds_file)

    src_graph = c.load_src_graph()
    assert src_graph
    assert set(src_graph["tests/test_project/main.c"]["compiled_in"]) == {"2", "4", "7"}
    assert set(src_graph["tests/test_project/main.c"]["used_by"]) == {"3"}
    assert src_graph["tests/test_project/main.c"]["loc"] == 11


def test_src_graph_empty_conf(tmpdir, cmds_file):
    c = SrcGraph(tmpdir)
    c.parse(cmds_file)

    src_graph = c.load_src_graph()
    assert src_graph
    assert not src_graph["tests/test_project/main.c"]["used_by"]