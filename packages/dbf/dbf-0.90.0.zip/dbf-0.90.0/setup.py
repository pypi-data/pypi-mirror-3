from distutils.core import setup
from glob import glob
import os
import dbf

html_docs = glob('dbf/html/*')

long_desc="""
Currently supports dBase III, and FoxPro - Visual FoxPro tables. Text is returned as unicode, and codepage settings in tables are honored. Documentation needs work, but author is very responsive to e-mails.

Not supported: index files (but can create tempory non-file indexes), null fields (data returned is blank), and auto-incrementing fields.

This version is backwards-incompatible as far as the default types of returned data.  However, it does supply backwards-compatible custom data types that can be specified when tables are opened: Char (auto-trims white-space), Date & DateTime (allows False values), and Logical (allows unknown values).  To get the old behavior with a dBase III table would look like this:  table = Table(somefile, default_data_types=dict(C=Char, L=Logical, D=Date, T=DateTime, M=Char))
"""

setup( name='dbf',
       version= '.'.join([str(x) for x in dbf.version]),
       license='BSD License',
       description='Pure python package for reading/writing dBase, FoxPro, and Visual FoxPro .dbf files (including memos)',
       long_description=long_desc,
       url='http://groups.google.com/group/python-dbase',
       py_modules=['dbf', 'test_dbf'],
       provides=['dbf'],
       author='Ethan Furman',
       author_email='ethan@stoneleaf.us',
       classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Topic :: Database' ],
     )

