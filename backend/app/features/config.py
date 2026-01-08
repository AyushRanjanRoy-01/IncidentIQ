"""Feature configuration management.

Manages feature-specific configuration and settings.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from app.features.flags import FeatureFlagClient, get_feature_flag_client


@dataclass
class FeatureConfig:
    """Configuration for a specific feature."""
    name: str
    enabled: bool = False
    rollout_percentage: int = 0  # 0-100
    config: Dict[str, Any] = field(default_factory=dict)
    target_users: list[str] = field(default_factory=list)
    target_environments: list[str] = field(default_factory=list)


class FeatureConfigManager:
    """Manages feature configurations.
    
    Provides centralized management of feature configurations,
    integrating with feature flags for gradual rollouts.
    """
    
    def __init__(self) -> None:
        """Initialize feature config manager."""
        self.configs: Dict[str, FeatureConfig] = {}
        self.flag_client = get_feature_flag_client()
    
    def register_feature(
        self,
        name: str,
        enabled: bool = False,
        rollout_percentage: int = 0,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a new feature configuration.
        
        Args:
            name: Feature name
            enabled: Whether feature is enabled
            rollout_percentage: Percentage of users to enable for (0-100)
            config: Feature-specific configuration
        """
        self.configs[name] = FeatureConfig(
            name=name,
            enabled=enabled,
            rollout_percentage=rollout_percentage,
            config=config or {},
        )
    
    def get_feature_config(
        self,
        name: str,
        user_id: Optional[str] = None,
    ) -> Optional[FeatureConfig]:
        """Get feature configuration.
        
        Args:
            name: Feature name
            user_id: Optional user identifier for targeting
            
        Returns:
            Feature configuration or None if not found
        """
        if name not in self.configs:
            return None
        
        config = self.configs[name]
        
        # Check feature flag
        flag_enabled = self.flag_client.is_enabled(
            f"feature_{name}",
            user_id,
            default=config.enabled,
        )
        
        if not flag_enabled:
            return None
        
        return config
    
    def is_feature_enabled(
        self,
        name: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """Check if feature is enabled for user.
        
        Args:
            name: Feature name
            user_id: Optional user identifier
            
        Returns:
            True if feature is enabled
        """
        config = self.get_feature_config(name, user_id)
        return config is not None and config.enabled
    
    def get_feature_value(
        self,
        name: str,
        key: str,
        default: Any = None,
        user_id: Optional[str] = None,
    ) -> Any:
        """Get feature configuration value.
        
        Args:
            name: Feature name
            key: Configuration key
            default: Default value if not found
            user_id: Optional user identifier
            
        Returns:
            Configuration value or default
        """
        config = self.get_feature_config(name, user_id)
        if config:
            return config.config.get(key, default)
        return default


# Global feature config manager
_feature_config_manager: Optional[FeatureConfigManager] = None


def get_feature_config_manager() -> FeatureConfigManager:
    """Get global feature config manager instance.
    
    Returns:
        Feature config manager instance
    """
    global _feature_config_manager
    if _feature_config_manager is None:
        _feature_config_manager = FeatureConfigManager()
    return _feature_config_manager

