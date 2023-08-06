from setuptools import setup

long_description = """
Simple library for complex projects with a need for a
simple and persistent configurations.
"""

def main():
    setup(
        name='configmgr',
        description='simple configuration management',
        long_description=long_description,
        version='0.0',
        author='grantor61',
        author_email='grantor61@gmail.com',
        url='https://bitbucket.org/grantor61/configmgr',
        license='MIT license',
        platforms=['linux',  'win32'],
        install_requires=['appdirs', 'py'],
        classifiers=['Development Status :: 4 - Beta',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: MIT License',
                     'Operating System :: POSIX',
                     'Operating System :: Microsoft :: Windows',
                     'Topic :: Software Development :: Libraries',
                     'Topic :: Utilities',
                     'Programming Language :: Python'],
        py_modules=['configmgr'],
    )


if __name__ == '__main__':
    main()
