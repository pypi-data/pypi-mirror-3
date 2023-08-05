import warnings

# Show all deprecated warning only once:
warnings.filterwarnings('once', category=DeprecationWarning)
del warnings

__version__ = '0.1.0'
