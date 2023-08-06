A set of tools that will fake missing Zope interface classes..  This
thing writes to the filesystem, so beware.

It creates a directory called FakedZopeInterfaces within the egg
directory FakeZopeInterface (needs write adds), adds it to the system
path and creates importable modules and interface definitions.
