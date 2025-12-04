#!/usr/bin/env python3
"""
Tests for Lane Lexicon StarDict converter.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Import the converter module
import sys
sys.path.insert(0, str(Path(__file__).parent))
from convert_to_stardict import LaneConverter


class TestLaneConverter(unittest.TestCase):
    """Test cases for LaneConverter."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.test_dir) / "source"
        self.output_dir = Path(self.test_dir) / "output"
        self.source_dir.mkdir()
        self.output_dir.mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_sample_xml(self, filename, content):
        """Create a sample XML file for testing."""
        with open(self.source_dir / filename, 'w', encoding='utf-8') as f:
            f.write(content)

    def test_initialization(self):
        """Test LaneConverter initialization."""
        converter = LaneConverter(self.source_dir, self.output_dir)
        self.assertEqual(converter.source_dir, self.source_dir)
        self.assertEqual(converter.output_dir, self.output_dir)
        self.assertTrue(self.output_dir.exists())

    def test_merge_xml_files(self):
        """Test XML file merging."""
        # Create test XML files
        xml1 = '<?xml version="1.0" encoding="UTF-8"?><TEI.2><text>Content 1</text></TEI.2>'
        xml2 = '<?xml version="1.0" encoding="UTF-8"?><TEI.2><text>Content 2</text></TEI.2>'
        
        self.create_sample_xml('test1.xml', xml1)
        self.create_sample_xml('test2.xml', xml2)
        
        converter = LaneConverter(self.source_dir, self.output_dir)
        converter.merge_xml_files()
        
        # Check merged file exists
        merged_file = self.output_dir / "lane-lexicon.xml"
        self.assertTrue(merged_file.exists())
        
        # Check content
        with open(merged_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('Content 1', content)
        self.assertIn('Content 2', content)

    def test_merge_xml_files_no_source(self):
        """Test merge_xml_files raises error when no XML files found."""
        converter = LaneConverter(self.source_dir, self.output_dir)
        with self.assertRaises(FileNotFoundError):
            converter.merge_xml_files()

    def test_first_cleanup(self):
        """Test first cleanup transformation."""
        # Create a merged XML file with tags to remove
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<TEI.2>
<text>
<body>
<entryFree id="test" key="word">
<form><orth lang="ar">word</orth></form>
<hi rend="ital">definition</hi>
</entryFree>
</body>
</text>
</TEI.2>'''
        
        converter = LaneConverter(self.source_dir, self.output_dir)
        with open(converter.filename_xml, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        converter.first_cleanup()
        
        with open(converter.filename_xml, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that specific tags were removed/replaced
        self.assertNotIn('<TEI.2>', content)
        self.assertNotIn('<?xml', content)
        self.assertNotIn('<entryFree', content)
        self.assertIn('HI_OPEN', content)
        self.assertIn('HI_CLOSE', content)
        self.assertIn('_____', content)

    def test_second_cleanup(self):
        """Test second cleanup transformation."""
        csv_content = "word\tdefinition with \\n newline <k>key</k>"
        
        converter = LaneConverter(self.source_dir, self.output_dir)
        with open(converter.filename_csv, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        converter.second_cleanup()
        
        with open(converter.filename_csv, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check transformations
        self.assertNotIn('\t', content)
        self.assertIn('#####_____#####_____#####', content)
        self.assertNotIn('\\n', content)
        self.assertNotIn('<k>', content)

    def test_put_colors(self):
        """Test color formatting."""
        csv_content = "word#####_____#####_____#####HI_OPENtext HI_CLOSE FOREIGNOPEN FOREIGNCLOSE"
        
        converter = LaneConverter(self.source_dir, self.output_dir)
        with open(converter.filename_csv, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        converter.put_colors()
        
        with open(converter.filename_csv, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check color formatting applied
        self.assertIn('<FONT COLOR="DarkBlue">', content)
        self.assertIn('</FONT>', content)
        self.assertNotIn('HI_OPEN', content)
        self.assertNotIn('FOREIGNOPEN', content)

    def test_convert_dictd_to_tab(self):
        """Test dictd to tab conversion helper."""
        converter = LaneConverter(self.source_dir, self.output_dir)
        
        # Create mock index file
        index_file = self.output_dir / "test.index"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("word1\t0\t5\n")
            f.write("word2\t5\t5\n")
        
        # Create mock dict file
        dict_file = self.output_dir / "test.dict"
        with open(dict_file, 'wb') as f:
            f.write(b"def1 def2 ")
        
        output_file = self.output_dir / "test.txt"
        converter._convert_dictd_to_tab(index_file, dict_file, output_file)
        
        self.assertTrue(output_file.exists())
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('word1', content)
        self.assertIn('word2', content)

    def test_clean_up(self):
        """Test cleanup of temporary files."""
        converter = LaneConverter(self.source_dir, self.output_dir)
        
        # Create some temporary files
        temp_files = [
            converter.filename_xml,
            self.output_dir / "lane-lexicon-no-tashkeel.txt",
            self.output_dir / "lane-lexicon-tashkeel.txt",
        ]
        
        for f in temp_files:
            f.touch()
            self.assertTrue(f.exists())
        
        converter.clean_up()
        
        # Check files are removed
        for f in temp_files:
            self.assertFalse(f.exists())


class TestIntegration(unittest.TestCase):
    """Integration tests that test multiple steps together."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.test_dir) / "source"
        self.output_dir = Path(self.test_dir) / "output"
        self.source_dir.mkdir()
        self.output_dir.mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_merge_and_cleanup_workflow(self):
        """Test the merge and cleanup workflow."""
        # Create realistic XML content
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<TEI.2>
<text>
<body>
<div1>
<entryFree id="entry1" key="test">
<form><orth lang="ar">تست</orth></form>
<hi rend="ital">A test word</hi>
<foreign lang="ar">عربي</foreign>
</entryFree>
</div1>
</body>
</text>
</TEI.2>'''
        
        with open(self.source_dir / "test.xml", 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        converter = LaneConverter(self.source_dir, self.output_dir)
        converter.merge_xml_files()
        converter.first_cleanup()
        
        # Verify the transformations occurred
        with open(converter.filename_xml, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertNotIn('<?xml', content)
        self.assertNotIn('<TEI.2>', content)
        self.assertNotIn('<entryFree', content)
        self.assertIn('_____', content)
        self.assertIn('HI_OPEN', content)
        self.assertIn('A test word', content)


if __name__ == '__main__':
    unittest.main()
