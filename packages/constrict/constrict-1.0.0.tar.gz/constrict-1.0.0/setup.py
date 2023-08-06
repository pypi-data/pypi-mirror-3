globals()['IGNORE_NO_TYPESPEC'] = True

import constrict
from distutils.core import setup

def make_readme():
    readme = ""
    with open('README.in') as f:
        readme = f.read()
    readme += "\n" + constrict.__doc__
    with open('README', 'w') as f:
        f.write(readme)
    with open('README.rst', 'w') as f:
        f.write(readme)

if __name__ == '__main__':
    make_readme()
    setup(
        name='constrict',
        version=constrict.__version__,
        packages=['constrict'],
        description='Type Checking and Constraints via Function Annotations',
        long_description=constrict.__doc__,
        url="https://github.com/galini/constrict",
        author="Duncan Davis",
        author_email="duncanjdavis@gmail.com",
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Topic :: Software Development :: Libraries"
        ]
    )
