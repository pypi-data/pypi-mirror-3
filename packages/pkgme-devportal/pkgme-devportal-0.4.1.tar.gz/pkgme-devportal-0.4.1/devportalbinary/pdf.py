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

    def get_explicit_copyright(self, metadata):
        # See https://bugs.launchpad.net/pkgme-devportal/+bug/1026121/.
        maintainer = self.get_maintainer(metadata)
        if maintainer:
            maintainer_suffix = (
                " or contact the submitter of the PDF, %s" % (maintainer,))
        else:
            maintainer_suffix = ''
        return """\
Please see the enclosed PDF file for the exact copyright holders%s.

This file was automatically generated.
""" % (maintainer_suffix,)

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

    def want_with_metadata(self, metadata):
        # XXX: This implies that we're doing exact string matching on the
        # paths in the metadata and the results of os.listdir.  We actually
        # want to exclude the icons if they are the same file, not if the
        # strings happen to be equal.
        excluded_files = set([self.METADATA_FILE, 'debian'])
        excluded_files |= set(metadata.get(self.ICONS, {}).values())
        files = os.listdir(self.path)
        files = [f for f in files if f not in excluded_files]
        # By default, we don't want it and give no reason.  Sane default in
        # case of buggy code below.
        score = 0
        reason = None
        if len(files) == 0:
            reason = 'No files found, just metadata'
        elif len(files) == 1:
            filename = files[0]
            if filename.endswith(".pdf"):
                score = 20
            else:
                reason = 'File is not a PDF: %r' % (filename,)
        else:
            reason = 'More files than just a PDF: %r' % (sorted(files),)
        return {'score': score, 'reason': reason}
