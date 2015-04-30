"""Plugin container package.

To dynamically add new authoring or mapped sources, add modules to this
package that contain classes for those sources.
"""
import os
import glob

modules = glob.glob(os.path.dirname(__file__)+"/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules]
