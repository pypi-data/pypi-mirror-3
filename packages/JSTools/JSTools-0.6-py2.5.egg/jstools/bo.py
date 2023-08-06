"""
zc.buildout recipe
"""
from jstools import merge

class BuildJS(object):
    """
    @format for config
    """
    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        if options.get('output') is not None:
            #@@ detect if config only has 1 section
            assert options.get('only'), ValueError('output var requires "only" var to select config section')

        self.compress = options.get('compress', False)
        if self.compress != 'True' and self.compress != 'true':
            self.compress = False
        self.only = options.get('only')

    
    def install(self):
        buildout_dir = self.buildout['buildout']['directory']
        self.merge = merge.Merger.from_fn(
                tuple(self.options.get('config').split('\n')),
                output_dir=self.options.get('output-dir', buildout_dir),
                root_dir=self.options.get('base-dir', buildout_dir),
                defaults={
                    'resource-dir': self.options.get(
                        'resource-dir', buildout_dir)
                },
                printer=self.buildout._logger)
        files = self.merge.run(uncompressed=not self.compress, single=self.only)
        return files

    update = install
