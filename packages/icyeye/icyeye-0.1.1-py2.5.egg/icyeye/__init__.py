"""Main code for inline-css-images (icyeye) package"""

from base64 import standard_b64encode
from functools import partial
from mimetypes import guess_type
from os.path import abspath, dirname, basename, expanduser, getsize, join
import re


__all__ = ["make_css_images_inline", "encode_image_to_base64", "CssFileError"]


_CSS_URL_RE = re.compile(r"""(url\(\s*['"]?)(.+?)(['"]?\s*\))""")


class CssFileError(Exception):
    """
    Exception raised when there is a problem with the input regarding the CSS
    file.
    
    """
    
    pass


class _ImageTooLargeError(Exception):
    """Exception raised when the image exceeds the maximum image size allowed"""
    
    pass


def make_css_images_inline(
    css_file_path, css_file_url=None, image_size_limit=None):
    """
    Find all images specified in a "url(...)" declaration in the file specified
    by ``css_file_path`` and generate a copy of the the file with the images
    set inline as base64 encoded strings.

    :param css_file_path: The path to the CSS file to parse
    :type css_file_path: :class:`basestring`
    :param css_file_url: The absolute URL to the CSS file
    :type css_file_url: :class:`basestring`
    :param image_size_limit: The upper (inclusive) limit on file size of any
        image to make inline (in bytes)
    :type image_size_limit: :class:`int`
    
    .. note:: The ``css_file_url`` is needed to resolve any images referred
        to in the CSS in an absolute manner.
    
    """
    
    # If the no URL is not given assume that all url(...) declarations will be
    # relative. However, we need to compute the file root, so assume that it's
    # the same directory.
    if not css_file_url:
        css_file_url = "/%s" % basename(css_file_path)
    
    if not css_file_path.endswith(css_file_url):
        raise CssFileError(
            "css_file_url must occur at the end of css_file_path")
    
    if not css_file_url.startswith("/"):
        raise CssFileError(
            "css_file_url must be an absolute URL")
    
    # Compute where the root of the webserver lies on disk
    css_file_abs_path = abspath(expanduser(css_file_path))
    css_file_relative_root = dirname(css_file_abs_path)
    css_file_root = css_file_abs_path[:-len(css_file_url)]
    
    
    css_file = None
    try:
        css_file = open(css_file_abs_path)
        css_text = css_file.read()
    finally:
        if css_file is not None:
            css_file.close()
    
    url_substitutor = partial(
        _substitute_css_url,
        css_file_root,
        css_file_relative_root,
        image_size_limit,
        )
    
    return _CSS_URL_RE.sub(url_substitutor, css_text)


def _substitute_css_url(
    css_file_root, css_file_relative_root, image_size_limit, url_match):
    """
    Replace the string referring to the url path contained in ``url_match``
    with the base64 encoded version of the image.
    
    .. warning:: This function must be used in conjunction with
        :func:`functools.partial` to generate a callable suitable for use with
        :func:`re.sub` and should not be called directly
    
    :param css_file_root: The root directory for the web server
    :type css_file_root: :class:`basestring` 
    :param css_file_relative_root: The directory which contains the CSS file
        (for relative URL references)
    :type css_file_relative_root: :class:`basestring` 
    :param image_size_limit: The upper (inclusive) limit on the size of image
        file to convert (in bytes)
    :type image_size_limit: :class:`int`
    :param url_match: The match object for the url pattern
    :type url_match: :class:`re.MatchObject`
    :return: A new url(...) declaration with the image inline (if possible)
    
    """
    
    url_path = url_match.group(2)
    
    if "://" in url_path:
        # URLs which point to other internet address are left as is
        encoded_url = url_path
    else:
        if url_path.startswith("/"):
            # Work out where the file should be on disk relative to the CSS
            # file
            absolute_image_path = join(css_file_root, url_path[1:])
        else:
            # Must be a relative URL, so put the path together:
            absolute_image_path = abspath(
                join(css_file_relative_root, url_path))
        
        try:
            if image_size_limit:
                image_size = getsize(absolute_image_path)
                if image_size > image_size_limit:
                    raise _ImageTooLargeError(
                        "%s is larger (%db) than the maximum image size "
                        "permitted (%db)" %
                        (absolute_image_path, image_size, image_size_limit)
                        )
                 
            encoded_url = encode_image_to_base64(absolute_image_path)
        except (OSError, IOError):
            # All error concerning reading of the image file are swallowed
            # silently and the url_path is used
            
            # TODO: Should this be logged?
            encoded_url = url_path
        except _ImageTooLargeError:
            # TODO: Should this be logged?
            encoded_url = url_path

    return "url(%s)" % encoded_url


def encode_image_to_base64(image_path):
    """
    Encode the image at ``image_path`` to a base64 encoded format suitable for
    inclusion in a CSS url() definition.
    
    .. note:: Any exceptions caused by file operations are allowed to propagate
    
    """
    mime_type = guess_type(image_path)[0]
    assert mime_type, "Cannot workout mimetype of image"
    
    image_file = None
    
    try:
        image_file = open(image_path)
        image_data = image_file.read()
    finally:
        if image_file is not None:
            image_file.close()
    
    image_data_encoded = standard_b64encode(image_data)
    image_representation = "data:%s;base64,%s" % (mime_type, image_data_encoded) 
    
    return image_representation 
