import App.FindHomes # activate Zope's import magic
from AccessControl.Permission import addPermission

# register our permission
addPermission("zdoc: view documentation")

# rebind 'pydoc.locate' to prevent reloading -- as this deactivates Zope's import magic
from pydoc import *
import pydoc

org_locate = locate
def locate(path, *args, **kw):
 if args: args = (False,) + args[1:]
 if 'forceload' in kw: kw['forceload'] = False
 return org_locate(path, *args, **kw)

pydoc.locate = locate

# work around a Python bug in older Python versions
if not hasattr(Doc, "docdata"):
  # old version which needs patching
  import inspect
  from dm.reuse import rebindFunction
  def _patched_dir(obj):
    return [d for d in dir(obj) if hasattr(obj, d)]
  inspect.getmembers = rebindFunction(inspect.getmembers, dir=_patched_dir)
  inspect.classify_class_attrs = rebindFunction(inspect.classify_class_attrs, dir=_patched_dir)

if __name__ == '__main__': cli()
                              
