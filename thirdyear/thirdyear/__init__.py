"""Compatibility shim package.

This package exists so deployments using the import path
`thirdyear.thirdyear.wsgi:application` continue to work. It simply
re-exports the real WSGI application from the parent package.
"""
