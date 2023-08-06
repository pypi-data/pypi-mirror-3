from setuptools import setup, find_packages

setup(
    name='claun',
    version='2.0.0.5',
    description='Claun system for distributed environments',
    long_description='\n'.join((
        '',
    )),
    author='Jiri Chadima',
    author_email='chadima.jiri@gmail.com',
    url='example.com',
    license='Other',
    
    include_package_data = True,
    
    exclude_package_data={
         '':['ssl', 'logs']
    },

    packages=find_packages(
        exclude=('logs', 'ssl',)
    ),
    
    scripts = ['runclaun.py'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
#        "License :: OSI Approved :: MIT License",
        "License :: Other/Proprietary License",
        "Programming Language :: Python",
        "Topic :: System :: Distributed Computing",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    install_requires=[
         'mimeparse==0.1.3',
         'docutils',
         'PyYAML==3.10',
         'pyOpenSSL==0.13',
         'httplib2>=0.7.0, <= 0.7.4',
         'couchDB==0.8',
    ],
    setup_requires=[
#       'setuptools_dummy'
    ],
)
