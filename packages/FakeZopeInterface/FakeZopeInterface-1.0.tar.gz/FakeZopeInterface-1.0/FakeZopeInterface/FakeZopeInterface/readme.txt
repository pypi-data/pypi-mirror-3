A set of tools that will fake missing Zope interface classes..  This
thing writes to the filesystem (albeit to a temporary directory), so
beware.

It creates a directory called FakedZopeInterfaces in the servers'
temporary directory, adds it to the system path and creates importable
modules and interface definitions.
