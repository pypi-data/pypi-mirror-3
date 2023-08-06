try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

project_name = 'twittersync'
long_description = open('README.txt').read()

install_requires = [
        'python-dateutil',
        'Django',
]

setup(
    name='django-twittersync-extended',
    version=__import__(project_name).__version__,
    package_dir={project_name: project_name},
    packages=['twittersync'],
    description='Django app to sync Twitter stream to local DB with extendible  models. Fork of Peter Sanchez\'s Twitter sync',
    author='Martino Pizzol',
    author_email='martino@ahref.eu',
    license='BSD License',
    url='http://bitbucket.org/mpiz/django-twittersync',
    long_description=long_description,
    platforms=['any'],
    classifiers=[ 'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
    ],
    install_requires=install_requires,
)
