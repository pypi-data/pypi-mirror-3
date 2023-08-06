Per Backend Metadata
====================

Backend metadata is located in each backend's `__init__.py`.

currently the following variables are used:

:repo class: the full name of the repository class in setuptools notation
:workdir class: the full name of the workdir class in setuptools notation
:workdir control: the name of the directory that identifies a workdir


Other required (but not yet implemented) fields

:repo_control: lists sets of paths that will exist in a repository
:repo features: same in green
:repo commands: required executables for repo to function propper
:repo modules: required modules to function propper

:serving_class: the full name of the reposity serving class in setuptools notation
:workdir features: stuff the repo can do like graph, merge, props
:workdir commands: required executables for repo to function propper
:workdir modules: required modules to function propper
:license: the license of the backend code (would help with avoiding license problems)
