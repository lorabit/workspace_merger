from shutil import copy2
from os import path, remove
from random import randint
import argparse


class WorkspaceReader:
    def __init__(self, fname):
        self.maven_jars = []
        self.java_libraries = []
        module_name = 'tmp'+str(randint(1000,9999))
        new_name = path.join(path.dirname(__file__), module_name +'.py')
        copy2(fname, new_name)
        workspace = __import__(module_name)
        workspace.native = self
        workspace.generated_java_libraries()
        workspace.generated_maven_jars()
        remove(new_name)

    def maven_jar(self, name = None, artifact = None, sha1 = None):
        self.maven_jars.append(
            {
                "name": name,
                "artifact": artifact,
                "sha1" : sha1
            }
        )

    def java_library(self, name = None, visibility = [], exports = [], runtime_deps = []):
        self.java_libraries.append(
            {
                "name": name,
                "visibility": visibility,
                "exports": exports,
                "runtime_deps": runtime_deps
            }
        )

class WorkspaceMerger:
    def __init__(self):
        self.maven_jars = {}
        self.java_libraries = {}

    def merge(self, reader):
        for maven_jar in reader.maven_jars:
            self.maven_jars[maven_jar["name"]] = maven_jar

        for java_library in reader.java_libraries:
            self.java_libraries[java_library["name"]] = java_library

    def export(self, fname):
        def format_array(array, indent = 6):
            if len(array) == 0:
                return "[]"
            if len(array) == 1:
                return "[\"%s\"]" % (array[0])
            ret = [((" "*(indent+4)+"\"%s\",\n") %(i,)) for i in array]
            return "[\n"+"".join(ret)+" "*indent+"]"
        with open(fname, 'w') as f:
            f.write("# The following dependencies were calculated by workspace_merger. \n# https://github.com/lorabit/workspace_merger\n\n\n")
            f.write("def generated_maven_jars():\n")
            for maven_jar_name in self.maven_jars:
                maven_jar = self.maven_jars[maven_jar_name]
                f.write("  native.maven_jar(\n")
                f.write("      name = \"%s\",\n" % (maven_jar["name"],))
                if maven_jar.get("artifact")!=None:
                    f.write("      artifact = \"%s\",\n" % (maven_jar["artifact"]))
                if maven_jar.get("sha1")!=None:
                    f.write("      sha1 = \"%s\",\n" % (maven_jar["sha1"]))
                f.write("  )\n\n")

            f.write("def generated_java_libraries():\n")
            for java_library_name in self.java_libraries:
                java_library = self.java_libraries[java_library_name]
                f.write("  native.java_library(\n")
                f.write("      name = \"%s\",\n" % (java_library["name"],))
                if java_library.get("visibility")!=None:
                    f.write("      visibility = %s,\n" % (format_array(java_library["visibility"])))
                if java_library.get("exports")!=None:
                    f.write("      exports = %s,\n" % (format_array(java_library["exports"])))
                if java_library.get("runtime_deps")!=None:
                    f.write("      runtime_deps = %s,\n" % (format_array(java_library["runtime_deps"])))
                f.write("  )\n\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Log-Bilinear model for relation extraction.')
    _arg = parser.add_argument
    _arg(
        '-s', '--source', 
        type=str, 
        action='store',
        metavar='PATH', 
        help='The source bzl file path.', 
        required = True
    )
    _arg(
        '-d', '--destination', 
        type=str, 
        action='store',
        metavar='PATH', 
        help='The destination bzl file path. If the file does not exist, a new file will be created.', 
        required = True
    )
    args = parser.parse_args()
    if not path.isfile(args.source):
        print("%s does not exist.\n" % (args.source))
        exit(0)
    merger = WorkspaceMerger()
    if path.isfile(args.destination):
        dest = WorkspaceReader(args.destination)
        merger.merge(dest)
    source = WorkspaceReader(args.source)
    merger.merge(source)
    merger.export(args.destination)
    print('Done!')
