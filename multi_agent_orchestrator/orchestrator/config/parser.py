"""YAML configuration parser."""

from pathlib import Path
from typing import Union

import yaml
from pydantic import ValidationError

from .schema import OrchestratorConfig


class ConfigError(Exception):
    """Configuration parsing or validation error."""
    pass


def parse_config(config_path: Union[str, Path]) -> OrchestratorConfig:
    """
    Parse and validate a YAML configuration file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Validated OrchestratorConfig object
        
    Raises:
        ConfigError: If the file cannot be read or validation fails
    """
    path = Path(config_path)
    
    if not path.exists():
        raise ConfigError(f"Configuration file not found: {path}")
    
    if not path.suffix in {".yaml", ".yml"}:
        raise ConfigError(f"Expected YAML file, got: {path.suffix}")
    
    try:
        with open(path, "r") as f:
            raw_config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML syntax: {e}")
    
    if raw_config is None:
        raise ConfigError("Empty configuration file")
    
    return validate_config(raw_config)


def validate_config(raw_config: dict) -> OrchestratorConfig:
    """
    Validate a raw configuration dictionary.
    
    Args:
        raw_config: Dictionary from parsed YAML
        
    Returns:
        Validated OrchestratorConfig object
        
    Raises:
        ConfigError: If validation fails
    """
    try:
        return OrchestratorConfig.model_validate(raw_config)
    except ValidationError as e:
        errors = []
        for error in e.errors():
            loc = " -> ".join(str(l) for l in error["loc"])
            msg = error["msg"]
            errors.append(f"  {loc}: {msg}")
        raise ConfigError("Configuration validation failed:\n" + "\n".join(errors))
