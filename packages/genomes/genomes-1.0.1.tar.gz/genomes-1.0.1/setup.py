from distutils.core import setup

setup(
        name             = 'genomes',
        version          = '1.0.1',
        description      = 'Access to genomic assemblies meta data',
        long_description = open('README.txt').read(),
        license          = 'Kopimi',
        url              = 'http://xapple.github.com/genomes/',
        author           = 'Lucas Sinclair',
        author_email     = 'lucas.sinclair@me.com',
        classifiers      = ['Topic :: Scientific/Engineering :: Bio-Informatics'],
        packages         = ['genomes'],
        package_data     = {'genomes': ['genomes.db']},
    )
