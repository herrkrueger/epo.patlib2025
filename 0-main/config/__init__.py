"""
Configuration Management Module for Patent Analysis Platform
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides centralized configuration management for the patent analysis platform
with support for YAML configurations, environment variables, and runtime overrides.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging
from copy import deepcopy

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from the patlib/.env file."""
    try:
        # Look for .env file in patlib directory
        env_file_paths = [
            '/home/jovyan/patlib/.env',  # Full path
            '../../../.env',             # Relative to config
            '../../../../.env'           # Alternative relative path
        ]
        
        for env_file in env_file_paths:
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key] = value
                logger.debug(f"✅ Loaded environment variables from {env_file}")
                return True
        
        logger.warning("⚠️ No .env file found in expected locations")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to load .env file: {e}")
        return False

# Load environment variables on module import
load_env_file()

class ConfigurationManager:
    """
    Centralized configuration manager for the patent analysis platform.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize configuration manager with .env loading.
        
        Args:
            config_dir: Directory containing configuration files
        """
        if config_dir is None:
            config_dir = Path(__file__).parent
        
        self.config_dir = Path(config_dir)
        self.configs = {}
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
        # Load all configuration files
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all YAML configuration files from the config directory."""
        config_files = {
            'api': 'api_config.yaml',
            'database': 'database_config.yaml', 
            'visualization': 'visualization_config.yaml',
            'search_patterns': 'search_patterns_config.yaml'
        }
        
        for config_name, filename in config_files.items():
            config_path = self.config_dir / filename
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                    
                    # Process environment variable substitutions
                    config_data = self._process_env_substitutions(config_data)
                    
                    self.configs[config_name] = config_data
                    logger.debug(f"✅ Loaded {config_name} configuration from {filename}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to load {config_name} configuration: {e}")
                    self.configs[config_name] = {}
            else:
                logger.warning(f"⚠️ Configuration file not found: {filename}")
                self.configs[config_name] = {}
    
    def _process_env_substitutions(self, data: Any) -> Any:
        """
        Process environment variable substitutions in configuration data.
        
        Args:
            data: Configuration data that may contain ${ENV:VAR_NAME} patterns
            
        Returns:
            Processed data with environment variables substituted
        """
        if isinstance(data, dict):
            return {key: self._process_env_substitutions(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._process_env_substitutions(item) for item in data]
        elif isinstance(data, str) and data.startswith('${ENV:') and data.endswith('}'):
            # Extract environment variable name
            env_var = data[6:-1]  # Remove ${ENV: and }
            default_value = None
            
            # Handle default values: ${ENV:VAR_NAME:default_value}
            if ':' in env_var:
                env_var, default_value = env_var.split(':', 1)
            
            return os.getenv(env_var, default_value)
        else:
            return data
    
    def get(self, config_type: str, key_path: str = None, default: Any = None) -> Any:
        """
        Get configuration value by type and optional key path.
        
        Args:
            config_type: Type of configuration ('api', 'database', 'visualization')
            key_path: Dot-separated path to specific configuration (e.g., 'epo_ops.rate_limiting.requests_per_minute')
            default: Default value if configuration not found
            
        Returns:
            Configuration value
        """
        if config_type not in self.configs:
            logger.warning(f"⚠️ Configuration type '{config_type}' not found")
            return default
        
        config_data = self.configs[config_type]
        
        if key_path is None:
            return config_data
        
        # Navigate through nested dictionary using dot notation
        keys = key_path.split('.')
        current_data = config_data
        
        try:
            for key in keys:
                current_data = current_data[key]
            return current_data
        except (KeyError, TypeError):
            logger.debug(f"📋 Configuration key '{key_path}' not found in '{config_type}'")
            return default
    
    def get_api_config(self, key_path: str = None, default: Any = None) -> Any:
        """Get API configuration."""
        return self.get('api', key_path, default)
    
    def get_database_config(self, key_path: str = None, default: Any = None) -> Any:
        """Get database configuration."""
        return self.get('database', key_path, default)
    
    def get_visualization_config(self, key_path: str = None, default: Any = None) -> Any:
        """Get visualization configuration."""
        return self.get('visualization', key_path, default)
    
    def get_search_patterns_config(self, key_path: str = None, default: Any = None) -> Any:
        """Get search patterns configuration."""
        return self.get('search_patterns', key_path, default)
    
    def update_config(self, config_type: str, key_path: str, value: Any):
        """
        Update configuration value at runtime.
        
        Args:
            config_type: Type of configuration
            key_path: Dot-separated path to configuration key
            value: New value
        """
        if config_type not in self.configs:
            logger.warning(f"⚠️ Configuration type '{config_type}' not found")
            return
        
        keys = key_path.split('.')
        current_data = self.configs[config_type]
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in current_data:
                current_data[key] = {}
            current_data = current_data[key]
        
        # Set the value
        current_data[keys[-1]] = value
        logger.debug(f"📝 Updated {config_type}.{key_path} = {value}")
    
    def get_environment_specific_config(self, config_type: str, key_path: str = None, default: Any = None) -> Any:
        """
        Get environment-specific configuration with fallback to general config.
        
        Args:
            config_type: Type of configuration
            key_path: Configuration key path
            default: Default value
            
        Returns:
            Environment-specific configuration value
        """
        # Try environment-specific configuration first
        env_key_path = f"environments.{self.environment}.{key_path}" if key_path else f"environments.{self.environment}"
        env_config = self.get(config_type, env_key_path)
        
        if env_config is not None:
            return env_config
        
        # Fallback to general configuration
        return self.get(config_type, key_path, default)
    
    def validate_configuration(self) -> Dict[str, bool]:
        """
        Validate configuration completeness and correctness.
        
        Returns:
            Dictionary with validation results for each configuration type
        """
        validation_results = {}
        
        # API Configuration Validation
        api_valid = True
        try:
            # Check EPO OPS credentials
            ops_key = self.get_api_config('epo_ops.authentication.consumer_key')
            ops_secret = self.get_api_config('epo_ops.authentication.consumer_secret')
            
            if not ops_key or ops_key.startswith('${ENV:'):
                logger.warning("⚠️ EPO OPS consumer key not configured or environment variable not set")
                api_valid = False
            
            if not ops_secret or ops_secret.startswith('${ENV:'):
                logger.warning("⚠️ EPO OPS consumer secret not configured or environment variable not set")
                api_valid = False
            
            # Check rate limiting configuration
            rate_limit = self.get_api_config('epo_ops.rate_limiting.requests_per_minute')
            if not isinstance(rate_limit, int) or rate_limit <= 0:
                logger.warning("⚠️ Invalid rate limiting configuration")
                api_valid = False
                
        except Exception as e:
            logger.error(f"❌ API configuration validation failed: {e}")
            api_valid = False
        
        validation_results['api'] = api_valid
        
        # Database Configuration Validation
        db_valid = True
        try:
            # Check PATSTAT configuration
            patstat_env = self.get_database_config('patstat.connection.environment')
            if patstat_env not in ['PROD', 'TEST']:
                logger.warning("⚠️ Invalid PATSTAT environment configuration")
                db_valid = False
            
            # Check required table configurations
            required_tables = ['applications', 'titles', 'abstracts', 'ipc_classifications']
            for table in required_tables:
                table_config = self.get_database_config(f'patstat.tables.{table}')
                if not table_config:
                    logger.warning(f"⚠️ Missing table configuration for {table}")
                    db_valid = False
                    
        except Exception as e:
            logger.error(f"❌ Database configuration validation failed: {e}")
            db_valid = False
        
        validation_results['database'] = db_valid
        
        # Visualization Configuration Validation
        viz_valid = True
        try:
            # Check theme configuration
            default_theme = self.get_visualization_config('general.themes.default_theme')
            available_themes = self.get_visualization_config('general.themes.available_themes', [])
            
            if default_theme not in available_themes:
                logger.warning("⚠️ Default theme not in available themes list")
                viz_valid = False
            
            # Check color scheme completeness
            required_schemes = ['patent_analysis', 'qualitative_professional']
            for scheme in required_schemes:
                colors = self.get_visualization_config(f'charts.color_schemes.{scheme}')
                if not colors or len(colors) < 5:
                    logger.warning(f"⚠️ Insufficient colors in {scheme} color scheme")
                    viz_valid = False
                    
        except Exception as e:
            logger.error(f"❌ Visualization configuration validation failed: {e}")
            viz_valid = False
        
        validation_results['visualization'] = viz_valid
        
        # Overall validation status
        overall_valid = all(validation_results.values())
        validation_results['overall'] = overall_valid
        
        if overall_valid:
            logger.debug("✅ All configurations validated successfully")
        else:
            logger.warning("⚠️ Some configuration validation issues found")
        
        return validation_results
    
    def export_effective_config(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export the effective configuration (after environment variable substitution).
        
        Args:
            output_path: Optional path to save configuration as YAML
            
        Returns:
            Complete effective configuration
        """
        effective_config = deepcopy(self.configs)
        effective_config['_metadata'] = {
            'environment': self.environment,
            'config_dir': str(self.config_dir),
            'generated_at': str(pd.Timestamp.now()),
            'validation_status': self.validate_configuration()
        }
        
        if output_path:
            try:
                with open(output_path, 'w') as f:
                    yaml.dump(effective_config, f, default_flow_style=False, indent=2)
                logger.debug(f"💾 Effective configuration exported to {output_path}")
            except Exception as e:
                logger.error(f"❌ Failed to export configuration: {e}")
        
        return effective_config
    
    def reload_configurations(self):
        """Reload all configuration files from disk."""
        logger.debug("🔄 Reloading configurations...")
        self.configs.clear()
        self._load_all_configs()
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of loaded configurations."""
        summary = {
            'environment': self.environment,
            'config_directory': str(self.config_dir),
            'loaded_configs': list(self.configs.keys()),
            'validation_status': self.validate_configuration()
        }
        
        # Add configuration sizes
        for config_type, config_data in self.configs.items():
            summary[f'{config_type}_keys'] = len(config_data) if isinstance(config_data, dict) else 0
        
        return summary

# Global configuration manager instance
_config_manager = None

def get_config_manager(config_dir: Optional[str] = None) -> ConfigurationManager:
    """
    Get or create the global configuration manager instance.
    
    Args:
        config_dir: Directory containing configuration files
        
    Returns:
        ConfigurationManager instance
    """
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigurationManager(config_dir)
    
    return _config_manager

# Convenience functions
def get_api_config(key_path: str = None, default: Any = None) -> Any:
    """Get API configuration value."""
    return get_config_manager().get_api_config(key_path, default)

def get_database_config(key_path: str = None, default: Any = None) -> Any:
    """Get database configuration value."""
    return get_config_manager().get_database_config(key_path, default)

def get_visualization_config(key_path: str = None, default: Any = None) -> Any:
    """Get visualization configuration value."""
    return get_config_manager().get_visualization_config(key_path, default)

def get_search_patterns_config(key_path: str = None, default: Any = None) -> Any:
    """Get search patterns configuration value."""
    return get_config_manager().get_search_patterns_config(key_path, default)

def validate_all_configurations() -> Dict[str, bool]:
    """Validate all configurations."""
    return get_config_manager().validate_configuration()

# Patent search configuration helpers
def get_patent_search_config() -> Dict[str, Any]:
    """Get patent search configuration (updated structure to match YAML)."""
    return {
        'keywords': get_search_patterns_config('keywords', {}),
        'cpc_classifications': {'technology_areas': get_search_patterns_config('cpc_classifications.technology_areas', {})},
        'date_ranges': get_search_patterns_config('global_settings.date_ranges', {}),
        'search_strategies': get_search_patterns_config('search_strategies', {}),
        'quality_thresholds': get_search_patterns_config('global_settings.quality_thresholds', {}),
        'demo_parameters': {'max_results': get_search_patterns_config('global_settings.max_results.default', 1000)},
        'technology_taxonomy': get_search_patterns_config('cpc_classifications.technology_areas', {}),
        'classification_descriptions': _build_classification_descriptions(),
        'search_patterns': get_search_patterns_config('search_patterns', {}),
        'market_events': get_search_patterns_config('market_data_integration.market_events', {}),
        'market_data_integration': get_search_patterns_config('market_data_integration', {}),
        'epo_ops_patterns': get_search_patterns_config('search_patterns.epo_ops_patterns', {})
    }

def _build_classification_descriptions() -> Dict[str, str]:
    """Build classification descriptions from CPC technology areas."""
    descriptions = {}
    tech_areas = get_search_patterns_config('cpc_classifications.technology_areas', {})
    
    for area_name, area_config in tech_areas.items():
        codes = area_config.get('codes', [])
        description = area_config.get('description', f'{area_name.replace("_", " ").title()} technology')
        
        for code in codes:
            descriptions[code] = description
    
    return descriptions

def get_epo_ops_credentials() -> Dict[str, str]:
    """Get EPO OPS API credentials."""
    return {
        'consumer_key': get_api_config('epo_ops.authentication.consumer_key'),
        'consumer_secret': get_api_config('epo_ops.authentication.consumer_secret')
    }

def get_patstat_connection_config() -> Dict[str, Any]:
    """Get PATSTAT connection configuration."""
    return {
        'environment': get_database_config('patstat.connection.environment', 'PROD'),
        'timeout': get_database_config('patstat.connection.timeout', 300),
        'project_id': get_database_config('patstat.connection.project_id'),
        'dataset_id': get_database_config('patstat.connection.dataset_id')
    }

def get_visualization_theme_config(theme_name: str = None) -> Dict[str, Any]:
    """Get visualization theme configuration."""
    if theme_name is None:
        theme_name = get_visualization_config('general.themes.default_theme', 'patent_intelligence')
    
    return {
        'theme_name': theme_name,
        'color_schemes': get_visualization_config('charts.color_schemes', {}),
        'layout': get_visualization_config('charts.layout', {}),
        'export': get_visualization_config('export', {})
    }

def get_technology_taxonomy() -> Dict[str, Any]:
    """Get technology taxonomy configuration."""
    return get_search_patterns_config('ree_technology.technology_taxonomy', {})

def get_classification_descriptions() -> Dict[str, str]:
    """Get classification code descriptions."""
    return get_search_patterns_config('ree_technology.classification_descriptions', {})


def get_search_strategy_config(strategy_name: str = 'focused_high_precision') -> Dict[str, Any]:
    """Get specific search strategy configuration."""
    return get_search_patterns_config(f'search_strategies.{strategy_name}', {})

def get_market_data_integration_config() -> Dict[str, Any]:
    """Get market data integration configuration."""
    return get_search_patterns_config('market_data_integration', {})

def get_epo_ops_query_templates() -> Dict[str, Any]:
    """Get EPO OPS query templates."""
    return get_search_patterns_config('search_patterns.epo_ops_patterns', {})

def run_configuration_tests() -> bool:
    """Run comprehensive configuration tests."""
    try:
        from .test_config import main
        return main() == 0
    except ImportError:
        print("❌ Test configuration module not found")
        return False

# For backwards compatibility and imports
import pandas as pd

__all__ = [
    'ConfigurationManager',
    'get_config_manager',
    'get_api_config',
    'get_database_config', 
    'get_visualization_config',
    'get_search_patterns_config',
    'validate_all_configurations',
    # Patent search functions
    'get_patent_search_config',
    'get_technology_taxonomy',
    'get_classification_descriptions',
    'get_search_strategy_config',
    'get_market_data_integration_config',
    'get_epo_ops_query_templates',
    # Platform functions
    'get_epo_ops_credentials',
    'get_patstat_connection_config',
    'get_visualization_theme_config',
    'run_configuration_tests'
]