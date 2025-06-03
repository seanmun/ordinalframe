#!/usr/bin/env python3
"""
Ordinal Frame - Main Flask Server
A Bitcoin-native digital art display for Ordinals inscriptions
"""

import os
import sys
import json
import time
import logging
import requests
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urlparse
from typing import Dict, List, Optional, Union

import coloredlogs
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash
from werkzeug.exceptions import RequestTimeout
from PIL import Image
import diskcache as dc

# Configuration and Constants
class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # API settings
    HIRO_API_BASE = os.getenv('HIRO_API_BASE_URL', 'https://api.hiro.so/ordinals/v1')
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    
    # File paths
    BASE_DIR = Path(__file__).parent
    ORDINALS_DIR = BASE_DIR / 'ordinals'
    CACHE_DIR = ORDINALS_DIR / 'cached'
    METADATA_DIR = ORDINALS_DIR / 'metadata'
    LOGS_DIR = BASE_DIR / 'logs'
    
    # File names
    METADATA_FILE = METADATA_DIR / 'ordinals.json'
    SELECTION_FILE = METADATA_DIR / 'selection.json'
    LOG_FILE = LOGS_DIR / 'ordinal-frame.log'
    
    # Image settings
    MAX_IMAGE_SIZE_MB = int(os.getenv('MAX_IMAGE_SIZE_MB', 50))
    SUPPORTED_FORMATS = os.getenv('SUPPORTED_FORMATS', 'jpg,jpeg,png,gif,svg,webp,avif').split(',')
    
    # Display settings
    DEFAULT_SLIDESHOW_INTERVAL = int(os.getenv('DEFAULT_SLIDESHOW_INTERVAL', 30))
    TOUCH_HOLD_DURATION = int(os.getenv('TOUCH_HOLD_DURATION', 500))
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        for directory in [cls.ORDINALS_DIR, cls.CACHE_DIR, cls.METADATA_DIR, cls.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

# Setup logging
def setup_logging():
    """Configure application logging"""
    Config.ensure_directories()
    
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Setup colored logs for console
    coloredlogs.install(
        level=log_level,
        fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup file logging
    file_handler = logging.FileHandler(Config.LOG_FILE)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

# Bitcoin address validation
def validate_bitcoin_address(address: str) -> Dict[str, Union[bool, str]]:
    """
    Validate Bitcoin address format
    Returns: dict with 'valid' boolean and 'type' string
    """
    if not address or not isinstance(address, str):
        return {'valid': False, 'type': 'invalid', 'error': 'Address is required'}
    
    address = address.strip()
    
    # Legacy address (P2PKH: starts with 1, P2SH: starts with 3)
    if address.startswith(('1', '3')):
        if 25 <= len(address) <= 34:
            return {'valid': True, 'type': 'legacy'}
    
    # Bech32 address (P2WPKH/P2WSH: starts with bc1)
    elif address.startswith('bc1'):
        if len(address) >= 42:  # Bech32 addresses are longer
            if address.startswith('bc1q'):
                return {'valid': True, 'type': 'segwit_v0'}
            elif address.startswith('bc1p'):
                return {'valid': True, 'type': 'taproot'}
            else:
                return {'valid': True, 'type': 'segwit'}
    
    return {'valid': False, 'type': 'invalid', 'error': 'Invalid Bitcoin address format'}

# API Client for Ordinals data
class OrdinalsAPIClient:
    """Client for fetching Ordinals data from various APIs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.timeout = Config.REQUEST_TIMEOUT
        
        # Setup cache
        self.cache = dc.Cache(str(Config.CACHE_DIR / 'api_cache'))
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request with retries and error handling"""
        for attempt in range(Config.MAX_RETRIES):
            try:
                self.logger.info(f"Making request to {url} (attempt {attempt + 1})")
                
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt == Config.MAX_RETRIES - 1:
                    raise RequestTimeout("API request timed out")
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed: {e}")
                if attempt == Config.MAX_RETRIES - 1:
                    raise
                time.sleep(2 ** attempt)
        
        return None
    
    def fetch_address_inscriptions(self, address: str) -> List[Dict]:
        """Fetch all inscriptions for a Bitcoin address"""
        # Check cache first (cache for 1 hour)
        cache_key = f"inscriptions_{address}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result is not None:
            self.logger.info(f"Using cached data for address {address}")
            return cached_result
        
        self.logger.info(f"Fetching inscriptions for address: {address}")
        
        try:
            # Primary API: Hiro Ordinals API
            url = f"{Config.HIRO_API_BASE}/inscriptions"
            params = {
                'address': address,
                'limit': 60,  # Maximum limit per request
                'offset': 0
            }
            
            all_inscriptions = []
            
            while True:
                data = self._make_request(url, params)
                if not data or 'results' not in data:
                    break
                
                inscriptions = data['results']
                if not inscriptions:
                    break
                
                all_inscriptions.extend(inscriptions)
                
                # Check if there are more pages
                if len(inscriptions) < params['limit']:
                    break
                
                params['offset'] += params['limit']
                
                # Prevent infinite loops
                if params['offset'] > 1000:
                    self.logger.warning("Stopping pagination after 1000 inscriptions")
                    break
            
            # Process and clean the data
            processed_inscriptions = []
            for inscription in all_inscriptions:
                processed = self._process_inscription_data(inscription)
                if processed:
                    processed_inscriptions.append(processed)
            
            # Cache the result
            self.cache.set(cache_key, processed_inscriptions, expire=3600)  # 1 hour
            
            self.logger.info(f"Found {len(processed_inscriptions)} inscriptions for {address}")
            return processed_inscriptions
            
        except Exception as e:
            self.logger.error(f"Error fetching inscriptions: {e}")
            return []
    
    def _process_inscription_data(self, raw_data: Dict) -> Optional[Dict]:
        """Process raw inscription data into clean format"""
        try:
            inscription_id = raw_data.get('id', '')
            if not inscription_id:
                return None
            
            # Extract content URL
            content_url = f"{Config.HIRO_API_BASE}/inscriptions/{inscription_id}/content"
            
            return {
                'id': inscription_id,
                'number': raw_data.get('number', 0),
                'address': raw_data.get('address', ''),
                'content_type': raw_data.get('content_type', 'unknown'),
                'content_length': raw_data.get('content_length', 0),
                'content_url': content_url,
                'timestamp': raw_data.get('timestamp', 0),
                'sat_ordinal': raw_data.get('sat_ordinal'),
                'sat_rarity': raw_data.get('sat_rarity', 'common'),
                'fee': raw_data.get('fee', 0),
                'value': raw_data.get('value', 0),
                'block_height': raw_data.get('genesis_block_height', 0),
                'tx_id': raw_data.get('genesis_tx_id', ''),
                'collection_slug': raw_data.get('collection_slug'),
                'metadata': raw_data.get('metadata', {})
            }
        except Exception as e:
            self.logger.error(f"Error processing inscription data: {e}")
            return None

# Ordinals Manager
class OrdinalsManager:
    """Manages local Ordinals data, metadata, and selection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_client = OrdinalsAPIClient()
        
        Config.ensure_directories()
        
        # Load existing data
        self.metadata = self._load_metadata()
        self.selection = self._load_selection()
    
    def _load_metadata(self) -> Dict:
        """Load Ordinals metadata from JSON file"""
        if Config.METADATA_FILE.exists():
            try:
                with open(Config.METADATA_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                self.logger.error(f"Error loading metadata: {e}")
        
        return {'ordinals': [], 'last_updated': None, 'address': None}
    
    def _save_metadata(self):
        """Save metadata to JSON file"""
        try:
            with open(Config.METADATA_FILE, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except IOError as e:
            self.logger.error(f"Error saving metadata: {e}")
    
    def _load_selection(self) -> Dict:
        """Load user's Ordinal selection"""
        if Config.SELECTION_FILE.exists():
            try:
                with open(Config.SELECTION_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                self.logger.error(f"Error loading selection: {e}")
        
        return {'selected_ids': [], 'slideshow_interval': Config.DEFAULT_SLIDESHOW_INTERVAL}
    
    def _save_selection(self):
        """Save selection to JSON file"""
        try:
            with open(Config.SELECTION_FILE, 'w') as f:
                json.dump(self.selection, f, indent=2)
        except IOError as e:
            self.logger.error(f"Error saving selection: {e}")
    
    def fetch_address_ordinals(self, address: str) -> Dict[str, Union[bool, str, List]]:
        """Fetch Ordinals for a given address"""
        self.logger.info(f"Fetching Ordinals for address: {address}")
        
        try:
            inscriptions = self.api_client.fetch_address_inscriptions(address)
            
            # Filter for supported image types
            image_inscriptions = []
            for inscription in inscriptions:
                content_type = inscription.get('content_type', '').lower()
                if any(fmt in content_type for fmt in ['image', 'svg']):
                    image_inscriptions.append(inscription)
            
            # Update metadata
            self.metadata = {
                'ordinals': image_inscriptions,
                'last_updated': datetime.now().isoformat(),
                'address': address,
                'total_count': len(inscriptions),
                'image_count': len(image_inscriptions)
            }
            self._save_metadata()
            
            return {
                'success': True,
                'message': f"Found {len(image_inscriptions)} image inscriptions",
                'ordinals': image_inscriptions,
                'total_count': len(inscriptions),
                'image_count': len(image_inscriptions)
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching Ordinals: {e}")
            return {
                'success': False,
                'message': f"Error fetching Ordinals: {str(e)}",
                'ordinals': []
            }
    
    def update_selection(self, selected_ids: List[str]) -> bool:
        """Update user's Ordinal selection"""
        try:
            self.selection['selected_ids'] = selected_ids
            self.selection['last_updated'] = datetime.now().isoformat()
            self._save_selection()
            
            self.logger.info(f"Updated selection: {len(selected_ids)} Ordinals selected")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating selection: {e}")
            return False
    
    def get_selected_ordinals(self) -> List[Dict]:
        """Get currently selected Ordinals with metadata"""
        selected_ids = self.selection.get('selected_ids', [])
        all_ordinals = self.metadata.get('ordinals', [])
        
        selected_ordinals = []
        for ordinal in all_ordinals:
            if ordinal['id'] in selected_ids:
                selected_ordinals.append(ordinal)
        
        return selected_ordinals

# Flask Application Setup
def create_app() -> Flask:
    """Create and configure Flask application"""
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize managers
    ordinals_manager = OrdinalsManager()
    
    @app.route('/')
    def index():
        """Main landing page"""
        return render_template('index.html')
    
    @app.route('/setup')
    def setup():
        """Setup page for entering wallet address"""
        return render_template('setup.html')
    
    @app.route('/select')
    def select():
        """Ordinal selection page"""
        ordinals = ordinals_manager.metadata.get('ordinals', [])
        selected_ids = ordinals_manager.selection.get('selected_ids', [])
        
        return render_template('select.html', 
                             ordinals=ordinals, 
                             selected_ids=selected_ids)
    
    @app.route('/frame')
    def frame():
        """Main frame display"""
        selected_ordinals = ordinals_manager.get_selected_ordinals()
        
        if not selected_ordinals:
            # Redirect to setup if no Ordinals selected
            return redirect(url_for('setup'))
        
        return render_template('frame.html', 
                             ordinals=selected_ordinals,
                             slideshow_interval=ordinals_manager.selection.get('slideshow_interval', 30))
    
    # API Routes
    @app.route('/api/fetch-ordinals', methods=['POST'])
    def api_fetch_ordinals():
        """API endpoint to fetch Ordinals for an address"""
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({'success': False, 'message': 'Address is required'}), 400
        
        address = data['address'].strip()
        
        # Validate address
        validation = validate_bitcoin_address(address)
        if not validation['valid']:
            return jsonify({
                'success': False, 
                'message': validation.get('error', 'Invalid Bitcoin address')
            }), 400
        
        # Fetch Ordinals
        result = ordinals_manager.fetch_address_ordinals(address)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
    
    @app.route('/api/update-selection', methods=['POST'])
    def api_update_selection():
        """API endpoint to update Ordinal selection"""
        data = request.get_json()
        
        if not data or 'selected_ids' not in data:
            return jsonify({'success': False, 'message': 'selected_ids is required'}), 400
        
        selected_ids = data['selected_ids']
        
        if not isinstance(selected_ids, list):
            return jsonify({'success': False, 'message': 'selected_ids must be a list'}), 400
        
        success = ordinals_manager.update_selection(selected_ids)
        
        if success:
            return jsonify({
                'success': True, 
                'message': f'Selection updated: {len(selected_ids)} Ordinals selected'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to update selection'}), 500
    
    @app.route('/api/ordinals')
    def api_get_ordinals():
        """API endpoint to get current Ordinals data"""
        return jsonify({
            'success': True,
            'metadata': ordinals_manager.metadata,
            'selection': ordinals_manager.selection
        })
    
    @app.route('/api/health')
    def api_health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'config': {
                'debug': Config.DEBUG,
                'cache_dir': str(Config.CACHE_DIR),
                'ordinals_count': len(ordinals_manager.metadata.get('ordinals', [])),
                'selected_count': len(ordinals_manager.selection.get('selected_ids', []))
            }
        })
    
    # Content serving
    @app.route('/content/<inscription_id>')
    def serve_inscription_content(inscription_id):
        """Proxy inscription content from API"""
        try:
            content_url = f"{Config.HIRO_API_BASE}/inscriptions/{inscription_id}/content"
            
            response = requests.get(content_url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            # Return the content with appropriate headers
            return response.content, response.status_code, {
                'Content-Type': response.headers.get('Content-Type', 'application/octet-stream'),
                'Cache-Control': 'public, max-age=86400'  # Cache for 24 hours
            }
            
        except Exception as e:
            logger.error(f"Error serving inscription content: {e}")
            return jsonify({'error': 'Content not found'}), 404
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    return app

# Main execution
def main():
    """Main entry point"""
    app = create_app()
    
    logger = logging.getLogger(__name__)
    logger.info("🖼️  Starting Ordinal Frame Server...")
    logger.info(f"📁 Cache Directory: {Config.CACHE_DIR}")
    logger.info(f"🌐 Server URL: http://{Config.HOST}:{Config.PORT}")
    
    try:
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            use_reloader=Config.DEBUG
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()