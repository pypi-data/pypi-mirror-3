from distutils.core import Command


class bdist_msi_fixed(Command):
    user_options = []
    description = "fix bdist_msi command"

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.run_command("bdist_msi")

        fullname = self.distribution.get_fullname()
        bdist_msi_cmd = self.get_finalized_command("bdist_msi")
        pyversion = bdist_msi_cmd.target_version or "any"
        installer_name = bdist_msi_cmd.get_installer_filename(fullname)

        try:
            i = self.distribution.dist_files.index(("bdist_msi", pyversion, fullname))
        except ValueError:
            pass
        else:
            self.distribution.dist_files[i] = ("bdist_msi", pyversion, installer_name)
