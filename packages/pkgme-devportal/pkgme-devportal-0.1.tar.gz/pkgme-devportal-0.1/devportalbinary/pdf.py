# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import os

from devportalbinary.metadata import MetadataBackend


class PdfBackend(MetadataBackend):
    """A backend that uses MyApps metadata to build a package for a PDF."""

    def get_architecture(self, metadata):
        return 'all'

    def get_build_depends(self, metadata):
        return 'debhelper (>=7)'

    def get_depends(self, metadata):
        return 'xdg-utils, ${misc:Depends}'

    def get_executable(self, package_name):
        pdf_filename = None
        for filename in os.listdir(self.path):
            if filename.endswith('.pdf'):
                pdf_filename = filename
                break
        if pdf_filename is None:
            return None
        return '/usr/bin/xdg-open /opt/%s/%s' % (package_name, pdf_filename)

    def want(self):
        if not self.has_metadata_file():
            return 0

        excluded_files = set([self.METADATA_FILE, 'debian'])
        try:
            metadata = self.get_metadata()
        except ValueError:
            # Not a JSON file.
            return 0

        # XXX: This implies that we're doing exact string matching on the
        # paths in the metadata and the results of os.listdir.  We actually
        # want to exclude the icons if they are the same file, not if the
        # strings happen to be equal.
        excluded_files |= set(metadata.get(self.ICONS, {}).values())
        files = os.listdir(self.path)
        files = [f for f in files if f not in excluded_files]
        if len(files) == 1:
            if files[0].endswith(".pdf"):
                return 20
        return 0
