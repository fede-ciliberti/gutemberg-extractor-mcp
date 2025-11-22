#!/usr/bin/env python3
"""
Gutenberg Resource Extractor
===========================

Herramienta para extraer recursos grandes embebidos en archivos Gutenberg
exportados desde Figma y optimizarlos para reducir el tamaño del contexto.

Autor: Roo AI Agent
Versión: 1.0.0
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

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GutenbergExtractor:
    """Extractor de recursos embebidos para archivos Gutenberg."""
    
    def __init__(self, threshold_kb: int = 1):
        """
        Inicializar el extractor.
        
        Args:
            threshold_kb: Umbral en KB para extraer recursos (default: 1KB)
        """
        self.threshold_kb = threshold_kb
        self.threshold_bytes = threshold_kb * 1024
        
        # Patrones regex para diferentes tipos de data URIs
        self.patterns = {
            'svg': re.compile(r'data:image/svg\+xml(?:;charset=utf-8)?,(?P<content>[^"\'<]+)'),
            'png': re.compile(r'data:image/png(?:;charset=utf-8)?;base64,\s*(?P<content>[A-Za-z0-9+/=]+)'),
            'jpg': re.compile(r'data:image/jpeg(?:;charset=utf-8)?;base64,\s*(?P<content>[A-Za-z0-9+/=]+)'),
            'webp': re.compile(r'data:image/webp(?:;charset=utf-8)?;base64,\s*(?P<content>[A-Za-z0-9+/=]+)'),
            'gif': re.compile(r'data:image/gif(?:;charset=utf-8)?;base64,\s*(?P<content>[A-Za-z0-9+/=]+)')
        }
        
        # Mapeo de tipos a extensiones
        self.type_extensions = {
            'svg': '.svg',
            'png': '.png',
            'jpg': '.jpg',
            'webp': '.webp',
            'gif': '.gif'
        }
        
        # Contadores para estadísticas
        self.stats = {
            'total_resources': 0,
            'extracted': 0,
            'skipped': 0,
            'original_size': 0,
            'optimized_size': 0
        }
    
    def extract_data_uri_content(self, match: re.Match, resource_type: str) -> Optional[bytes]:
        """
        Extraer contenido de un data URI.
        
        Args:
            match: Match regex
            resource_type: Tipo de recurso ('svg', 'png', etc.)
            
        Returns:
            Contenido decodificado o None si falla
        """
        try:
            if resource_type == 'svg':
                # Los SVG pueden estar URL-encoded
                import urllib.parse
                content = urllib.parse.unquote(match.group('content'))
                # Verificar si es un SVG válido (debe tener <svg> al inicio)
                if not content.strip().startswith('<svg'):
                    logger.warning(f"SVG inválido detectado: {content[:50]}...")
                    return content.encode('utf-8')  # Devolver el contenido tal como está
                return content.encode('utf-8')
            else:
                # Base64 para otros tipos
                content = match.group('content')
                # Manejar padding incompleto en base64
                missing_padding = len(content) % 4
                if missing_padding:
                    content += '=' * (4 - missing_padding)
                return base64.b64decode(content)
        except Exception as e:
            logger.error(f"Error decodificando {resource_type}: {e}")
            return None
    
    def calculate_hash(self, data: bytes) -> str:
        """
        Calcular hash MD5 de los datos.
        
        Args:
            data: Datos binarios
            
        Returns:
            Hash MD5 en hexadecimal
        """
        return hashlib.md5(data).hexdigest()[:12]
    
    def generate_filename(self, resource_type: str, content_hash: str, index: int) -> str:
        """
        Generar nombre de archivo para el recurso.
        
        Args:
            resource_type: Tipo de recurso
            content_hash: Hash del contenido
            index: Índice del recurso
            
        Returns:
            Nombre de archivo generado
        """
        extension = self.type_extensions.get(resource_type, '.bin')
        return f"{resource_type}_{content_hash}_{index}{extension}"
    
    def extract_resources_from_file(self, file_path: Path, output_dir: Path) -> Tuple[str, List[Dict]]:
        """
        Extraer recursos de un archivo Gutenberg.
        
        Args:
            file_path: Ruta del archivo origen
            output_dir: Directorio de salida para recursos
            
        Returns:
            Tupla (contenido_optimizado, metadatos)
        """
        logger.info(f"Procesando archivo: {file_path}")
        
        # Leer archivo original
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        self.stats['original_size'] = len(original_content)
        optimized_content = original_content
        extracted_resources = []
        resource_index = 0
        
        # Procesar cada tipo de data URI
        for resource_type, pattern in self.patterns.items():
            matches = list(pattern.finditer(original_content))
            logger.info(f"Encontrados {len(matches)} recursos {resource_type}")
            
            for match in matches:
                self.stats['total_resources'] += 1
                
                # Extraer contenido
                content = self.extract_data_uri_content(match, resource_type)
                if not content:
                    self.stats['skipped'] += 1
                    continue
                
                # Verificar tamaño
                if len(content) < self.threshold_bytes:
                    self.stats['skipped'] += 1
                    logger.info(f"Recurso {resource_type} muy pequeño ({len(content)} bytes), omitido")
                    continue
                
                # Generar archivo de salida
                content_hash = self.calculate_hash(content)
                filename = self.generate_filename(resource_type, content_hash, resource_index)
                resource_path = output_dir / filename
                
                # Escribir archivo
                try:
                    with open(resource_path, 'wb') as f:
                        f.write(content)
                    
                    # Calcular URL relativa
                    relative_url = f"assets/{filename}"
                    
                    # Reemplazar en el contenido optimizado
                    replacement = f'src="{relative_url}"'
                    optimized_content = optimized_content.replace(match.group(0), replacement, 1)
                    
                    # Guardar metadatos
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
                    
                    logger.info(f"Extraído: {filename} ({len(content)} bytes)")
                    
                except Exception as e:
                    logger.error(f"Error guardando {filename}: {e}")
                    self.stats['skipped'] += 1
        
        self.stats['optimized_size'] = len(optimized_content)
        
        return optimized_content, extracted_resources
    
    def process_file(self, input_file: str, output_dir: Optional[str] = None) -> Dict:
        """
        Procesar un archivo Gutenberg completo con nueva convención de nomenclatura.
        
        Args:
            input_file: Ruta del archivo de entrada (.gutemberg)
            output_dir: Directorio de salida (opcional)
            
        Returns:
            Diccionario con resultados del procesamiento
        """
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {input_file}")
        
        # Validar que sea un archivo .gutemberg
        if not input_path.suffix == '.gutemberg':
            raise ValueError(f"El archivo debe tener extensión .gutemberg, recibido: {input_path.suffix}")
        
        # Determinar directorio de salida
        if output_dir is None:
            output_dir = input_path.parent / input_path.stem
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear subdirectorio para assets
        assets_dir = output_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        logger.info(f"Directorio de salida: {output_dir}")
        
        # Extraer recursos
        optimized_content, resources = self.extract_resources_from_file(input_path, assets_dir)
        
        # Guardar archivo optimizado como index.html
        optimized_file = output_dir / "index.html"
        with open(optimized_file, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
        
        # Guardar metadatos
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
        
        logger.info(f"Procesamiento completado con nueva convención:")
        logger.info(f"  - Input: {input_path.name}")
        logger.info(f"  - Output: {output_dir}/index.html")
        logger.info(f"  - Assets: {output_dir}/assets/")
        logger.info(f"  - Recursos totales: {self.stats['total_resources']}")
        logger.info(f"  - Extraídos: {self.stats['extracted']}")
        logger.info(f"  - Omitidos: {self.stats['skipped']}")
        logger.info(f"  - Tamaño original: {self.stats['original_size']:,} bytes")
        logger.info(f"  - Tamaño optimizado: {self.stats['optimized_size']:,} bytes")
        logger.info(f"  - Reducción: {((self.stats['original_size'] - self.stats['optimized_size']) / self.stats['original_size'] * 100):.1f}%")
        
        return metadata


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Extractor de recursos para archivos Gutenberg (.gutemberg)')
    parser.add_argument('input_file', help='Archivo Gutenberg a procesar (.gutemberg)')
    parser.add_argument('-o', '--output', help='Directorio de salida (opcional)')
    parser.add_argument('-t', '--threshold', type=int, default=1,
                       help='Umbral en KB para extraer recursos (default: 1KB)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Output detallado')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        extractor = GutenbergExtractor(threshold_kb=args.threshold)
        metadata = extractor.process_file(args.input_file, args.output)
        
        print(f"\n✅ Procesamiento completado exitosamente con nueva convención!")
        print(f"📄 Input: {metadata['original_filename']}")
        print(f"🏠 Output: {metadata['optimized_file']}")
        print(f"📂 Assets: {metadata['assets_directory']}")
        print(f"📁 Metadata: {metadata['output_directory']}/extraction_metadata.json")
        print(f"💾 Reducción: {((metadata['statistics']['original_size'] - metadata['statistics']['optimized_size']) / metadata['statistics']['original_size'] * 100):.1f}%")
        
    except Exception as e:
        logger.error(f"Error procesando archivo: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())