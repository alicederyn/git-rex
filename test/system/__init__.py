"""System tests invoke rex with no mocking, in a simulated environment.

They are relatively slow, but stable across refactorings, so should be used to test:
 - the happy path for advertised features
   e.g. rex --edit
 - system-wide integration paths
   e.g. rex's overall error handling integration

Other tests should be targetted at the unit or integration level.
"""
