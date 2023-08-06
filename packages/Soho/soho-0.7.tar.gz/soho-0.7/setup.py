import os
from setuptools import setup, find_packages


description_file = 'README.txt'
description = open(description_file).read().split('\n\n')[0].strip()
description = description.replace('\n', ' ')
long_description_file = os.path.join('doc', 'README.txt')
long_description = open(long_description_file).read().strip()

setup(
    name='soho',
    version='0.7',
    packages=find_packages('src'),
    namespace_packages=(),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=True,

    install_requires=['docutils',
                      'zope.pagetemplate'],

    entry_points={
        'console_scripts': ('soho=soho.sohobuild:main', )
        },

    author='Damien Baty',
    author_email='damien.baty@remove-me.gmail.com',
    description=description,
    long_description=long_description,
    license='GNU GPL',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Documentation',
                 'Topic :: Internet :: WWW/HTTP',
                 'Topic :: Text Processing :: Markup :: HTML',
                 ],
    keywords='rest zpt website generator template',
    url='http://code.noherring.com/soho',
    download_url='http://cheeseshop.python.org/pypi/soho',
    )
