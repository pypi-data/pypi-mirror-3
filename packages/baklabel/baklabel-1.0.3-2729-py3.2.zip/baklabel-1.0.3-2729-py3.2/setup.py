from distutils.core import setup
from baklabel import baklabel
"""
We want to leave version as is for sdist but include pyver
when doing a bdist_wininst. So we need an external reference
so we know what is happening. Hence, the calling software will
write pyver to pyver.run and we will read it here.
"""

pyver = ''

version='1.0.3-2729'

try:
    with open('./pyver.run', 'r') as fsock:
        pyver = fsock.read()
except IOError:
    pass

files = ['doc/*.txt', 'test/*.py']

rev = '%s%s' % (version, pyver)

setup(
        name='baklabel',
        version=rev,
        description='Automatic pathnames for Grandfathered backups',
        author='Mike Dewhirst',
        author_email='miked@dewhirst.com.au',
        url='http:///pypi.python.org/pypi/baklabel',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Operating System :: OS Independent',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Topic :: System :: Archiving :: Backup',
            'Topic :: Utilities',
            ],
        scripts=[],
        long_description="""%s""" % baklabel.longdesc,
        packages=['baklabel'],
        package_data={'baklabel': files},

)
