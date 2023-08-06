import typespec
from distutils.core import setup

def make_readme():
    readme = ""
    with open('README.in') as f:
        readme = f.read()
    readme += "\n" + typespec.__doc__
    with open('README', 'w') as f:
        f.write(readme)
    with open('README.rst', 'w') as f:
        f.write(readme)

if __name__ == '__main__':
    make_readme()
    setup(
        name='typespec',
        version=typespec.__version__,
        packages=['typespec'],
        description='Type Specification for Function Annotations',
        long_description=typespec.__doc__,
        url="https://github.com/galini/typespec",
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
