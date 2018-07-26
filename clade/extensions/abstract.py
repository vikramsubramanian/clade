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

import abc
import glob
import logging
import os
import sys
import tempfile
import ujson


class Extension(metaclass=abc.ABCMeta):
    """Parent interface class for parsing intercepted build commands.

    Attributes:
        work_dir: A path to the working directory where all output files will be stored
        cmds: A list with intercepted build commands
        conf: A dictionary with optional arguments

    Raises:
        NotImplementedError: Required sublcass is not found
        FileNotFoundError: Cant find file with parsed build command
    """

    already_initialised = dict()

    def __init__(self, work_dir, conf=None):
        self.name = self.__class__.__name__
        self.work_dir = os.path.join(os.path.abspath(work_dir), self.name)
        self.conf = conf if conf else dict()
        self.temp_dir = tempfile.mkdtemp()

        if not hasattr(self, "requires"):
            self.requires = []

        self.extensions = dict()

        logging.basicConfig(
            format="%(asctime)s {}: %(message)s".format(os.path.basename(sys.argv[0])),
            level=self.conf["log_level"],
            datefmt="%H:%M:%S"
        )

        self.already_initialised[self.name] = self
        self.init_extensions(work_dir)

        self.debug("Working directory: {}".format(self.work_dir))

    def init_extensions(self, work_dir):
        """Initialise all extensions required by this object."""

        if not self.requires:
            return

        self.log("Prerequisites to initialise: {}".format(
            [x for x in self.requires if x not in self.already_initialised]
        ))

        for ext_name in self.requires:
            if ext_name in self.already_initialised:
                self.extensions[ext_name] = self.already_initialised[ext_name]
                continue

            ext_class = Extension.find_subclass(ext_name)
            self.extensions[ext_name] = ext_class(work_dir, self.conf)

    def parse_prerequisites(self, cmds):
        """Run parse() method on all extensions required by this object."""
        for ext_name in self.extensions:
            self.extensions[ext_name].parse(cmds)

    def is_parsed(self):
        """Returns True if build commands are already parsed."""
        return os.path.exists(self.work_dir)

    @abc.abstractmethod
    def parse(self, cmds):
        """Parse intercepted commands."""
        pass

    def load_json(self, file_name):
        """Load json file by name."""

        if not os.path.isabs(file_name):
            file_name = os.path.join(self.work_dir, file_name)

        if not os.path.isfile(file_name):
            raise FileNotFoundError("'{}' file is not found".format(file_name))

        self.debug("Load {}".format(file_name))
        with open(file_name, "r") as fh:
            return ujson.load(fh)

    def dump_data(self, data, file_name):
        """Dump data to a json file in the object working directory."""

        try:
            os.makedirs(self.work_dir)
        except FileExistsError:
            pass

        if not os.path.isabs(file_name):
            file_name = os.path.join(self.work_dir, file_name)

        self.debug("Dump {}".format(file_name))
        with open(file_name, "w") as fh:
            ujson.dump(data, fh, sort_keys=True, indent=4, ensure_ascii=False, escape_forward_slashes=False)

    @staticmethod
    def __get_all_subclasses(cls):
        """Get all sublclasses of a given class."""

        all_subclasses = []

        for subclass in cls.__subclasses__():
            all_subclasses.append(subclass)
            all_subclasses.extend(Extension.__get_all_subclasses(subclass))

        return all_subclasses

    @staticmethod
    def __import_extension_modules():
        """Import all Python modules located in 'extensions' folder."""
        files = glob.glob(os.path.join(os.path.dirname(__file__), '*.py'), recursive=True)
        for file in files:
            sys.path.insert(0, os.path.dirname(file))
            name, _ = os.path.splitext(os.path.basename(file))

            if file != __file__:
                __import__(name)

            sys.path.pop(0)

    @staticmethod
    def find_subclass(ext_name):
        """Find a sublclass of Interface class."""

        Extension.__import_extension_modules()

        for ext_class in Extension.__get_all_subclasses(Extension):
            if ext_name == ext_class.__name__:
                return ext_class
        else:
            raise NotImplementedError("Can't find '{}' class".format(ext_name))

    def log(self, message):
        """Print debug message.

        self.conf["log_level"] must be set to INFO or DEBUG in order to see the message.
        """
        logging.info("{}: {}".format(self.name, message))

    def debug(self, message):
        """Print debug message.

        self.conf["log_level"] must be set to DEBUG in order to see the message.

        WARNING: debug messages can have a great impact on the performance.
        """
        logging.debug("{}: {}".format(self.name, message))