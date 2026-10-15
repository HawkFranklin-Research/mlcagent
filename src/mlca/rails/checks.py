"""Only reviewed engine functions may be registered as executable rails.

A function returns (fired, value-free detail); it may refuse through MlcaUserError.
Rail YAML never supplies executable code or an arbitrary import path.
"""

FUNCTIONS = {}
