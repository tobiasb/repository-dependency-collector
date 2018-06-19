import glob
from dependencyCollectorBase import DependencyCollectorBase
import json


class AzureFunctionPackageDependencyCollector(DependencyCollectorBase):
    def __init__(self, verbose):
        super().__init__(verbose=verbose)

    def process_azure_function_package(self, repo_name, path):
        self.print_if_verbose(f'Processing Azure Function package [{path}]')
        with open(path, 'r') as file:
            package_json = json.loads(file.read())
            if 'dependencies' in package_json:
                deps = package_json['dependencies']
                for key in deps:
                    self.dependencies.append(self.build_dependency(repo_name, 'function', key, deps[key]))

    def process_azure_function_packages(self, repo_name, path):
        for filename in glob.iglob(f'{path}/**/package.json', recursive=True):
            self.process_azure_function_package(repo_name, filename)
        return self
