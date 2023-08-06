from __future__ import with_statement

import glob
import os
import shutil
import subprocess
import tempfile

from humfrey.update.transform.base import Transform

class SparqlFilter(Transform):
    def __init__(self, *file_globs):
        for file_glob in file_globs:
            file_glob = os.path.normpath(file_glob)
            if '..' in os.path.split(file_glob):
                raise ValueError("%r attempts to traverse to a higher directory" % file_glob)
        self.file_globs = file_globs




    def execute(self, transform_manager, input):
        filenames = []
        for file_glob in self.file_globs:
            file_glob = os.path.join(transform_manager.update_directory, file_glob)
            self.filenames.extend(glob.glob(file_glob))

        tdb_directory = tempfile.mkdtemp()

        try:
            with open(transform_manager('nt'), 'w') as output:
                self.perform_transform(transform_manager, tdb_directory, output)
        finally:
            shutil.rmtree(tdb_directory)

    def perform_transform(self, transform_manager, tdb_directory, output):
        subprocess.call(['java'])

        if True:

            stderr_filename = output.name[:-3] + 'stderr'
            with open(stderr_filename, 'w') as stderr:
                transform_manager.start(self, [input])
                output_filenames = [output.name]

                # Call xmllint to perform the transformation
                subprocess.call(['xmllint', '--html', '--xmlout',
                                            '--dropdtd', '--recover',
                                            '--format', input],
                                stdout=output, stderr=stderr)

                # If something was written to stderr, we add it to our
                # outputs.
                if stderr.tell():
                    output_filenames.append(stderr_filename)

                transform_manager.end(output_filenames)

            # If nothing was written to stderr, it won't be in our
            # outputs, so we can unlink the file.
            if len(output_filenames) == 1:
                os.unlink(stderr_filename)

            return output.name
