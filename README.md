# Repository Dependency Collector

A [sloppy](https://www.youtube.com/watch?v=Jd8ulMb6_ls) dependency collector. Goal: Automate a one time task that I would have otherwise done manually. Share so that my co-workers won't have to do it either.

Given a base partial base URI for Git repositories and a list of repository names under that base path, collect various project dependencies and output them in JSON or CSV. Currently supported:

* Maven plugins
* Maven dependencies
* JavaScript Azure Functions
* DotNet NuGet dependencies

Repositories will be cloned locally and then analysed statically.

# Requirements

* Python 3.x

Packages other than the ones explicitly required in the code are

* lxml

# Usage

Specify repositories relative to the base url in a `repofile`. The format is the following:


```
[
  {
    "name": "path-to/the-repository",
    "branch": "dev"
  },
  {
    "name": "another-repository",
    "branch": "master"
  },
  ...
]
```

Clone and analyse repositories, output array of dependencies in a JSON file:

`python collectDependencies.py --host gitlab.corporate-gitlab-server.com --username johndoe --verbose --repofile=repositories.json --outfile=dependencies.json`

This will clone and analyse the following repositories:

 * https://gitlab.corporate-gitlab-server.com/path-to/the-repository.git
 * https://gitlab.corporate-gitlab-server.com/another-repository.git

Work with local repositories (in `/tmp` folder) without cloning them again and output dependencies in CSV

`python collectDependencies.py --noclone --repofile=repositories.json --outformat=csv --outfile=dependencies.csv`
