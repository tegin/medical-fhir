import pathlib
import os
from setuptools_odoo.manifest import read_manifest
import setuptools

repo_name = "medical-fhir"
branch = "12.0"
organization = "tegin"


path = str(pathlib.Path(__file__).absolute().parent)
data = os.listdir(path)

to_process = {}
new_data = []
for d in data:
    if d in ['.github', 'setup', '.git', '__pycache__', "pip-egg-info"]:
        continue
    if os.path.isfile(os.path.join(path, d)):
        continue
    manifest = read_manifest(os.path.join(path, "..", d))
    to_process[d] = manifest.get("depends", [])
    new_data.append(d)

data = new_data
pending_data = new_data.copy()
install_requires = ["setuptools", "setuptools_scm>=2.1,!=4.0.0", "setuptools-odoo"]
dependency_links = []
while pending_data:
    new_pending_data = []
    for d in pending_data:
        if any(depend in pending_data for depend in to_process[d]):
            new_pending_data.append(d)
            continue
        install_requires.append(
            "odoo12-addon-{module}@git+https://github.com/{organization}/{repo_name}.git@{branch}#subdirectory=setup/{module}".format(
                module=d, organization=organization, repo_name=repo_name, branch=branch
            ))
        dependency_links.append(
            "git+https://github.com/{organization}/{repo_name}.git@{branch}#subdirectory=setup/{module}".format(
                module=d, organization=organization, repo_name=repo_name, branch=branch
            ))
    pending_data = new_pending_data

setuptools.setup(
    name="repo_odoo%s_%s_%s" % (branch, organization, repo_name),
    version=branch,
    description=repo_name,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: " "GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX",  # because we use symlinks
        "Programming Language :: Python",
        "Framework :: Odoo",
    ],
    packages=[],
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    setup_requires=["setuptools-scm!=4.0.0"],
)
