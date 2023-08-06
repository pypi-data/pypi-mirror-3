from distutils.spawn import spawn
from distutils.core import Command


class recompress(Command):
    user_options = []
    description = "recompress .zip/.egg/.tar.gz files with advzip/advdef to get minimal size"

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for command, pyversion, filename in self.distribution.dist_files:
            if filename.endswith(".zip") or filename.endswith(".egg"):
                spawn(["advzip", "-z", "-4", filename])
            elif filename.endswith(".gz"):
                spawn(["advdef", "-z", "-4", filename])
