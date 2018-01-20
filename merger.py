from shutil import copy2
from os import path, remove
from random import randint

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

f1 = WorkspaceReader("/Users/lorabit/Develop/java/generate_workspace.bzl")
merger = WorkspaceMerger()
merger.merge(f1)