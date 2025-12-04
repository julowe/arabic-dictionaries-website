#!/usr/bin/env python3
"""
Convert Lane Arabic-English Lexicon XML files to StarDict format.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

Copyright 2015 Abu Djuwairiyyah Karim Mohammad Karimou
Converted to Python 2024
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


class LaneConverter:
    """Convert Lane Lexicon XML files to StarDict format."""

    def __init__(self, source_dir, output_dir):
        """
        Initialize the converter.

        Args:
            source_dir: Directory containing source XML files
            output_dir: Directory for output files
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.filename_xml = self.output_dir / "lane-lexicon.xml"
        self.filename_csv = self.output_dir / "lane-lexicon.csv"

    def merge_xml_files(self):
        """Merge all XML files from source directory into one file."""
        print("Stage 0: Merging XML files")
        
        xml_files = sorted(self.source_dir.glob("*.xml"))
        if not xml_files:
            raise FileNotFoundError(f"No XML files found in {self.source_dir}")
        
        with open(self.filename_xml, 'w', encoding='utf-8') as outfile:
            for xml_file in xml_files:
                with open(xml_file, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
        
        print(f"Merged {len(xml_files)} XML files into {self.filename_xml}")

    def first_cleanup(self):
        """Remove and replace XML tags."""
        print("Stage 1: First cleanup")
        
        with open(self.filename_xml, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply all the regex replacements from the bash script
        replacements = [
            (r'<entryFree.*?[^<\n\r\f]*?>', '\n\n_____\n\n'),
            (r'</entryFree>', ''),
            (r'</orth>', '\n</orth>'),
            (r'<\?xml version="1.0" encoding="UTF-8"\?>', ''),
            (r'<TEI.2>', ''),
            (r'<text>', ''),
            (r'<body>', ''),
            (r'<div1.*?[^<\n\r\f]>', ''),
            (r'<head.*?[^<\n\r\f]>', ''),
            (r'</head>', ''),
            (r'<div2.*?[^<\n\r\f]>', ''),
            (r'<form.*?[^<\n\r\f]*?>', ''),
            (r'</form>', ''),
            (r'<itype>.+?[^<\n\r\f]*?</itype>', ''),
            (r'<orth.*?[^<\n\r\f]*?>', ''),
            (r'</orth>', ''),
            (r'<hi.*?[^<\n\r\f]*?>', 'HI_OPEN'),
            (r'</hi>', 'HI_CLOSE'),
            (r'<foreign.*?[^<\n\r\f]*?>', 'FOREIGNOPEN'),
            (r'</foreign>', 'FOREIGNCLOSE'),
            (r'</div2>', ''),
            (r'<quote>', ''),
            (r'</quote>', ''),
            (r'<L>', ''),
            (r'</L>', ''),
            (r'<pb.*?[^<\n\r\f]*?>', ''),
            (r'<G/>', ''),
            (r'</div1>', ''),
            (r'</body>', ''),
            (r'</text>', ''),
            (r'</TEI.2>', ''),
            (r'<H>', ''),
            (r'</H>', ''),
            (r'<G>', ''),
            (r'</G>', ''),
            (r'<head>', ''),
            (r'<analytic/>', ''),
            (r'</author>', ''),
            (r'<author>', ''),
            (r'</authority>', ''),
            (r'<authority>', ''),
            (r'</availability>', ''),
            (r'<availability status="free">', ''),
            (r'</biblStruct>', ''),
            (r'<biblStruct>', ''),
            (r'</date>', ''),
            (r'<date>', ''),
            (r'</fileDesc>', ''),
            (r'<fileDesc>', ''),
            (r'</imprint>', ''),
            (r'<imprint>', ''),
            (r'</item>', ''),
            (r'<item>', ''),
            (r'</list>', ''),
            (r'<list>', ''),
            (r'</listBibl>', ''),
            (r'<listBibl>', ''),
            (r'</monogr>', ''),
            (r'<monogr>', ''),
            (r'</note>', ''),
            (r'<note anchored="yes" place="unspecified">', ''),
            (r'</notesStmt>', ''),
            (r'<notesStmt>', ''),
            (r'</p>', ''),
            (r'<p>', ''),
            (r'</publicationStmt>', ''),
            (r'<publicationStmt>', ''),
            (r'</publisher>', ''),
            (r'<publisher>', ''),
            (r'</pubPlace>', ''),
            (r'<pubPlace>', ''),
            (r'</sourceDesc>', ''),
            (r'<sourceDesc>', ''),
            (r'</teiHeader>', ''),
            (r'<teiHeader type="text" status="new">', ''),
            (r'</title>', ''),
            (r'<title>', ''),
            (r'</titleStmt>', ''),
            (r'<titleStmt>', ''),
            (r'<H/>', ''),
            (r'<sense>', ''),
            (r'<dictScrap>', ''),
            (r'</dictScrap>', ''),
            (r'</sense>', ''),
            (r'<Table>', 'OPENTABLE'),
            (r'<row role="data">', 'ROWROLDATA'),
            (r'<cell role="data" rows="1" cols="1">', 'CELLROLEROWSDATA'),
            (r'</cell>', 'CLOSECELL'),
            (r'</row>', 'CLOSEROW'),
            (r'</Table>', 'CLOSETABLE'),
            (r'\n\n\n', '\n'),
            (r'\n\n', '\n'),
            (r'_____', '\n\n\n_____\n'),
            (r'^\s+', ''),
            (r'�', ' '),
            (r'@', ' '),
            (r'=', ' '),
            (r'\r', '\n'),
            (r'foreignopen', ''),
            (r'_____\s*(.*?see)', r'\1'),
            (r'\f', '\n'),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        with open(self.filename_xml, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("First cleanup completed")

    def convert_to_dictd(self):
        """Convert to dictd format using dictfmt."""
        print("Stage 2: Converting to dictd format")
        
        # Check if dictfmt is available
        try:
            result = subprocess.run(['dictfmt', '--version'], 
                                  capture_output=True)
            # dictfmt --version returns exit code 1, so just check if it runs
        except FileNotFoundError:
            raise RuntimeError("dictfmt not found. Please install dictd-tools package.")
        
        # Convert without tashkeel
        no_tashkeel = self.output_dir / "lane-lexicon-no-tashkeel"
        subprocess.run([
            'dictfmt', '--utf8', 
            '-u', 'dfmcreator@gmail.com',
            '-s', 'Lane Arabic-English Lexicon',
            '-c5', str(no_tashkeel)
        ], stdin=open(self.filename_xml, 'r'), check=True)
        
        # Delete inconsistencies from index file
        index_file = no_tashkeel.with_suffix('.index')
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(index_file, 'w', encoding='utf-8') as f:
                f.writelines(lines[600:])
        
        # Convert with tashkeel
        tashkeel = self.output_dir / "lane-lexicon-tashkeel"
        subprocess.run([
            'dictfmt', '--utf8', '--allchars',
            '-u', 'dfmcreator@gmail.com',
            '-s', 'Lane Arabic-English Lexicon',
            '-c5', str(tashkeel)
        ], stdin=open(self.filename_xml, 'r'), check=True)
        
        # Delete inconsistencies from index file
        index_file = tashkeel.with_suffix('.index')
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(index_file, 'w', encoding='utf-8') as f:
                f.writelines(lines[602:])
        
        print("Dictd conversion completed")

    def convert_to_csv_with_pyglossary(self):
        """Convert dictd format to CSV using pyglossary."""
        print("Stage 3: Converting to CSV with pyglossary")
        
        # Check if pyglossary is available
        try:
            subprocess.run(['pyglossary', '--version'], 
                         capture_output=True, check=False)
        except FileNotFoundError:
            raise RuntimeError(
                "pyglossary not found. Please install it with: pip install pyglossary"
            )
        
        no_tashkeel_index = self.output_dir / "lane-lexicon-no-tashkeel.index"
        tashkeel_index = self.output_dir / "lane-lexicon-tashkeel.index"
        
        no_tashkeel_txt = self.output_dir / "lane-lexicon-no-tashkeel.txt"
        tashkeel_txt = self.output_dir / "lane-lexicon-tashkeel.txt"
        
        # Convert using pyglossary command line (like the original bash script)
        for index_file, output_file in [
            (no_tashkeel_index, no_tashkeel_txt),
            (tashkeel_index, tashkeel_txt)
        ]:
            if index_file.exists():
                subprocess.run([
                    'pyglossary',
                    str(index_file),
                    str(output_file)
                ], check=True)
        
        # Combine the two files
        with open(self.filename_csv, 'w', encoding='utf-8') as outfile:
            if no_tashkeel_txt.exists():
                with open(no_tashkeel_txt, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
            if tashkeel_txt.exists():
                with open(tashkeel_txt, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
        
        print("CSV conversion completed")

    def second_cleanup(self):
        """Apply second round of cleanup to CSV."""
        print("Stage 4: Second cleanup")
        
        with open(self.filename_csv, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply replacements
        content = re.sub(r'\t', '#####_____#####_____#####', content)
        content = re.sub(r'\\n', '<br>', content)
        content = re.sub(r'<k>', '', content)
        content = re.sub(r'</k>', '', content)
        content = re.sub(r'<br>', ' ', content)
        
        with open(self.filename_csv, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Second cleanup completed")

    def put_colors(self):
        """Add HTML color formatting."""
        print("Stage 5: Adding colors")
        
        with open(self.filename_csv, 'r', encoding='utf-8') as f:
            content = f.read()
        
        replacements = [
            (r'FOREIGNOPEN', ''),
            (r'FOREIGNCLOSE', ''),
            (r'OPENTABLE', '<Table>'),
            (r'ROWROLDATA', '<row role="data">'),
            (r'CELLROLEROWSDATA', '<cell role="data" rows="1" cols="1">'),
            (r'CLOSECELL', '</cell>'),
            (r'CLOSEROW', '</row>'),
            (r'CLOSETABLE', '</Table>'),
            (r'HI_OPEN', '<b><i><FONT COLOR="DarkBlue">'),
            (r'HI_CLOSE', '</FONT></i></b>'),
            (r'― - ', '―'),
            (r'-', '―'),
            (r'― ―', '―'),
            (r'((―|-)*a[0-9]+(―|-)+)', r'<p></p><b><FONT COLOR="DarkSlateGray">[\1]</FONT></b>'),
            (r'((―|-)*b[0-9]+(―|-)+)', r'<p></p><b><FONT COLOR="DarkRed">[\1]</FONT></b>'),
            (r'((―|-)*A[0-9]+(―|-)+)', r'<p></p><b><FONT COLOR="SaddleBrown">[\1]</FONT></b>'),
            (r'((―|-)*B[0-9]+(―|-)+)', r'<p></p><b><FONT COLOR="Indigo">[\1]</FONT></b>'),
            (r'(\(.+?[^(\n\f\r]\))', r'<b><i><FONT COLOR="DarkOliveGreen"> \1 </FONT></i></b>'),
            (r'[ ]{2,}', ' '),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        with open(self.filename_csv, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Color formatting completed")

    def convert_to_stardict(self, tabfile_path=None):
        """Convert to StarDict format using tabfile tool."""
        print("Stage 6: Converting to StarDict format")
        
        # Restore tab character
        with open(self.filename_csv, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r'#####_____#####_____#####', '\t', content)
        with open(self.filename_csv, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Add newline at end if not present
        with open(self.filename_csv, 'r+b') as f:
            f.seek(-1, 2)
            last_char = f.read(1)
            if last_char != b'\n':
                f.write(b'\n')
        
        # Find tabfile executable
        if tabfile_path is None:
            # Look for tabfile in common locations
            possible_paths = [
                Path(__file__).parent.parent.parent / 'deps' / 'tabfile',
                Path('/usr/local/bin/tabfile'),
                Path('/usr/bin/tabfile'),
            ]
            for path in possible_paths:
                if path.exists():
                    tabfile_path = path
                    break
        
        if tabfile_path is None or not Path(tabfile_path).exists():
            raise RuntimeError(
                "tabfile executable not found. Please specify path or install it."
            )
        
        # Run tabfile
        csv_abs = self.filename_csv.resolve()
        subprocess.run([str(tabfile_path), str(csv_abs)], 
                      cwd=self.output_dir, check=True)
        
        print("StarDict conversion completed")

    def clean_up(self):
        """Remove temporary files."""
        print("Cleaning up temporary files")
        
        temp_files = [
            self.filename_xml,
            self.output_dir / "lane-lexicon-tashkeel.txt",
            self.output_dir / "lane-lexicon-no-tashkeel.txt",
            self.output_dir / "lane-lexicon-no-tashkeel.index",
            self.output_dir / "lane-lexicon-no-tashkeel.dict",
            self.output_dir / "lane-lexicon-tashkeel.index",
            self.output_dir / "lane-lexicon-tashkeel.dict",
            self.output_dir / "stardict-lane-lexicon-2.4.2",
        ]
        
        for file in temp_files:
            if Path(file).exists():
                if Path(file).is_dir():
                    import shutil
                    shutil.rmtree(file)
                else:
                    Path(file).unlink()
        
        print("Cleanup completed")

    def convert(self, clean=True, tabfile_path=None):
        """
        Run the complete conversion process.
        
        Args:
            clean: Whether to clean up temporary files
            tabfile_path: Path to tabfile executable
        
        Returns:
            List of output files created
        """
        try:
            self.merge_xml_files()
            self.first_cleanup()
            self.convert_to_dictd()
            self.convert_to_csv_with_pyglossary()
            self.second_cleanup()
            self.put_colors()
            self.convert_to_stardict(tabfile_path)
            
            if clean:
                self.clean_up()
            
            # Return list of expected output files
            output_files = [
                self.output_dir / "lane-lexicon.dict.dz",
                self.output_dir / "lane-lexicon.idx",
                self.output_dir / "lane-lexicon.ifo",
            ]
            
            return [f for f in output_files if f.exists()]
            
        except Exception as e:
            print(f"Error during conversion: {e}", file=sys.stderr)
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Convert Lane Lexicon XML files to StarDict format'
    )
    parser.add_argument(
        '--source-dir',
        default='../source-lane',
        help='Directory containing source XML files (default: ../source-lane)'
    )
    parser.add_argument(
        '--output-dir',
        default='.',
        help='Directory for output files (default: current directory)'
    )
    parser.add_argument(
        '--tabfile',
        help='Path to tabfile executable'
    )
    parser.add_argument(
        '--no-clean',
        action='store_true',
        help='Do not clean up temporary files'
    )
    
    args = parser.parse_args()
    
    converter = LaneConverter(args.source_dir, args.output_dir)
    output_files = converter.convert(clean=not args.no_clean, 
                                     tabfile_path=args.tabfile)
    
    print("\nConversion completed successfully!")
    print("Output files:")
    for f in output_files:
        print(f"  - {f}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
