from bs4 import BeautifulSoup
import glob
from dependencyCollectorBase import DependencyCollectorBase
import re
import requests
from random import randint


class NuGetPackageDependencyCollector(DependencyCollectorBase):
    license_re = re.compile(r'<i class="ms-Icon ms-Icon--Certificate".*?<a href="(.*?)" data-track="outbound-license-url.*?>(.*?)<', re.S)

    def __init__(self, verbose):
        super().__init__(verbose=verbose)
        self.licenses = []

    def process_nuget_package(self, repo_name, path):
        self.print_if_verbose(f'Processing NuGet package dependency file [{path}]')
        with open(path, 'r', encoding='utf-8-sig') as file:
            content = file.read()
            root = BeautifulSoup(content, 'xml')
            for element in root.findAll('package'):
                name = element['id']
                version = element['version']
                license = self.retrieve_license(name)
                self.dependencies.append(self.build_dependency(repo_name, f'nuget', name, version, license))

    def process_nuget_packages(self, repo_name, path):
        for filename in glob.iglob(f'{path}/**/packages.config', recursive=True):
            self.process_nuget_package(repo_name, filename)
        return self

    def retrieve_license(self, name):
        if name == '':
            return ''

        matches = list(filter(lambda l: l['name'] == name, self.licenses))
        if len(matches) > 0:
            return matches[0]['license']

        url = f'https://www.nuget.org/packages/{name}'
        response = requests.get(url)
        content = response.text
        matches = self.license_re.findall(content)
        if(len(matches)) > 0:
            license = matches[0][1].strip()
            link = matches[0][0]
            license = f'{license} ({link})'
        else:
            license = ''
        self.licenses.append({'name': name, 'license': license})
        return license
