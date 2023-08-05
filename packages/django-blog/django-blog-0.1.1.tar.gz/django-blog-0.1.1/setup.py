from setuptools import setup, find_packages

setup(
    name='django-blog',
    version='0.1.1',
    author='Michael Samoylov',
    author_email='mike@djangoware.com',
    url='http://github.com/djangoware/django-blog',
    description = 'A simple blog app',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
