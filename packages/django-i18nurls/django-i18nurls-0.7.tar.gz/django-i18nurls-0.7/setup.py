from distutils.core import setup


setup(
    name='django-i18nurls',
    version='0.7',
    author='Orne Brocaar',
    author_email='info@brocaar.com',
    url='http://github.com/brocaar/django-i18nurls',
    description='Translate URL patterns and prefix URLs with language-code.',
    long_description=open('README.rst').read(),
    license='BSD',
    packages=[
        'i18nurls',
        'i18nurls.tests',
    ],
    package_data={
        'i18nurls': [
            'templates/i18nurls/*',
            'locale/en/LC_MESSAGES/*',
            'locale/nl/LC_MESSAGES/*'
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
