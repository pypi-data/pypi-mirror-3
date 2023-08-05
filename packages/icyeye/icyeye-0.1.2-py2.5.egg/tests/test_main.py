"""Main test suite for icyeye"""

from os import path
from nose.tools import eq_, assert_raises

from icyeye import make_css_images_inline, encode_image_to_base64, CssFileError


class _BaseFixtureTestCase(object):
    """Base test case class which can find and read fixture files."""
    
    def get_fixture_file_path(self, file_name):
        """
        Utility to return he full path to ``file_name`` in the fixtures
        directory.
        
        """
        return path.join(path.dirname(__file__), "fixtures", file_name)
    
    def read_fixture_file(self, file_name):
        """
        Utility to read the contents of ``file_name`` in the fixture directory
        
        """
        fixture_file = None
        try:
            fixture_file = open(self.get_fixture_file_path(file_name))
            fixture_data = fixture_file.read()
        finally:
            if fixture_file is not None:
                fixture_file.close()
        
        return fixture_data


class TestMakeCssImagesInline(_BaseFixtureTestCase):
    """Tests for :func:`make_css_images_inline`."""
    
    def test_mismatched_arguements(self):
        """
        The css_file_url must come at the end of the css_file_path argument.
        
        """
        assert_raises(
            CssFileError,
            make_css_images_inline,
            "/tmp/css/main.css",
            "/other.css",
            )
    
    def test_passing_relative_url(self):
        """The css_file_url must be an absolute URL."""
        
        assert_raises(
            CssFileError,
            make_css_images_inline,
            "/tmp/css/main.css",
            "main.css",
            )


class TestCssImagesInlinerParsing(_BaseFixtureTestCase):
    """Tests for the parsing component of :func:`make_images_inline`"""
    
    def test_relative_urls(self):
        """URLs relative to the CSS file are correctly identified and encoded"""
        
        expected_output = self.read_fixture_file("relative_urls.expected.css")
        
        new_css = make_css_images_inline(
            self.get_fixture_file_path("relative_urls.css"),
            )
        
        eq_(expected_output, new_css)
        
    def test_absolute_urls(self):
        """URLs relative to the CSS file are correctly identified and encoded"""
        
        expected_output = self.read_fixture_file(
            "absolute/absolute_urls.expected.css")
        
        new_css = make_css_images_inline(
            self.get_fixture_file_path("absolute/absolute_urls.css"),
            "/absolute/absolute_urls.css",
            )
        
        eq_(expected_output, new_css)
    
    def test_skipped_urls(self):
        """
        URLs which point to http:// locations or cannot be found on disk are
        left unchanged.
        
        """
        expected_output = self.read_fixture_file("skip.css")
        
        new_css = make_css_images_inline(
            self.get_fixture_file_path("skip.css"),
            "/skip.css",
            )
        
        eq_(expected_output, new_css)
    
    def test_quotes(self):
        """
        All styles of quoting are permitted as defined by
        http://www.w3.org/TR/CSS2/syndata.html#uri
        
        """
        expected_output = self.read_fixture_file("quotes.expected.css")
        
        new_css = make_css_images_inline(
            self.get_fixture_file_path("quotes.css"),
            "/quotes.css",
            )
        
        eq_(expected_output, new_css)
    
    def test_whitespace(self):
        """
        All styles of whitespace around the URL being defined are allowed as per
        http://www.w3.org/TR/CSS2/syndata.html#uri
        
        """
        expected_output = self.read_fixture_file("whitespace.expected.css")
        
        new_css = make_css_images_inline(
            self.get_fixture_file_path("whitespace.css"),
            "/whitespace.css",
            )
    
    def test_size_limit_met(self):
        """
        When the size of a file exactly matches the limit or is under the limit,
        it is still encoded.
        
        """
        expected_output = self.read_fixture_file("relative_urls.expected.css")
        
        # Exact hit on size of blue.jpg
        new_css = make_css_images_inline(
            self.get_fixture_file_path("relative_urls.css"),
            "/relative_urls.css", image_size_limit=16965
            )
        
        eq_(expected_output, new_css)
        
        # Easily clear of blue.jpg size
        new_css = make_css_images_inline(
            self.get_fixture_file_path("relative_urls.css"),
            "/relative_urls.css", image_size_limit=20000
            )
        
        eq_(expected_output, new_css)
        
    def test_size_limit_not_met(self):
        """
        When the size of a file exceeds the maximum file size that file is left
        alone in the output.
        
        """
        
        expected_output = self.read_fixture_file(
            "image_size_not_met.expected.css")
        
        new_css = make_css_images_inline(
            self.get_fixture_file_path("relative_urls.css"),
            "/relative_urls.css", image_size_limit=3000
            )
        
        eq_(expected_output, new_css)


class TestEncodeImageToBase64(_BaseFixtureTestCase):
    """Tests for :func:`encode_image_to_base64` """
    
    def do_encode(self, image_file_name):
        """
        Test that the contents od ``image_file_name`` are converted to match
        fixtures created by an external utility.
        
        """
        expected_output_file = open("%s.base64" % image_file_name) 
        expected_output = expected_output_file.read()
        expected_output_file.close()
        
        generated_output = encode_image_to_base64(image_file_name)
        
        eq_(expected_output, generated_output)
    
    def test_files(self):
        """PNG-, GIF- and JPEG-files can be encoded (amongst others)."""
        
        for file_name in ("red.png", "green.gif", "blue.jpg"):
            image_file_name = self.get_fixture_file_path(file_name) 
            
            yield self.do_encode, image_file_name
            
    def test_unknown_mime_type(self):
        """
        The file must have an extension which is recognized to use as a
        mime-type.
        
        """
        assert_raises(
            AssertionError,
            encode_image_to_base64,
            self.get_fixture_file_path("foo.unknown"),
            )