
"""
clid.mediafile
~~~~~~~~~~~~~~

Tag different music file formats through a unified interface.
"""

import phrydy
import phrydy.mediafile

from . import exceptions

FIELDS = phrydy.MediaFile.fields()  # list of valid fields, like artist, album, etc


class MediaFile:
    """
    Tag multiple file formats easily.
    Attributes:
        length (int): Duration of audio in seconds.
        format (str): Human readable format name of the given file.
        _tags (phrydy.MediaFile): Actual object with tagging information.
    """

    def __init__(self, path):
        """
        Args:
            path (str): Path to file to read tags from.
        """
        try:
            self._tags = phrydy.MediaFile(path=path)
        except phrydy.mediafile.FileTypeError as e:
            # unrecognized filetype
            raise exceptions.UnknownFileTypeError(str(e)) from e
        except phrydy.mediafile.UnreadableFileError as e:
            # information could not be extracted from the file
            raise exceptions.ClidUserError(str(e)) from e

        self.length = self._tags.length
        self.format = self._tags.format

    def get_tag(self, tagname):
        """
        Get the value of a tag.
        Args:
            tagname (str): Name of tag. Should be a valid field in `FIELDS`.

        Raises:
            errors.InvalidTagError: `tagname` is not a recognized tag field.
        """
        if tagname in FIELDS:
            return getattr(self._tags, tagname)
        else:
            raise exceptions.InvalidTagError(
                '"{}" is not a valid tag name.'.format(tagname)
            )

    def set_tag(self, tagname, value):
        """
        Set the value of a tag. The tag is not saved to the file; call the
        `save` method to do so.
        Args:
            tagname (str): Name of tag. Should be a valid field in `FIELDS`.
            value (str):
                Value of tag field. It will be automatically converted to the
                appropriate datatype if required.
        """
        setattr(self._tags, tagname, value)

    def save(self):
        """Save the tags to the file."""
        try:
            self._tags.save()
        except phrydy.mediafile.UnreadableFileError as e:
            raise exceptions.ClidUserError(str(e)) from e
