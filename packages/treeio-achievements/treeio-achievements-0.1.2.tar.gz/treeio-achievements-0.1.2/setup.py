from setuptools import setup, find_packages

setup(
    name='treeio-achievements',
    version='0.1.2',
    url = 'http://github.com/pascalmouret/treeio-achievements',
    license = 'BSD',
    platforms=['OS Independent'],
    description = "A module for treeio that lets you hand out achievements.",
    long_description = open('README.rst').read(),
    author = 'Pascal Mouret',
    author_email = 'pascal.mouret@me.com',
    packages=find_packages(),
    install_requires = (),
    include_package_data=True,
    zip_safe=False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)