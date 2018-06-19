from urllib.parse import quote
import subprocess
import os


class RepoCloner:
    def __init__(self, verbose):
        self.verbose = verbose

    def print_if_verbose(self, s):
        if self.verbose:
            print(s)

    def run(self, command):
        with open(os.devnull, 'w') as devnull:
            if self.verbose:
                subprocess.run(command, shell=True)
            else:
                subprocess.run(command, shell=True, stdout=devnull, stderr=subprocess.STDOUT)

    def clone_repo(self, username, password, host, name, branch, path):
        self.print_if_verbose(f'Cloning [https://{username}:*********@{host}/{name}.git]')
        git_url = f'https://{username}:{quote(password)}@{host}/{name}.git'
        self.run(f'set GIT_SSL_NO_VERIFY=true && git clone {git_url} {path}')
        if branch != 'master':
            self.print_if_verbose(f'Checkout branch [{branch}]')
            self.run(f'cd {path} && git checkout {branch}')
