from distutils.core import setup

setup(
        name = 'netbytes',
        version = '1.3',
        author = 'Nicolas DAVID',
        author_email = 'nicolas.david.mail@gmail.com',
        py_modules = ['netbytes'],
        description = 'writes and handle the bytes exchanged on network',
        long_description = '''
netbytes
===============

The *netbytes* module aims to offer an easy way to handle the bytes exchanded
beetween server and clients.

.. warning::

    *netbytes* does not replace the module socket, nor package twisted or
    alike. It only manages the *str* exchanged via network ; in fact, you may
    very well not doing any networking at all, it doesn't care because
    **technicaly, it has nothing to do with networking**, even if designed to
    operate in such context.

As servers and clients can only exchange *str*, there is a need to
establish an arbitrary convention for representing instructions, informations,
data, etc... into *str*. A common technic, is to reserve the first bytes
of the string to this purpose, and the rest of the string to contain data. And
even this data must be rigourously encoded by an arbitrary convention... If not
properly handled, the readability can quickly be a mess, and a nightmare to
maintain.

This is where *netbytes* aims to be handfull : it creates a tree of all the
type of bytes that can be exchanged beetween clients and server from a model
easy to understand, and quick to design. The nodes of this tree can then be
called to produce a string ready to be sent. And on the reciever side, this
string can be processed by the tree, which call the appropriate handler. This
way, the programmer spends less time in writing code to decode and interpret
the recieved string of bytes, and the source code become a lot more readable,
and maintainable.''',
        classifiers = [
                        'Programming Language :: Python :: 2.7',
                        'Programming Language :: Python :: 2.6',
                        'Programming Language :: Python :: 2.5',
                        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                        'Development Status :: 4 - Beta',
                        'Intended Audience :: Developers',
                        'Operating System :: OS Independent',
                        'Topic :: System :: Networking',
                        'Topic :: Software Development :: Libraries'
                      ]
)
                        
                        
