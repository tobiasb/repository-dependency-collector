from bs4 import BeautifulSoup
import glob
from dependencyCollectorBase import DependencyCollectorBase


class NuGetPackageDependencyCollector(DependencyCollectorBase):
    def __init__(self, verbose):
        super().__init__(verbose=verbose)

    def process_nuget_package(self, repo_name, path):
        self.print_if_verbose(f'Processing NuGet package dependency file [{path}]')
        with open(path, 'r', encoding='utf-8-sig') as file:
            content = file.read()
            root = BeautifulSoup(content, 'xml')
            for element in root.findAll('package'):
                name = element['id']
                version = element['version']
                self.dependencies.append(self.build_dependency(repo_name, f'nuget', name, version))

    def process_nuget_packages(self, repo_name, path):
        for filename in glob.iglob(f'{path}/**/packages.config', recursive=True):
            self.process_nuget_package(repo_name, filename)
        return self
