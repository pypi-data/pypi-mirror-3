'''
Copyright 2012 Research Institute eAustria

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Marian Neagul <marian@ieat.ro>
@contact: marian@ieat.ro
@copyright: 2012 Research Institute eAustria
'''

import re
import os
import json
import pipes
import copy
import hashlib
import logging
import tarfile
import fnmatch
import zipfile
import StringIO

from dric import Downloader

SPEC_FILE_NAME = "spec.json"
SPEC_FILE_VERSION = "0.1"

DEFAULT_CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".me2pack")

VARIABLE_EXPANSION_RE = re.compile(r"(?P<variable>\${(?P<path>((\w|\-)+)(\.(\w|\-)+)*)(\|(?P<transform>\w+))?})")
VARIABLE_EXPANSION_TRANSFORM_HANDLERS = {'sh': pipes.quote}

class VariableExpansionError(Exception):
    pass

class PropertyNotFound(VariableExpansionError):
    pass

class InvalidProperty(VariableExpansionError):
    pass

class SpecificationError(Exception):
    pass

class UnsupportedSpecificationError(SpecificationError):
    pass

def expand_variables(input_string, tree, default = None, panic_if_not_found = True, nesting_level = 0, max_nesting_level = 15):
    _nest_level = nesting_level
    if _nest_level > max_nesting_level:
        raise VariableExpansionError("Nesting level above configured limit %d" % max_nesting_level)
    def replace(match):

        _group_dict = match.groupdict()
        _path = _group_dict['path']
        if 'transform' in _group_dict:
            _transform = _group_dict['transform']
            if _transform is None:
                _escape = str
            else:
                if _transform not in VARIABLE_EXPANSION_TRANSFORM_HANDLERS:
                    raise VariableExpansionError("Transform `%s` not found, valid transforms: %s" % (_transform, VARIABLE_EXPANSION_TRANSFORM_HANDLERS.keys()))
                _escape = VARIABLE_EXPANSION_TRANSFORM_HANDLERS[_transform]
        else:
            _escape = str
        _obj = tree
        path_elements = _path.split(".")

        terminal = path_elements[-1]
        parents = path_elements[:-1]

        _obj = tree
        for node in parents: # Validate the parents
            if node not in _obj:
                raise PropertyNotFound("Property %s not found (%s)" % (_path, node))
            if not isinstance(_obj[node], dict): # All parent should be dict's
                raise InvalidProperty("Property %s could not be expanded. Node %s is not a dictionary !" % (_path, node))
            _obj = _obj[node]

        if terminal not in _obj:
            raise PropertyNotFound("Property %s not found" % _path)

        _obj = _obj[terminal]

        if isinstance(_obj, basestring) or isinstance(_obj, int) or isinstance(_obj, float):
            return _escape(str(_obj))
        else:
            raise InvalidProperty("Property %s is not a string" % _path)


    new_string, num_subs = VARIABLE_EXPANSION_RE.subn(replace, input_string)
    if num_subs == 0:
        return new_string
    else:
        return expand_variables(new_string, tree, default, panic_if_not_found, nesting_level + 1, max_nesting_level)

def sha1file(fname):
    m = hashlib.sha1()
    with open(fname, "rb") as f:
        while True:
            buf = f.read(512)
            if len(buf) <= 0:
                break
            m.update(buf)

    return m.hexdigest()




def validate_spec(spec):
    if "spec-version" not in spec:
        raise SpecificationError("Missing specification")
    if spec["spec-version"] != SPEC_FILE_VERSION:
        raise UnsupportedSpecificationError("Specification version %s is different then the supported one %s" % (spec["spec-version"], SPEC_FILE_VERSION))
    if "bundle" not in spec:
        raise SpecificationError("Missing field `bundle`!")

class PackageBuilder(object):
    log = logging.getLogger("PackageBuilder")
    def __init__(self, config = {}):
        self.config = copy.deepcopy(config)
        self.downloader = Downloader()
        self.validate()

    def validate(self):
        validate_spec(self.config)
        if "assembly" not in self.config:
            raise SpecificationError("Missing assembly specification")

    def downloadArtifacts(self):
        assemblySpec = self.config["assembly"]
        download_registry = self.config["me2"]["build"]["download"]
        download_dir = expand_variables("${me2.build.download_dir}", self.config)

        if not 'fetch' in assemblySpec:
            self.log.debug('Nothing to download')
            return
        else:
            self.log.debug("Download dir: %s", download_dir)

        if not os.path.exists(download_dir):
            self.log.info("Creating download directory: %s", download_dir)
            os.makedirs(download_dir)
        fetchList = assemblySpec['fetch']
        for entry in fetchList:
            name = entry["name"]
            if name in download_registry: # Already registered, should not happen
                self.log.error("Artifact %s marked already as downloaded!", name)
                continue
            url = expand_variables(entry["url"], self.config)
            destination = expand_variables(entry["destination"], self.config)
            self.log.info("Downloading %s -> %s", url, destination)
            self.downloader.fetch(url, destination)
            download_registry[name] = {'file': destination}
            self.log.info("Download finished!")
            if "action" in entry:
                self.log.info("Running post download actions")
                self.do_post_download(name, entry)

    def do_post_download(self, name, entry):
        action = entry["action"]
        operation = action["operation"]
        input_file = self.config["me2"]["build"]["download"][name]['file']
        if operation == "extract":
            extract_dir = expand_variables(action['destination'], self.config)
            self.extract(input_file, extract_dir, options = action)
        else:
            self.log.critical("Operation %s is not supported!", operation)


    def extract(self, infile, outdir, options):
        log = self.log.getChild("extract")
        archive_type = options['type']
        if archive_type not in ["tgz", "tbz", "tar.gz", "tar.bz2"]:
            log.critical("Unsupport archive type: %s", archive_type)
            return
        log.info("Extracting file %s into directory %s", infile, outdir)

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        exclude = options["exclude"]
        tar = tarfile.open(infile, "r:*")
        for item in tar:
            if any(map(lambda x: fnmatch.fnmatchcase (item.name, x), exclude)):
                log.info("Ignoring file %s", item.name)
                continue
            try:
                log.debug("Extracting %s", item.name)
                tar.extract(item.name, path = outdir)
            except EnvironmentError, e:
                log.warn("Failed to extract %s: %s", item.name, e)
        tar.close()

    def repack(self, task):
        log = self.log.getChild("repack")
        infile = expand_variables(task['source'], self.config)
        destfile = expand_variables(task['destination'], self.config)
        compresion_type = expand_variables(task['compression-type'], self.config)
        exclude = task['exclude']
        inject = task['inject']

        if compresion_type is None:
            compression_flag = ""
        elif compresion_type not in ["gz", "bz2", ""]:
            raise SpecificationError("Unsupported compression format '%s'" % compresion_type)
        else:
            compression_flag = compresion_type
        if os.path.exists(destfile):
            os.remove(destfile)
        #ToDo: check that the file exists 
        in_tar = tarfile.open(infile, "r:*")
        out_tar = tarfile.open(destfile, "w:%s" % compression_flag, format = tarfile.GNU_FORMAT)
        try:
            # Copy between archives
            for item in in_tar.getmembers():
                if any(map(lambda x: fnmatch.fnmatchcase (item.name, x), exclude)):
                    log.debug("Ignoring file %s", item.name)
                    continue

                if item.isfile():
                    log.debug("Adding regular file %s", item.name)
                    fle = in_tar.extractfile(item)
                    out_tar.addfile(item, fle)
                else:
                    log.debug("Adding special file %s", item.name)
                    out_tar.addfile(item)
            # Inject files
            for entry in inject:
                raw_source, destination = entry
                source = expand_variables(raw_source, self.config)
                destination = expand_variables(destination, self.config)
                if not os.path.exists(source):
                    raise SpecificationError("File %s (%s) does not exist" % (raw_source, source))
                out_tar.add(source, destination)

        finally:
            out_tar.close()
            in_tar.close()


    def runTasks(self):
        log = self.log.getChild("runTasks")
        tasks_spec = self.config["assembly"]['tasks']
        for task in tasks_spec:
            operation = task["operation"]
            if operation == "repack":
                self.repack(task)
            else:
                log.critical("Operation %s is not supported", operation)

    def saveDescriptor(self):
        bundle_dir = expand_variables("${me2.build.bundle_dir}", self.config)
        desc_file = os.path.join(bundle_dir, "buildspec.json")
        self.log.debug("Saving build time descriptor to %s", desc_file)
        with open(desc_file, "w") as f:
            json.dump(self.config, f, sort_keys = True, indent = 4)


    def createBundle(self):
        log = self.log.getChild("createBundle")
        bundle_name = expand_variables("${me2.bundle_name}", self.config)
        bundle_file = expand_variables("${me2.build.bundle}", self.config)
        bundle_dir = expand_variables("${me2.build.bundle_dir}", self.config)
        log.info("Destination bundle: %s", bundle_file)
        if os.path.exists(bundle_file):
            log.warn("bundle file exists and it will be removed: %s", bundle_file)
            os.remove(bundle_file)


        with zipfile.ZipFile(bundle_file, 'w', allowZip64 = True, compression = zipfile.ZIP_DEFLATED) as bundle:
            bundle.comment = "mOSAIC Bundle for %s" % bundle_name
            manifest = StringIO.StringIO()
            for dirpath, dirnames, filenames in os.walk(bundle_dir):
                arc_dir = os.path.relpath(os.path.abspath(dirpath), bundle_dir)
                for dir_file in filenames:
                    efective_path = os.path.join(dirpath, dir_file)
                    arc_path = os.path.join(arc_dir, dir_file)
                    if not os.path.exists(efective_path):
                        log.warn("File %s does not exist !", efective_path)
                        continue
                    fsize = os.path.getsize(efective_path)
                    fhash = sha1file(efective_path)
                    manifest.write("%(fname)s\t%(fsize)d\t%(fhash)s\n" % {'fname': arc_path, 'fsize': fsize, 'fhash': fhash})
                    bundle.write(efective_path, arc_path)
            bundle.writestr("./MANIFEST.mf", manifest.getvalue())
            manifest.close()

        return bundle_file

    def build(self):
        self.make_dirs()
        self.log.info("Validateing specification")
        self.validate()
        self.log.info("Downloading Artifacts")
        self.downloadArtifacts()
        self.log.info("Running tasks")
        self.runTasks()
        self.log.info("Saving build time descriptor")
        self.saveDescriptor()
        self.log.info("Creating bundle")
        self.createBundle()

    def make_dirs(self):
        bundle_dir = expand_variables("${me2.build.bundle_dir}", self.config)
        if not os.path.exists(bundle_dir):
            os.makedirs(bundle_dir)

class Packager(object):
    log = logging.getLogger("Packager")
    def __init__(self, default_config = DEFAULT_CONFIG_FILE):
        if os.path.exists(default_config):
            self.log.info("Loading config from: %s", default_config)
            self.config = json.load(open(default_config))
        else:
            self.log.debug("Starting with empty config")
            self.config = {'me2': {}}

        self.config_file = os.path.join(os.getcwd(), SPEC_FILE_NAME)
        self.config.update(json.load(open(self.config_file)))
        me2_config = self.config["me2"]
        me2_config['cwd'] = os.getcwd()
        me2_config['bundle_name'] = "${bundle.package-id}-${bundle.version}-${bundle.classifier}"

    def __call__(self, options):
        self.handle(options)

    def setup_parser(self, parser):
        parser.add_argument('--directory', type = str, default = ".", help = "Base directory of bundle")
        subparsers = parser.add_subparsers(help = 'commands')
        validate_parser = subparsers.add_parser('validate', help = 'Validate a package')
        validate_parser.set_defaults(package_command = self.validate)

        build_parser = subparsers.add_parser('build', help = 'Validate a package')
        build_parser.add_argument("--buildDir", type = str, default = "${me2.cwd}/me2-build")
        build_parser.set_defaults(package_command = self.build)

        extract_parser = subparsers.add_parser('extract', help = 'extract a package')
        extract_parser.add_argument("--bundle", type = str, help = "The bundle file that should be extracted")
        extract_parser.set_defaults(package_command = self.extract)

    def validate(self, options):
        raise NotImplementedError()

    def extract(self, options):
        raise NotImplementedError()

    def build(self, options):
        config = copy.deepcopy(self.config)
        if 'build' in config['me2']:
            build_config = config['me2']['build']
        else:
            build_config = {}
            config['me2']['build'] = build_config

        build_config['build_dir'] = options.buildDir
        build_config['bundle'] = os.path.join("${me2.build.build_dir}", "${me2.bundle_name}.mb")
        build_config['download_dir'] = os.path.join("${me2.build.build_dir}", "download")
        build_config["extract_dir"] = os.path.join("${me2.build.build_dir}", "extract")
        build_config["bundle_dir"] = os.path.join("${me2.build.build_dir}", "bundle")
        build_config["resource_dir"] = os.path.join("${me2.cwd}", "resources")
        if 'download' not in build_config:
            build_config["download"] = {}

        builder = PackageBuilder(config = config)
        builder.build()

    def handle(self, options):
        options.package_command(options)


