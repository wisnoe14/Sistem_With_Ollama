# Ensure all submodules are recognized as part of the package
import os
import glob
import importlib

package_dir = os.path.dirname(__file__)
for module_path in glob.glob(os.path.join(package_dir, "**", "*.py"), recursive=True):
	rel_path = os.path.relpath(module_path, package_dir)
	if rel_path == "__init__.py" or rel_path.startswith("__pycache__"):
		continue
	module_name = rel_path[:-3].replace(os.sep, ".")
	try:
		importlib.import_module(f"app.{module_name}")
	except Exception:
		pass
