#!/usr/bin/env python3
"""
Gutenberg Resource Extractor
=============================

Tool to extract large embedded resources in Gutenberg files
exported from Figma and optimize them to reduce context size.

Author: Roo AI Agent
Version: 1.0.0
"""

import os
import re
import base64
import hashlib
import argparse
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GutenbergExtractor:
    """Extractor for embedded resources in Gutenberg files."""
    
    def __init__(self, threshold_kb: int = 1):
        """
        Initialize the extractor.
        
        Args:
            threshold_kb: Threshold in KB to extract resources (default: 1KB)
        """
        self.threshold_kb = threshold_kb
        self.threshold_bytes = threshold_kb * 1024
        
        # Regex patterns for different data URI types
        self.patterns = {
            'svg': re.compile(r'data:image/svg\+xml(?:;charset=utf-8)?,(?P<content>[^"\'<]+)'),
            'png': re.compile(r'data:image/png(?:;charset=utf-8)?;base64,\s*(?P<content>[A-Za-z0-9+/=]+)'),
            'jpg': re.compile(r'data:image/jpeg(?:;charset=utf-8)?;base64,\s*(?P<content>[A-Za-z0-9+/=]+)'),
            'webp': re.compile(r'data:image/webp(?:;charset=utf-8)?;base64,\s*(?P<content>[A-Za-z0-9+/=]+)'),
            'gif': re.compile(r'data:image/gif(?:;charset=utf-8)?;base64,\s*(?P<content>[A-Za-z0-9+/=]+)')
        }
        
        # Mapping of types to extensions
        self.type_extensions = {
            'svg': '.svg',
            'png': '.png',
            'jpg': '.jpg',
            'webp': '.webp',
            'gif': '.gif'
        }
        
        # Counters for statistics
        self.stats = {
            'total_resources': 0,
            'extracted': 0,
            'skipped': 0,
            'original_size': 0,
            'optimized_size': 0
        }
    
    def extract_data_uri_content(self, match: re.Match, resource_type: str) -> Optional[bytes]:
        """
        Extract content from a data URI.
        
        Args:
            match: Regex match
            resource_type: Resource type ('svg', 'png', etc.)
            
        Returns:
            Decoded content or None if fails
        """
        try:
            if resource_type == 'svg':
                # SVGs may be URL-encoded
                import urllib.parse
                content = urllib.parse.unquote(match.group('content'))
                # Check if it's a valid SVG (must have <svg> at start)
                if not content.strip().startswith('<svg'):
                    logger.warning(f"Invalid SVG detected: {content[:50]}...")
                    return content.encode('utf-8')  # Return content as-is
                return content.encode('utf-8')
            else:
                # Base64 for other types
                content = match.group('content')
                # Handle incomplete base64 padding
                missing_padding = len(content) % 4
                if missing_padding:
                    content += '=' * (4 - missing_padding)
                return base64.b64decode(content)
        except Exception as e:
            logger.error(f"Error decoding {resource_type}: {e}")
            return None
    
    def calculate_hash(self, data: bytes) -> str:
        """
        Calculate MD5 hash of data.
        
        Args:
            data: Binary data
            
        Returns:
            Hexadecimal MD5 hash
        """
        return hashlib.md5(data).hexdigest()[:12]
    
    def generate_filename(self, resource_type: str, content_hash: str, index: int) -> str:
        """
        Generate filename for the resource.
        
        Args:
            resource_type: Resource type
            content_hash: Content hash
            index: Resource index
            
        Returns:
            Generated filename
        """
        extension = self.type_extensions.get(resource_type, '.bin')
        return f"{resource_type}_{content_hash}_{index}{extension}"
    
    def extract_resources_from_file(self, file_path: Path, output_dir: Path) -> Tuple[str, List[Dict]]:
        """
        Extract resources from a Gutenberg file.
        
        Args:
            file_path: Source file path
            output_dir: Output directory for resources
            
        Returns:
            Tuple (optimized_content, metadata)
        """
        logger.info(f"Processing file: {file_path}")
        
        # Read original file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        self.stats['original_size'] = len(original_content)
        optimized_content = original_content
        extracted_resources = []
        resource_index = 0
        
        # Process each data URI type
        for resource_type, pattern in self.patterns.items():
            matches = list(pattern.finditer(original_content))
            logger.info(f"Found {len(matches)} {resource_type} resources")
            
            for match in matches:
                self.stats['total_resources'] += 1
                
                # Extract content
                content = self.extract_data_uri_content(match, resource_type)
                if not content:
                    self.stats['skipped'] += 1
                    continue
                
                # Check size
                if len(content) < self.threshold_bytes:
                    self.stats['skipped'] += 1
                    logger.info(f"{resource_type} resource too small ({len(content)} bytes), skipped")
                    continue
                
                # Generate output file
                content_hash = self.calculate_hash(content)
                filename = self.generate_filename(resource_type, content_hash, resource_index)
                resource_path = output_dir / filename
                
                # Write file
                try:
                    with open(resource_path, 'wb') as f:
                        f.write(content)
                    
                    # Calculate relative URL
                    relative_url = f"assets/{filename}"
                    
                    # Replace in optimized content
                    replacement = f'src="{relative_url}"'
                    optimized_content = optimized_content.replace(match.group(0), replacement, 1)
                    
                    # Save metadata
                    resource_info = {
                        'type': resource_type,
                        'original_data_uri': match.group(0),
                        'file': filename,
                        'path': str(resource_path),
                        'relative_url': relative_url,
                        'size_bytes': len(content),
                        'content_hash': content_hash,
                        'match_position': match.start()
                    }
                    extracted_resources.append(resource_info)
                    
                    self.stats['extracted'] += 1
                    resource_index += 1
                    
                    logger.info(f"Extracted: {filename} ({len(content)} bytes)")
                    
                except Exception as e:
                    logger.error(f"Error saving {filename}: {e}")
                    self.stats['skipped'] += 1
        
        self.stats['optimized_size'] = len(optimized_content)
        
        return optimized_content, extracted_resources
    
    def process_file(self, input_file: str, output_dir: Optional[str] = None) -> Dict:
        """
        Process a complete Gutenberg file with new naming convention.
        
        Args:
            input_file: Input file path (.gutemberg)
            output_dir: Output directory (optional)
            
        Returns:
            Dictionary with processing results
        """
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_file}")
        
        # Validate that it's a .gutemberg file
        if not input_path.suffix == '.gutemberg':
            raise ValueError(f"File must have .gutemberg extension, received: {input_path.suffix}")
        
        # Determine output directory
        if output_dir is None:
            output_dir = input_path.parent / input_path.stem
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create assets subdirectory
        assets_dir = output_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        logger.info(f"Output directory: {output_dir}")
        
        # Extract resources
        optimized_content, resources = self.extract_resources_from_file(input_path, assets_dir)
        
        # Save optimized file as index.html
        optimized_file = output_dir / "index.html"
        with open(optimized_file, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
        
        # Save metadata
        metadata = {
            'original_file': str(input_path),
            'original_filename': input_path.name,
            'optimized_file': str(optimized_file),
            'optimized_filename': 'index.html',
            'assets_directory': str(assets_dir),
            'output_directory': str(output_dir),
            'extraction_timestamp': __import__('datetime').datetime.now().isoformat(),
            'threshold_kb': self.threshold_kb,
            'extracted_resources': resources,
            'statistics': self.stats.copy(),
            'new_convention': {
                'input_extension': '.gutemberg',
                'output_main_file': 'index.html',
                'assets_folder': 'assets/'
            }
        }
        
        metadata_file = output_dir / "extraction_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Processing completed with new convention:")
        logger.info(f"  - Input: {input_path.name}")
        logger.info(f"  - Output: {output_dir}/index.html")
        logger.info(f"  - Assets: {output_dir}/assets/")
        logger.info(f"  - Total resources: {self.stats['total_resources']}")
        logger.info(f"  - Extracted: {self.stats['extracted']}")
        logger.info(f"  - Skipped: {self.stats['skipped']}")
        logger.info(f"  - Original size: {self.stats['original_size']:,} bytes")
        logger.info(f"  - Optimized size: {self.stats['optimized_size']:,} bytes")
        logger.info(f"  - Reduction: {((self.stats['original_size'] - self.stats['optimized_size']) / self.stats['original_size'] * 100):.1f}%")
        
        return metadata


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Resource extractor for Gutenberg files (.gutemberg)')
    parser.add_argument('input_file', help='Gutenberg file to process (.gutemberg)')
    parser.add_argument('-o', '--output', help='Output directory (optional)')
    parser.add_argument('-t', '--threshold', type=int, default=1,
                       help='Threshold in KB to extract resources (default: 1KB)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        extractor = GutenbergExtractor(threshold_kb=args.threshold)
        metadata = extractor.process_file(args.input_file, args.output)
        
        print(f"\n✅ Processing completed successfully with new convention!")
        print(f"📄 Input: {metadata['original_filename']}")
        print(f"🏠 Output: {metadata['optimized_file']}")
        print(f"📂 Assets: {metadata['assets_directory']}")
        print(f"📁 Metadata: {metadata['output_directory']}/extraction_metadata.json")
        print(f"💾 Reduction: {((metadata['statistics']['original_size'] - metadata['statistics']['optimized_size']) / metadata['statistics']['original_size'] * 100):.1f}%")
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())