from setuptools import setup, find_packages

setup(
    version = '0.8.0-13',
    description = 'PyBB Modified, Modified. Django forum application modified to work with other languages than Russian and English, as well as working with easy_thumbnails',
    long_description = open('README.rst').read(),
    author = 'Trygve Bertelsen Wiig',
    author_email = 'trygvebw@gmail.com',
    name = 'pybbm-tbw',
    packages = find_packages(),
    include_package_data = True,
    package_data = {'': ['pybb/templates', 'pybb/static']},
    install_requires = [
            'django',
            'markdown',
            'postmarkup',
            'south',
            'pytils',
            'django-annoying',
            'easy_thumbnails',
            'django-pure-pagination'
            ],

    license = "BSD",
    keywords = "django application forum board",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
