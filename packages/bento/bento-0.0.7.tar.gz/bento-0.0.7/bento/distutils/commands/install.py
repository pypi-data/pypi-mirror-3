import sys
import os
import os.path as op
import warnings

from distutils.cmd \
    import \
        Command
from distutils.command.install \
    import \
        INSTALL_SCHEMES

from bento._config \
    import \
        IPKG_PATH
from bento.installed_package_description \
    import \
        InstalledPkgDescription, iter_files
from bento.compat.api \
    import \
        relpath
from bento.core.utils \
    import \
        safe_write, subst_vars

from bento.commands.install \
    import \
        InstallCommand
from bento.commands.context \
    import \
        CmdContext
from bento.commands.options \
    import \
        OptionsContext
from bento.commands.wrapper_utils \
    import \
        run_cmd_in_context

class install(Command):
    description = "Install wrapper to install bento package"

    user_options = [
        ('prefix=', None, "installation prefix"),
        ('exec-prefix=', None, "prefix for platform-specific files"),

        ('record=', None, "Record file containing every path created by install command"),
        ('root=', None, "(Unix-only) Alternative root (equivalent to destdir option in bento)"),

        ('dry-run', 'n', "(Unix-only) Alternative root (equivalent to destdir option in bento)"),
        ('single-version-externally-managed', None, "Do nothing. For compatibility with pip only."),
        ('install-headers=', None, "Do nothing. For compatibility with pip only."),
    ]

    def initialize_options(self):
        self.prefix = None
        self.exec_prefix = None
        self.record = None
        self.root = None
        self.dry_run = None
        self.install_headers = None
        self.single_version_externally_managed = None

        self.scheme = {}

    def finalize_options(self):
        if self.install_headers is not None:
            warnings.warn("--install-headers option is ignored.")
        if os.name == "posix":
            self._finalize_unix()
        else:
            self._finalize_other()

    def _finalize_other(self):
        scheme = self.scheme

        if self.root:
            raise ValueError("Option root is meaningless on non-posix platforms !")

        scheme['prefix'] = self.prefix
        scheme['exec_prefix'] = self.exec_prefix

    def _finalize_unix(self):
        scheme = self.scheme

        if self.root:
            scheme["destdir"] = self.root

        # TODO: user and home schemes

        if self.prefix is None:
            prefix_customized = False
        else:
            prefix_customized = True

        if self.prefix is None:
            if self.exec_prefix is not None:
                raise DistutilsOptionError("must not supply exec-prefix without prefix")

            self.prefix = os.path.normpath(sys.prefix)
            self.exec_prefix = os.path.normpath(sys.exec_prefix)
        else:
            if self.exec_prefix is None:
                self.exec_prefix = self.prefix

        py_version_short = ".".join(map(str, sys.version_info[:2]))
        dist_name = self.distribution.pkg.name

        if prefix_customized:
            if op.normpath(self.prefix) != '/usr/local':
                # unix prefix
                scheme['prefix'] = self.prefix
                scheme['exec_prefix'] = self.exec_prefix
            else:
                scheme['prefix'] = self.prefix
                scheme['exec_prefix'] = self.exec_prefix
                # use deb_system on debian-like systems
                if 'deb_system' in INSTALL_SCHEMES:
                    v = {'py_version_short': py_version_short, 'dist_name': dist_name, 'base': self.prefix}
                    scheme['includedir'] = subst_vars(INSTALL_SCHEMES['deb_system']['headers'], v)
                    scheme['sitedir'] = subst_vars(INSTALL_SCHEMES['deb_system']['purelib'], v)
        else:
            # If no prefix is specified, we'd like to avoid installing anything
            # in /usr by default (i.e. like autotools, everything in
            # /usr/local).  If prefix is not /usr, then we can't really guess
            # the best default location.
            if hasattr(sys, 'real_prefix'): # run under virtualenv
                prefix = sys.prefix
                exec_prefix = sys.exec_prefix
            elif sys.prefix == '/usr':
                prefix = exec_prefix = '/usr/local'
            else:
                prefix = sys.prefix
                exec_prefix = sys.exec_prefix
            scheme['prefix'] = prefix
            scheme['exec_prefix'] = exec_prefix
            # use unix_local on debian-like systems
            if 'unix_local' in INSTALL_SCHEMES:
                v = {'py_version_short': py_version_short, 'dist_name': dist_name, 'base': prefix}
                scheme['includedir'] = subst_vars(INSTALL_SCHEMES['unix_local']['headers'], v)
                scheme['sitedir'] = subst_vars(INSTALL_SCHEMES['unix_local']['purelib'], v)

    def run(self):
        self.run_command("build")
        dist = self.distribution
        args = []

        if self.dry_run == 1:
            args.append("--dry-run")
        run_cmd_in_context(InstallCommand, "install", args, CmdContext,
                           dist.run_node, dist.top_node, dist.pkg)
        if self.record:
            self.write_record()

    def write_record(self):
        dist = self.distribution

        install = InstallCommand()
        options_context = OptionsContext.from_command(install)
        context = CmdContext([], options_context, dist.pkg, dist.run_node)

        n = context.build_node.make_node(IPKG_PATH)
        ipkg = InstalledPkgDescription.from_file(n.abspath())
        scheme = context.get_paths_scheme()
        ipkg.update_paths(scheme)
        file_sections = ipkg.resolve_paths_with_destdir(src_root_node=context.build_node)

        def writer(fid):
            for kind, source, target in iter_files(file_sections):
                fid.write("%s\n" % target.abspath())
        safe_write(self.record, writer, "w")
