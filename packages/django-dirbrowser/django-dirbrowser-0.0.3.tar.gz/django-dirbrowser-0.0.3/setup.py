from setuptools import setup, find_packages

setup(
    name='django-dirbrowser',
    version='0.0.3',
    description='Django app For browsing a directory tree.',
    long_description=open('README.rst', 'r').read(),
    author='Ferran Pegueroles',
    author_email='ferran@pegueroles.com',
    license='GPL',
    url='http://bitbucket.org/ferranp/django-dirbrowser',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    data_files=['README.rst',
                ],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Environment :: Web Environment",
    ],
    package_data={'dirbrowser':
            ['templates/mnemosyne/*.html', 'templates/*.html*']},
    keywords='browser,django',
)
