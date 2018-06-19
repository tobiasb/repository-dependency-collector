
class DependencyCollectorBase:
    def __init__(self, verbose):
        self.verbose = verbose
        self.dependencies = []

    def get_dependencies(self):
        return self.dependencies

    @staticmethod
    def build_dependency(repo_name, type, name, version):
        return {'repo': repo_name, 'type': type, 'name': name, 'version': version}

    def print_if_verbose(self, s):
        if self.verbose:
            print(s)
