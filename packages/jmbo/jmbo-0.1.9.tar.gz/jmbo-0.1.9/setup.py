from setuptools import setup, find_packages

setup(
    name='jmbo',
    version='0.1.9',
    description='Jmbo base app.',
    long_description = open('README.rst', 'r').read() + open('AUTHORS.rst', 'r').read() + open('CHANGELOG.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://www.jmbo.org',
    packages = find_packages(),
    dependency_links = [
        'http://dist.plone.org/thirdparty/',
        'http://github.com/praekelt/django-photologue/tarball/2.6.praekelt#egg=django-photologue-2.6.praekelt',
    ],
    install_requires = [
        'PIL',
        'django',
        'django-category',
        'django-photologue==2.6.praekelt',
        'django-preferences',
        'django-publisher',
        'django-likes',
    ],
    include_package_data=True,
    tests_require=[
        'django-setuptest>=0.0.6',
    ],
    test_suite="setuptest.SetupTestSuite",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)
