from distutils.core import setup
import re

__version__ = '0.0.4'

def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)

    return requirements

def parse_dependency_links(file_name):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'\s*-[ef]\s+', line):
            dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))

    return dependency_links

setup(
    name = 'checkout-by-amazon',
    version = __version__,
    packages = ['cba',],
    license = 'GNU Lesser General Public License v. 3.0',
    long_description = open('README').read(),
    url = 'https://bitbucket.org/bluejeansummer/cba',
    author = 'Nick Meharry',
    author_email = 'nick@nickmeharry.com',
    install_requires = parse_requirements('requirements.txt'),
    dependency_links = parse_dependency_links('requirements.txt'),
)
