import sys
import os
import os.path as op

from six import moves

from bento.utils.utils \
    import \
        subst_vars, virtualenv_prefix
from bento.core.platforms import \
        get_scheme
from bento._config \
    import \
        CONFIGURED_STATE_DUMP, BENTO_SCRIPT

from bento.commands.core \
    import \
        Command, Option
from bento.errors \
    import \
        UsageException

def set_scheme_unix(scheme, options, package):
    # This mess is the simplest solution I can think of to support:
    #   - /usr/local as default for prefix while using debian/ubuntu changes
    #   (dist-packages instead of site-packages)
    #   - virtualenv support
    #   - arbitrary python install
    #
    # Cases to consider:
    #   - if prefix is given:
    #       - prefix and exec_prefix are customized following their options
    #   - if prefix is not given:
    #       - if under virtualenv: prefix and exec_prefix are set to their sys.* values
    #       - else on unix != darwin: using /usr/local
    #       - else on darwin: using sys values
    if options.prefix is not None:
        scheme["prefix"] = options.prefix
        if options.eprefix is None:
            scheme["eprefix"] = scheme["prefix"]
        else:
            scheme["eprefix"] = options.eprefix
    elif options.prefix is None and options.eprefix is not None:
        raise NotImplementedError("Customizing exec_prefix without " \
                                  "customizing prefix is not implemented yet")
    elif options.prefix is None and options.eprefix is None:
        venv_prefix = virtualenv_prefix()
        if venv_prefix is not None:
            scheme["prefix"] = scheme["eprefix"] = venv_prefix
        elif sys.platform == "darwin":
            scheme["prefix"] = op.normpath(sys.prefix)
            scheme["eprefix"] = op.normpath(sys.exec_prefix)
        else:
            # XXX: unix_local is an ubuntu/debian thing only ?
            from distutils.command.install import INSTALL_SCHEMES
            if "unix_local" in INSTALL_SCHEMES:
                dist_scheme = INSTALL_SCHEMES["unix_local"]
                # This madness is used to support ubuntu/debian customization
                prefix = "/usr/local"
                base = "/usr"
                py_version = sys.version.split()[0]
                py_version_short = py_version[0:3]
                dist_name = package.name
                v = {"base": base, "py_version_short": py_version_short, "dist_name": dist_name}

                scheme["prefix"] = scheme["eprefix"] = prefix
                scheme["sitedir"] = subst_vars(dist_scheme["purelib"], v)
                scheme["includedir"] = subst_vars(dist_scheme["headers"], v)
            else:
                scheme["prefix"] = scheme["eprefix"] = "/usr/local"

def set_scheme_win32(scheme, options, package):
    if options.prefix is not None:
        scheme["prefix"] = options.prefix
        if options.eprefix is None:
            scheme["eprefix"] = scheme["prefix"]
        else:
            scheme["eprefix"] = options.eprefix
    elif options.prefix is None and options.eprefix is not None:
        raise NotImplementedError("Customizing exec_prefix without " \
                                  "customizing prefix is not implemented yet")
    elif options.prefix is None and options.eprefix is None:
        venv_prefix = virtualenv_prefix()
        if venv_prefix is not None:
            scheme["prefix"] = scheme["eprefix"] = venv_prefix
        else:
            scheme["prefix"] = op.normpath(sys.prefix)
            scheme["eprefix"] = op.normpath(sys.exec_prefix)

def set_scheme_options(scheme, options, package):
    """Set path variables given in options in scheme dictionary."""
    for k in scheme:
        if hasattr(options, k):
            val = getattr(options, k)
            if val:
                if not os.path.isabs(val):
                    msg = "value given for path option '%s' " \
                          "should be an absolute path (value " \
                          "given was '%s')" % (k, val)
                    raise UsageException(msg)
                scheme[k] = val

    if os.name == "posix":
        set_scheme_unix(scheme, options, package)
    elif os.name == "nt":
        set_scheme_win32(scheme, options, package)
    else:
        raise NotImplementedError("OS %s not supported" % os.name)

    # XXX: define default somewhere and stick with it
    if options.prefix is not None and options.eprefix is None:
        scheme["eprefix"] = scheme["prefix"]

def get_flag_values(cmd, cmd_argv):
    """Return flag values from the command instance and its arguments.

    Assumes cmd is an instance of Configure."""
    o, a = cmd.options_context.parser.parse_args(cmd_argv)
    flag_values = _get_flag_values(cmd.flags, o)
    return flag_values

def _get_flag_values(flag_names, options):
    """Return flag values as defined by the options."""
    flag_values = {}
    for option_name in flag_names:
        flag_value = getattr(options, option_name, None)
        if flag_value is not None:
            if flag_value.lower() in ["true", "yes"]:
                flag_values[option_name] = True
            elif flag_value.lower() in ["false", "no"]:
                flag_values[option_name] = False
            else:
                msg = """Option %s expects a true or false argument"""
                raise UsageException(msg % "--%s" % option_name)
    return flag_values

def _setup_options_parser(options_context, package_options):
    """Setup the command options parser, merging standard options as well
    as custom options defined in the bento.info file, if any.
    """
    scheme, scheme_opts_d = get_scheme(sys.platform)

    p = options_context

    # Create default path options
    scheme_opts = {}
    for name, opt_d in scheme_opts_d.items():
        o = opt_d.pop("opts")
        opt = Option(*o, **opt_d)
        scheme_opts[name] = opt

    # Add custom path options (as defined in bento.info) to the path scheme
    for name, f in package_options.path_options.items():
        scheme_opts[name] = \
            Option('--%s' % f.name,
                   help='%s [%s]' % (f.description, f.default_value))

    p.add_group("installation_options", "Installation fine tuning")
    for opt in scheme_opts.values():
        p.add_option(opt, "installation_options")

    flag_opts = {}
    if package_options.flag_options:
        p.add_group("optional_features", "Optional features")
        for name, v in package_options.flag_options.items():
            flag_opts[name] = Option(
                    "--%s" % v.name,
                    help="%s [default=%s]" % (v.description, v.default_value))
            p.add_option(flag_opts[name], "optional_features")

class ConfigureCommand(Command):
    long_descr = """\
Purpose: configure the project
Usage: bentomaker configure [OPTIONS]"""
    short_descr = "configure the project."

    def __init__(self, *a, **kw):
        super(ConfigureCommand, self).__init__(*a, **kw)
        self.scheme = {}
        self.flags = []

    def register_options(self, options_context, package_options=None):
        _setup_options_parser(options_context, package_options)

        self.scheme.update(_compute_scheme(package_options))
        self.flags.extend(package_options.flag_options.keys())

    def run(self, ctx):
        bento_script = ctx.top_node.find_node(BENTO_SCRIPT)
        if bento_script is None:
            raise IOError("%s not found ?" % BENTO_SCRIPT)

        args = ctx.command_argv
        o, a = ctx.options_context.parser.parse_args(args)
        if o.help:
            ctx.options_context.parser.print_help()
            return

        set_scheme_options(self.scheme, o, ctx.pkg)

def _compute_scheme(package_options):
    """Compute path and flags-related options as defined in the script file(s)

    Parameters
    ----------
    package_options: PackageOptions
    """
    scheme, scheme_opts_d = get_scheme(sys.platform)

    # XXX: abstract away those, as it is copied from distutils
    scheme['py_version_short'] = ".".join(str(part) for part in sys.version_info[:2])
    scheme['pkgname'] = package_options.name

    for name, f in package_options.path_options.items():
        scheme[name] = f.default_value
    return scheme
