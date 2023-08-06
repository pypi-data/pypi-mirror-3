import sys, types, tempfile, os

global sys_path_temp
sys_path_temp = None

def get_namespace_target(item):
    dottedName = str(item).split()[-1][:-1]
    if dottedName[0] in ('"', "'"):
        dottedName = dottedName[1:]
    if dottedName[-1] in ('"', "'"):
        dottedName = dottedName[:-1]        
    name = dottedName.split('.')
    result = '.'.join(name[:-1]), name[-1]
    print result
    return result

def check_importable(item):
    namespace, target = get_namespace_target(item)
    try:
        exec("from %s import %s" % (namespace, target))
        return True
    except ImportError:
        return False
    except SyntaxError:
        print 'SyntaxError'
        print dottedName, name, namespace, target, str(item)
        return False

def setup_sys_path_temp():
    directory = os.path.join(tempfile.gettempdir(), 'FakedZopeInterfaces')
    global sys_path_temp
    sys_path_temp = directory
    try:
        os.mkdir(sys_path_temp)
    except OSError:
        # Already exists
        pass
    sys.path.append(sys_path_temp)

def fake_module_and_interface(item):
    print 'faking', item
    #import pdb
    #pdb.set_trace()
    global sys_path_temp
    setup_sys_path_temp()
    namespace, target_name = get_namespace_target(item)
    if hasattr(sys.modules.get(namespace), target_name):
        # Nothing to do, leave it as it is
        return
    else:
        paths = namespace.split('.')
        file = None
        for index in range(len(paths)):
            path = os.path.join(sys_path_temp, '/'.join(paths[:index+1]))
            try:
                os.mkdir(path)
            except OSError:
                # Already exists
                pass
            filepath = os.path.join(path, '__init__.py')
            try:
                os.stat(filepath)
                file = open(filepath, 'aw')
            except OSError:
                file = open(filepath, 'w')
                file.write('pass\n')
    file.write("from zope.interface import Interface\n")
    file.write("class %s(Interface):\n\t'Simple marker'\n\n" % target_name)
    file.close()
    try:
        exec("from %s import %s" % (namespace, target_name))
    except ImportError, value:
        print 'importerror in fake_module_and_interface', value

setup_sys_path_temp()
