import os
import sys
import string

import os.path as op

from bento.errors \
    import \
        InvalidPackage
from bento.utils.utils \
    import \
        is_string, subst_vars
from bento.compat.api \
    import \
        defaultdict
from bento.core.node_package \
    import \
        NodeRepresentation
from bento.commands.build \
    import \
        _config_content
from bento.core.meta \
    import \
        PackageMetadata
from bento.commands.script_utils \
    import \
        create_posix_script, create_win32_script
from bento._config \
    import \
        CONFIGURED_STATE_DUMP
from bento.commands.configure \
    import \
        _compute_scheme
from bento.commands.build \
    import \
        SectionWriter
from bento.commands.install \
    import \
        copy_installer
from bento.installed_package_description \
    import \
        InstalledSection

class DummyContextManager(object):
    def __init__(self, pre, post):
        self.pre = pre
        self.post = post

    def __enter__(self):
        self.pre()

    def __exit__(self, *a, **kw):
        self.post()

class CmdContext(object):
    def __init__(self, global_context, command_argv, options_context, pkg, run_node):
        self._global_context = global_context
        self.pkg = pkg

        self.options_context = options_context
        o, a = options_context.parser.parse_args(command_argv)
        if o.help:
            self.help = True
        else:
            self.help = False

        self.command_argv = command_argv

        # All of run/top/cur nodes are set to the same value for the base
        # context: without a bento.info available, neither build directory, nor
        # out-of-tree concepts make much sense.

        # CWD node
        self.run_node = run_node
        # Top source node (the one containing the top bento.info)
        self.top_node = run_node
        # cur_node refers to the current path when recursing into sub directories
        self.cur_node = run_node

        # Recursive related members
        self.local_node = None
        self.local_pkg = None

    def recurse_manager(self, local_node):
        """
        Return a dummy object to use for recurse if one wants to use context
        manager. Example::

            with context.recurse_manager(local_node):
                func(context)
        """
        return DummyContextManager(lambda: self.pre_recurse(local_node),
                                   lambda: self.post_recurse())

    def pre_recurse(self, local_node):
        """
        Note
        ----
        Every call to pre_recurse should be followed by a call to post_recurse.

        Calling pre_recurse for the top hook node must work as well (but could
        do nothing)
        """
        if local_node == self.run_node:
            self.local_node = self.run_node
            return
        else:
            if not local_node.is_src():
                raise IOError("node %r is not in source tree !" % local_node.abspath())
            self.local_node = local_node

            def _get_sub_package():
                relative_pos = local_node.path_from(self.top_or_sub_directory_node)
                local_bento = self.top_node.find_node(op.join(relative_pos, "bento.info"))
                k = local_bento.path_from(self.run_node)
                if k is None:
                    raise IOError("%r not found" % os.path.join(local_node.abspath(), "bento.info"))
                else:
                    return self.pkg.subpackages.get(k, None)
            self.local_pkg = _get_sub_package()

    def post_recurse(self):
        # Setting those to None is not strictly necessary, but this makes
        # things more consistent for debugging (context state exactly same
        # before pre_recurse and after post_recurse
        self.local_node = None
        self.local_pkg = None

    def get_parsed_arguments(self):
        return self.options_context.parser.parse_args(self.command_argv)

    def retrieve_scheme(self):
        return self._global_context.retrieve_scheme()

    def retrieve_configured_scheme(self):
        configure_argv = self._global_context.retrieve_command_argv("configure")
        return self._global_context.retrieve_configured_scheme(configure_argv)

    # This is run before the associated command pre-hooks
    def init(self):
        pass

    # This is run after the associated command pre-hooks, but before the command run function
    def configure(self):
        pass

    # This is run after the associated command post_hooks
    def finish(self):
        pass

class ContextWithBuildDirectory(CmdContext):
    def __init__(self, *a, **kw):
        super(ContextWithBuildDirectory, self).__init__(*a, **kw)
        self.build_root = self.run_node.make_node("build")

        # TODO: kept for compatibility. Remove it ?
        assert self.run_node is not None
        self.top_node = self.run_node._ctx.srcnode
        self.build_node = self.run_node._ctx.bldnode

        if self.pkg.sub_directory:
            self.top_or_sub_directory_node = self.top_node.make_node(self.pkg.sub_directory)
            self.build_or_sub_directory_node = self.build_node.make_node(self.pkg.sub_directory)
        else:
            self.top_or_sub_directory_node = self.top_node
            self.build_or_sub_directory_node = self.build_node

    def make_source_node(self, path):
        n = self.top_node.find_node(path)
        if n is None:
            raise IOError("file %s not found" % (op.join(self.top_node.abspath(), path)))
        else:
            return n

    def make_build_node(self, path):
        n = self.build_node.make_node(path)
        n.parent.mkdir()
        return n

class ConfigureContext(ContextWithBuildDirectory):
    pass

class _Dummy(object):
    pass

class _RegistryBase(object):
    """A simple registry of sets of callbacks, one set per category."""
    def __init__(self):
        self._callbacks = {}
        self.categories = _Dummy()

    def register_category(self, category, default_builder):
        if category in self._callbacks:
            raise ValueError("Category %r already registered" % category)
        else:
            self._callbacks[category] = defaultdict(lambda: default_builder)
            setattr(self.categories, category, _Dummy())

    def register_callback(self, category, name, builder):
        c = self._callbacks.get(category, None)
        if c is not None:
            c[name] = builder
            cat = getattr(self.categories, category)
            setattr(cat, name, builder)
        else:
            raise ValueError("category %s is not registered yet" % category)

    def callback(self, category, name):
        if not category in self._callbacks:
            raise ValueError("Unregistered category %r" % category)
        else:
            return self._callbacks[category][name]

    def default_callback(self, category, *a, **kw):
        if not category in self._callbacks:
            raise ValueError("Unregistered category %r" % category)
        else:
            return self._callbacks[category].default_factory()(*a, **kw)

class BuilderRegistry(_RegistryBase):
    builder = _RegistryBase.callback

class ISectionRegistry(_RegistryBase):
    registrer = _RegistryBase.callback

class OutputRegistry(object):
    def __init__(self, categories=None):
        self.categories = {}
        self.installed_categories = {}
        if categories:
            for category, installed_category in categories:
                self.register_category(category, installed_category)

    def register_category(self, category, installed_category):
        if category in self.categories:
            raise ValueError("Category %r already registered")
        else:
            self.categories[category] = {}
            self.installed_categories[category] = installed_category

    def register_outputs(self, category, name, nodes, from_node, target_dir):
        if not category in self.categories:
            raise ValueError("Unknown category %r" % category)
        else:
            cat = self.categories[category]
            if name in cat:
                raise ValueError("Outputs for categoryr=%r and name=%r already registered" % (category, name))
            else:
                cat[name] = (nodes, from_node, target_dir)

    def iter_category(self, category):
        if not category in self.categories:
            raise ValueError("Unknown category %r" % category)
        else:
            for k, v in self.categories[category].items():
                yield k, v[0], v[1], v[2]

    def iter_over_category(self):
        for category in self.categories:
            for name, nodes, from_node, target_dir in self.iter_category(category):
                yield category, name, nodes, from_node, target_dir

def _generic_iregistrer(category, name, nodes, from_node, target_dir):
    source_dir = os.path.join("$_srcrootdir", from_node.bldpath())
    files = [n.path_from(from_node) for n in nodes]
    return InstalledSection.from_source_target_directories(
        category, name, source_dir, target_dir, files)

def fill_metadata_template(content, metadata):
    tpl = string.Template(content)

    def _safe_repr(val):
        # FIXME: actually not safe at all. Needs to escape and all.
        if is_string(val):
            if len(val.splitlines()) > 1:
                return '"""%s"""' % (val,)
            else:
                return '"%s"' % (val,)
        else:
            return repr(val)

    meta_dict = dict((k.upper(), _safe_repr(v)) for k, v in metadata.items())

    return tpl.substitute(meta_dict)

def _write_template(template_node, metadata):
    source_content = template_node.read()
    output_content = fill_metadata_template(source_content, metadata)

    output = template_node.change_ext("")
    output.safe_write(output_content)
    return output

def write_template(top_node, template_file, package, additional_metadata=None):
    if additional_metadata is None:
        additional_metadata = {}

    source = top_node.find_node(template_file)
    if source is None:
        raise InvalidPackage("File %r not found (defined in 'MetaTemplateFile' field)" \
                             % (package.meta_template_file,))
    package_metadata = PackageMetadata.from_package(package)
    meta = dict((k, getattr(package_metadata, k)) for k in package_metadata.metadata_attributes)
    meta.update(additional_metadata)
    return _write_template(source, meta)

class BuildContext(ContextWithBuildDirectory):
    def __init__(self, global_context, command_argv, options_context, pkg, run_node):
        super(BuildContext, self).__init__(global_context, command_argv, options_context, pkg, run_node)
        self.builder_registry = BuilderRegistry()
        self.section_writer = SectionWriter()

        o, a = self.options_context.parser.parse_args(command_argv)
        if o.inplace:
            self.inplace = True
        else:
            self.inplace = False
        # Builders signature:
        #   - first argument: name, str. Name of the entity to be built
        #   - second argument: object. Value returned by
        #   NodePackage.iter_category for this category

        # TODO: # Refactor builders so that they directoy register outputs
        # instead of returning stuff to be registered (to allow for "delayed"
        # registration)
        def data_section_builder(name, section):
            return name, section.nodes, section.ref_node, section.target_dir

        def package_builder(name, node_py_package):
            return name, node_py_package.nodes, self.top_or_sub_directory_node, "$sitedir"

        def module_builder(name, node):
            return name, [node], self.top_or_sub_directory_node, "$sitedir"

        def script_builder(name, executable):
            scripts_node = self.build_node.make_node("scripts-%s" % sys.version[:3])
            scripts_node.mkdir()
            if sys.platform == "win32":
                nodes = create_win32_script(name, executable, scripts_node)
            else:
                nodes = create_posix_script(name, executable, scripts_node)
            return name, nodes, scripts_node, "$bindir"

        self.builder_registry.register_category("datafiles", data_section_builder)
        self.builder_registry.register_category("packages", package_builder)
        self.builder_registry.register_category("modules", module_builder)
        self.builder_registry.register_category("scripts", script_builder)

        if self.pkg.sub_directory is not None:
            sub_directory_node = self.top_node.find_node(self.pkg.sub_directory)
        else:
            sub_directory_node = None
        self._node_pkg = NodeRepresentation(run_node, self.top_node, sub_directory_node)
        self._node_pkg.update_package(pkg)

        categories = (("packages", "pythonfiles"), ("modules", "pythonfiles"), ("datafiles", "datafiles"),
                      ("scripts", "executables"), ("extensions", "extensions"),
                      ("compiled_libraries", "compiled_libraries"))
        self.outputs_registry = OutputRegistry(categories)

        self.isection_registry = ISectionRegistry()
        self.isection_registry.register_category("extensions", _generic_iregistrer)
        self.isection_registry.register_category("compiled_libraries", _generic_iregistrer)
        self.isection_registry.register_category("packages", _generic_iregistrer)
        self.isection_registry.register_category("modules", _generic_iregistrer)
        self.isection_registry.register_category("datafiles", _generic_iregistrer)
        self.isection_registry.register_category("scripts", _generic_iregistrer)

        self._current_default_section = 0

        self._meta = {}

    def register_metadata(self, name, value):
        self._meta[name] = value

    def register_category(self, category_name, category_type="pythonfiles"):
        self.outputs_registry.register_category(category_name, category_type)
        self.isection_registry.register_category(category_name, _generic_iregistrer)

    def register_outputs_simple(self, nodes, from_node=None, target_dir='$sitedir'):
        category_name = "hook_registered"
        section_name = "hook_registered%d" % self._current_default_section

        if not category_name in self.outputs_registry.categories:
            self.register_category(category_name)
        self.register_outputs(category_name, section_name, nodes, from_node, target_dir)

        self._current_default_section += 1

    def register_outputs(self, category_name, section_name, nodes, from_node=None, target_dir="$sitedir"):
        if from_node is None:
            from_node = self.build_node
        self.outputs_registry.register_outputs(category_name, section_name, nodes, from_node, target_dir)

    def _compute_extension_name(self, extension_name):
        if self.local_node is None:
            raise ValueError("Forgot to call pre_recurse ?")
        if self.local_node != self.top_node:
            parent = self.local_node.srcpath().split(os.path.sep)
            return ".".join(parent + [extension_name])
        else:
            return extension_name

    def register_builder(self, extension_name, builder):
        full_name = self._compute_extension_name(extension_name)
        self.builder_registry.register_callback("extensions", full_name, builder)

    def default_builder(self, extension, **kw):
        return self.builder_registry.default_callback(
                                        "extensions",
                                        extension,
                                        **kw)

    def tweak_extension(self, extension_name, **kw):
        def _builder(extension):
            return self.default_builder(extension, **kw)
        full_name = self._compute_extension_name(extension_name)
        return self.builder_registry.register_callback("extensions", full_name, _builder)

    def tweak_library(self, lib_name, **kw):
        def _builder(lib_name):
            return self.default_library_builder(lib_name, **kw)
        relpos = self.local_node.path_from(self.top_node)
        full_name = os.path.join(relpos, lib_name).replace(os.sep, ".")
        return self.builder_registry.register_callback("compiled_libraries", full_name, _builder)

    def default_library_builder(self, library, **kw):
        return self.builder_registry.default_callback(
                                        "compiled_libraries",
                                        library,
                                        **kw)

    def disable_extension(self, extension_name):
        def nobuild(extension):
            pass
        self.register_builder(extension_name, nobuild)

    def register_compiled_library_builder(self, clib_name, builder):
        relpos = self.local_node.path_from(self.top_node)
        full_name = os.path.join(relpos, clib_name).replace(os.sep, ".")
        self.builder_registry.register_callback("compiled_libraries", full_name, builder)

    def compile(self):
        for category in ("packages", "modules", "datafiles"):
            for name, value in self._node_pkg.iter_category(category):
                builder = self.builder_registry.builder(category, name)
                name, nodes, from_node, target_dir = builder(name, value)
                self.outputs_registry.register_outputs(category, name, nodes, from_node, target_dir)

        category = "scripts"
        for name, executable in self.pkg.executables.items():
            builder = self.builder_registry.builder(category, name)
            name, nodes, from_node, target_dir = builder(name, executable)
            self.outputs_registry.register_outputs(category, name, nodes, from_node, target_dir)

        if self.pkg.config_py:
            content = _config_content(self.retrieve_configured_scheme())
            target_node = self.build_node.make_node(self.pkg.config_py)
            target_node.parent.mkdir()
            target_node.safe_write(content)
            self.outputs_registry.register_outputs("modules", "bento_config", [target_node],
                                                   self.build_node, "$sitedir")

        if self.pkg.meta_template_files:
            target_nodes = []
            for template in self.pkg.meta_template_files:
                target_node = write_template(self.top_node, template, self.pkg, self._meta)
                target_nodes.append(target_node)
            self.outputs_registry.register_outputs("modules", "meta_from_template", target_nodes,
                                               self.build_node, "$sitedir")
    def post_compile(self):
        # Do the output_registry -> installed sections registry convertion
        section_writer = self.section_writer

        for category, name, nodes, from_node, target_dir in self.outputs_registry.iter_over_category():
            installed_category = self.outputs_registry.installed_categories[category]
            if installed_category in section_writer.sections:
                sections = section_writer.sections[installed_category]
            else:
                sections = section_writer.sections[installed_category] = {}
            registrer = self.isection_registry.registrer(category, name)
            sections[name] = registrer(installed_category, name, nodes, from_node, target_dir)

        # FIXME: this is quite stupid.
        if self.inplace:
            scheme = self.retrieve_scheme()
            scheme["prefix"] = scheme["eprefix"] = self.run_node.abspath()
            scheme["sitedir"] = self.run_node.abspath()

            if self.pkg.config_py:
                target_node = self.build_node.find_node(self.pkg.config_py)
            else:
                target_node = None

            def _install_node(category, node, from_node, target_dir):
                installed_path = subst_vars(target_dir, scheme)
                target = os.path.join(installed_path, node.path_from(from_node))
                copy_installer(node.path_from(self.run_node), target, category)

            intree = (self.top_node == self.run_node)
            if intree:
                for category, name, nodes, from_node, target_dir in self.outputs_registry.iter_over_category():
                    for node in nodes:
                        if node != target_node and node.is_bld():
                            _install_node(category, node, from_node, target_dir)
            else:
                for category, name, nodes, from_node, target_dir in self.outputs_registry.iter_over_category():
                    for node in nodes:
                        if node != target_node:
                            _install_node(category, node, from_node, target_dir)

class SdistContext(CmdContext):
    def __init__(self, global_context, cmd_args, option_context, pkg, run_node):
        super(SdistContext, self).__init__(global_context, cmd_args, option_context, pkg, run_node)
        self._meta = {}

        self._node_pkg = NodeRepresentation(run_node, self.top_node)
        self._node_pkg.update_package(pkg)

    def register_metadata(self, name, value):
        self._meta[name] = value

    def register_source_node(self, node, archive_name=None):
        """Register a node into the source distribution.

        archive_name is an optional string which will be used for the file name
        in the archive."""
        self._node_pkg._extra_source_nodes.append(node)
        if archive_name:
            self._node_pkg._aliased_source_nodes[node] = archive_name

    def configure(self):
        if self.pkg.meta_template_files:
            for template in self.pkg.meta_template_files:
                output = write_template(self.top_node, template, self.pkg, self._meta)
                self.register_source_node(output, output.bldpath())

class HelpContext(CmdContext):
    def __init__(self, *a, **kw):
        super(HelpContext, self).__init__(*a, **kw)
        self.short_descriptions = {}
        for cmd_name in self._global_context.command_names(public_only=False):
            cmd = self._global_context.retrieve_command(cmd_name)
            self.short_descriptions[cmd_name] = cmd.short_descr

    def retrieve_options_context(self, cmd_name):
        return self._global_context.retrieve_options_context(cmd_name)

    def is_options_context_registered(self, cmd_name):
        return self._global_context.is_options_context_registered(cmd_name)
