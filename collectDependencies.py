import getpass
import json
import argparse

from azureFunctionPackageDependencyCollector import AzureFunctionPackageDependencyCollector
from mavenPomDependencyCollector import MavenPomDependencyCollector
from nuGetPackageDependencyCollector import NuGetPackageDependencyCollector
from repoCloner import RepoCloner

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

for repo in repositories:
    name = repo["name"]
    if verbose:
        print(f'Processing {name} (branch: {repo["branch"]})')
    repo_path = f'tmp/{name}'

    if not noclone:
        RepoCloner(verbose=verbose).clone_repo(args.username, password, args.host, name, repo["branch"], repo_path)
    dependencies.extend(MavenPomDependencyCollector(verbose=verbose).process_poms(name, repo_path).get_dependencies())
    dependencies.extend(AzureFunctionPackageDependencyCollector(verbose=verbose).process_azure_function_packages(name, repo_path).dependencies)
    dependencies.extend(NuGetPackageDependencyCollector(verbose=verbose).process_nuget_packages(name, repo_path).dependencies)

if outformat == 'json':
    print('[\n')
    for dependency in dependencies:
        print(f'{dependency}')
    print('\n]')

if outformat == 'csv':
    print('Repository,Type,Name,Version')
    for dependency in dependencies:
        print(f'{dependency["repo"]},{dependency["type"]},{dependency["name"]},="{dependency["version"]}"')
