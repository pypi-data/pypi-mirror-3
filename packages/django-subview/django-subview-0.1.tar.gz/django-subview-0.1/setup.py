from setuptools import setup

DESCRIPTION = 'Treat Django views as reusable and generic components'
LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README').read()
except:
    pass

setup(name='django-subview',
    version='0.1',
    py_modules=['urls', 'views'],
    packages=['templatetags'],
    author='Benjamin Roth',
    author_email='brstgt@gmail.com',
    url='https://github.com/brstgt',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms=['any'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
    ],
)
