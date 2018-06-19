from bs4 import BeautifulSoup
import glob
from dependencyCollectorBase import DependencyCollectorBase


class MavenPomDependencyCollector(DependencyCollectorBase):
    def __init__(self, verbose):
        super().__init__(verbose=verbose)

    def process_pom(self, repo_name, root, element_name):
        for element in root.findAll(element_name):
            name = element.artifactId.string
            version = element.version.string if element.version is not None else 'N/A'
            self.get_dependencies().append(self.build_dependency(repo_name, f'maven-{element_name}', name, version))

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
            self.process_pom_file(repo_name, filename)
        return self
