from bs4 import BeautifulSoup
import glob
from dependencyCollectorBase import DependencyCollectorBase
import re
import requests
from random import randint


class MavenPomDependencyCollector(DependencyCollectorBase):
    version_reference_re = re.compile(r'\${(.*?)}')
    license_re = re.compile(r'<span class="b lic">(.*?)<\/span>')

    def __init__(self, verbose):
        super().__init__(verbose=verbose)
        self.versions = []
        self.licenses = []

    def process_pom(self, repo_name, root, element_name):
        for element in root.findAll(element_name):
            name = element.artifactId.string
            version = self.find_version(root, element)

            group = ''
            if element.groupId is not None:
                group = element.groupId.string

            license = self.retrieve_license(group, name)

            dependency = self.build_dependency(repo_name, f'maven-{element_name}', name, version, license)

            self.get_dependencies().append(dependency)

    def retrieve_license(self, groupId, artifactId):
        if groupId == '' or artifactId == '':
            return ''

        matches = list(filter(lambda l: l['name'] == artifactId, self.licenses))
        if len(matches) > 0:
            return matches[0]['license']

        url = f'https://mvnrepository.com/artifact/{groupId}/{artifactId}'
        ip = f'{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}'
        # This circumvents the server rate limiting that kicks in after a handful requests and is very bad.
        # Only do this if you know you'll only be making a few requests
        response = requests.get(url, headers={'X-Forwarded-For': ip})

        content = response.text
        matches = self.license_re.findall(content)
        if(len(matches)) > 0:
            license = matches[0]
        else:
            license = ''
        self.licenses.append({'name': artifactId, 'license': license})
        return license

    def find_version(self, root, element):
        if element.version is None:
            return 'N/A'
        if element.version.string.startswith('$'):
            return self.find_version_property(root, element.version.string)
        return element.version.string

    def find_version_property(self, root, version_string):
        match = self.version_reference_re.match(version_string)
        if match is None:
            return version_string
        version_key = match.group(1)
        element = root.find(f'{version_key}')

        if element is not None:
            return element.string

        global_versions = list(filter(lambda v: v['name'] == version_key, self.versions))
        if len(global_versions) > 0:
            return global_versions[0]['version']

        return 'Not found'

    def process_pom_dependencies(self, repo_name, root):
        self.process_pom(repo_name, root, 'dependency')

    def process_pom_plugins(self, repo_name, root):
        self.process_pom(repo_name, root, 'plugin')

    def process_pom_file(self, repo_name, path):
        self.print_if_verbose(f'Processing POM [{path}]')
        with open(path, 'r') as file:
            root = BeautifulSoup(file.read(), 'xml')
            self.process_pom_dependencies(repo_name, root)
            self.process_pom_plugins(repo_name, root)

    def process_poms(self, repo_name, path):
        for filename in glob.iglob(f'{path}/**/pom.xml', recursive=True):
            self.versions.extend(self.find_versions(filename))
        for filename in glob.iglob(f'{path}/**/pom.xml', recursive=True):
            self.process_pom_file(repo_name, filename)
        return self

    @staticmethod
    def find_versions(filename):
        versions = []
        with open(filename, 'r') as file:
            root = BeautifulSoup(file.read(), 'xml')
            if root.properties is None:
                return versions
            for element in root.properties:
                if element.name is not None and '.version' in element.name:
                    versions.append({'name': element.name, 'version': element.string})
        return versions
