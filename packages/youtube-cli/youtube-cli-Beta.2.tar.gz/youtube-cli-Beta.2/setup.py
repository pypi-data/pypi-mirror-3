from setuptools import setup, find_packages

setup(
    name='youtube-cli',
    version='Beta 2',
    license="BSD",

    install_requires = [],

    description='Youtube command line interface with stream and download functionality',
    long_description=open('README.rst').read(),

    author='0xPr0xy',
    author_email='0xPr0xy@gmail.com',

    url='http://github.com/0xPr0xy/youtube-cli',
    download_url='http://github.com/0xPr0xy/youtube-cli/download/',

    include_package_data=True,

    packages=['youtube-cli'],

    zip_safe=False,
    classifiers=[
        #'Development Status :: V2.0',
        #'Environment :: Desktop Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        #'Framework :: Youtube Api',
    ]
 )
