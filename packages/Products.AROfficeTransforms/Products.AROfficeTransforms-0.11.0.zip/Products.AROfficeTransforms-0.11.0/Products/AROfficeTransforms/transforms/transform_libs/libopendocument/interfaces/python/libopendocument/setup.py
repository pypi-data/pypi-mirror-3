from distutils.core import setup

files = [
    '__init__',
    'OpenDocument',
    'unzip',
]

xsl = [
    'default',
]

setup(name='libopendocument',
        packages = ['libopendocument'],
        package_dir = {'libopendocument': '.'},
        package_data = {'libopendocument': ['xsl/*.xsl'] + ['xsl/%s/*.xsl' % x for x in xsl] },         
        py_modules = ["libopendocument.%s" % x for x in files ],

        

    )
    
    
