import os
import getpass
from urllib.parse import quote
import subprocess
import glob
from bs4 import BeautifulSoup  # requires lxml
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--username')
parser.add_argument('--noclone', action='store_true')
parser.add_argument('--verbose', action='store_true')
parser.add_argument('--outformat')
parser.add_argument('--host')
parser.add_argument('--repofile')
args = parser.parse_args()

noclone = args.noclone
verbose = args.verbose
outformat = 'json' if args.outformat is None else args.outformat

if args.repofile is None:
    print('Missing argument: --repofile')
    exit()

if not noclone:
    if args.username is None:
        print('Missing argument: --username')
        exit()
    if args.host is None:
        print('Missing argument: --host')
        exit()

password = ''
if not noclone:
    password = getpass.getpass(prompt='Git password:')

repositories = []
with open(args.repofile, 'r') as repofile:
    repositories = json.loads(repofile.read())

dependencies = []


def run(command):
    with open(os.devnull, 'w') as devnull:
        if verbose:
            subprocess.run(command, shell=True)
        else:
            subprocess.run(command, shell=True, stdout=devnull, stderr=subprocess.STDOUT)


def print_if_verbose(s):
    if verbose:
        print(s)


def clone_repo(name, branch, path):
    print_if_verbose(f'Cloning [https://{args.username}:*********@{args.host}/{name}.git]')
    git_url = f'https://{args.username}:{quote(password)}@{args.host}/{name}.git'
    run(f'set GIT_SSL_NO_VERIFY=true && git clone {git_url} {path}')
    if repo['branch'] != 'master':
        print_if_verbose(f'Checkout branch [{branch}]')
        run(f'cd {path} && git checkout {branch}')


def build_dependency(repo_name, type, name, version):
    return {'repo': repo_name, 'type': type, 'name': name, 'version': version}


def process_pom(repo_name, root, element_name):
    for element in root.findAll(element_name):
        name = element.artifactId.string
        version = element.version.string if element.version is not None else 'N/A'
        dependencies.append(build_dependency(repo_name, f'maven-{element_name}', name, version))


def process_pom_dependencies(repo_name, root):
    process_pom(repo_name, root, 'dependency')


def process_pom_plugins(repo_name, root):
    process_pom(repo_name, root, 'plugin')


def process_pom_file(repo_name, path):
    print_if_verbose(f'Processing POM [{path}]')
    with open(path, 'r') as file:
        root = BeautifulSoup(file.read(), 'xml')
        process_pom_dependencies(repo_name, root)
        process_pom_plugins(repo_name, root)


def process_poms(repo_name, path):
    for filename in glob.iglob(f'{path}/**/pom.xml', recursive=True):
        process_pom_file(repo_name, filename)


def process_azure_function_package(repo_name, path):
    print_if_verbose(f'Processing Azure Function package [{path}]')
    with open(path, 'r') as file:
        package_json = json.loads(file.read())
        if 'dependencies' in package_json:
            deps = package_json['dependencies']
            for key in deps:
                dependencies.append(build_dependency(repo_name, 'function', key, deps[key]))


def process_azure_function_packages(repo_name, path):
    for filename in glob.iglob(f'{path}/**/package.json', recursive=True):
        process_azure_function_package(repo_name, filename)


def process_nuget_package(repo_name, path):
    print_if_verbose(f'Processing NuGet package dependency file [{path}]')
    with open(path, 'r', encoding='utf-8-sig') as file:
        content = file.read()
        root = BeautifulSoup(content, 'xml')
        for element in root.findAll('package'):
            name = element['id']
            version = element['version']
            dependencies.append(build_dependency(repo_name, f'nuget', name, version))


def process_nuget_packages(repo_name, path):
    for filename in glob.iglob(f'{path}/**/packages.config', recursive=True):
        process_nuget_package(repo_name, filename)


for repo in repositories:
    name = repo["name"]
    print_if_verbose(f'Processing {name} (branch: {repo["branch"]})')
    repo_path = f'tmp/{name}'

    if not noclone:
        clone_repo(name, repo["branch"], repo_path)
    process_poms(name, repo_path)
    process_azure_function_packages(name, repo_path)
    process_nuget_packages(name, repo_path)

if outformat == 'json':
    print('[\n')
    for dependency in dependencies:
        print(f'{dependency}')
    print('\n]')

if outformat == 'csv':
    print('Repository,Type,Name,Version')
    for dependency in dependencies:
        print(f'{dependency["repo"]},{dependency["type"]},{dependency["name"]},="{dependency["version"]}"')
