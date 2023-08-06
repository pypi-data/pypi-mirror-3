"""
============
Introduction
============
The **genomes** software is a package written in Python. It is designed to provide easy access to some meta data about genome assemblies. You can retrieve the list of chromosomes for any assembly. In addition, you can get the lengths in base pairs of every chromosome.

============
Installation
============
To install you can simply type::

    $ sudo easy_install genomes

If you don't have permission to install it like that, you can simply download the code and include the directory in your python path::

    $ wget http://pypi.python.org/packages/source/g/genomes/genomes-1.0.0.tar.gz
    $ tar -xzf genomes-1.0.0.tar.gz
    $ cd genomes-1.0.0/
    $ sed -i "$ a\export PYTHONPATH=`pwd`/:\$PYTHONPATH" ~/.bashrc
    $ source ~/.bashrc

========
Examples
========
Here are all the things you can do with it::

    from genomes import Assembly
    a = Assembly('sacCer2')
    print a.chrmeta
    print a.guess_chromsome_name('chr1')

====
Code
====
"""

b'This module needs Python 2.6 or later.'

# Special variables #
__version__ = '1.0.0-4-g22d30bf'

# Built-in modules #
import os, sqlite3

# The database #
path = os.path.abspath(os.path.dirname(__file__)) + '/genomes.db'
connection = sqlite3.connect(path)
cursor = connection.cursor()

# The list of assemblies #
cursor.execute("select name from sqlite_master where type='table'")
assemblies = [x[0] for x in cursor if x[0] != 'assemblies']

################################################################################
class Assembly(object):
    """The only object provided by the library.

       :param assembly: A valid assembly name.
       :type  assembly: string
    """

    def __init__(self, assembly):
        # Check the input type #
        if not isinstance(assembly, basestring):
            raise TypeError('The assembly paramater needs to be a string such as "sacCer2".')
        if not assembly in assemblies:
            raise TypeError('The assembly "%s" was not found in the database.' % assembly)
        # Load the chromosome data #
        cursor.execute("select * from '%s'" % assembly)
        columns = [x[0] for x in cursor.description]
        self.chromosomes = [dict(zip(columns,chrom)) for chrom in cursor]
        # Cut the synonyms #
        for chrom in self.chromosomes:
            chrom['synonyms'] = chrom['synonyms'].split(',') if chrom['synonyms'] else []

    @property
    def chrmeta(self):
        """A dictionary of chromosome metadata:

        ::

            >>> from genomes import Assembly
            >>> a = Assembly('TAIR10')
            >>> print a.chrmeta
            {u'c': {'length': 154478}, u'm': {'length': 366924}, u'1': {'length': 30427671}, u'3': {'length': 23459830}, u'2': {'length': 19698289}, u'5': {'length': 26975502}, u'4': {'length': 18585056}}
        """
        return dict([(chrom['label'], dict([('length', chrom['length'])])) for chrom in self.chromosomes])

    def guess_chromosome_name(self, chromosome_name):
        """Searches the assembly for chromosome synonym names,
           and returns the canonical name of the chromosome.
           Returns None if the chromosome is not known about.

           :param chromosome_name: Any given name for a chromosome in this assembly.
           :type  chromosome_name: string

           :returns: The same or an other name for the chromosome.

           ::

               >>> from genomes import Assembly
               >>> a = Assembly('sacCer2')
               >>> print a.guess_chromosome_name('chrR')
               2micron
        """
        # Convert to unicode #
        chromosome_name = unicode(chromosome_name)
        # Check for synonyms #
        for chrom in self.chromosomes:
            if chromosome_name in chrom['synonyms']: return chrom['label']
        # Do some guessing #
        name = chromosome_name.lstrip('chr')
        for chrom in self.chromosomes:
            if name == chrom['name']: return chrom['label']
            if name == chrom['label'].strip('chr'): return chrom['label']

################################################################################
if __name__ == "__main__":
    import doctest
    doctest.testmod()
