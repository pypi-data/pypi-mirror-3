try:
    VERSION = __import__('pkg_resources').get_distribution('cutools').version
except Exception, e:
    VERSION = 'unknown'
