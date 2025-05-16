"""Route information handling for IPv6 Router Advertisements."""

from dataclasses import dataclass
from typing import Optional, List

@dataclass
class RouteInfo:
    """Represents route information from a Router Advertisement."""
    prefix: str
    prefix_len: int
    router: str
    is_prefix: bool = False  # True for on-link prefix, False for route
    valid_time: Optional[int] = None
    pref_time: Optional[int] = None
    lifetime: Optional[int] = None

class RouteInfoProcessor:
    """Processes route information from Router Advertisements."""
    
    def __init__(self, route_configurator, logger=None):
        """Initialize the route info processor.
        
        Args:
            route_configurator: The route configurator instance
            logger: Optional logger instance for debug output
        """
        self.route_configurator = route_configurator
        self.logger = logger
        self.initial_check_done = False

    def process_route_info(self, route_info: RouteInfo) -> bool:
        """Process a single route information entry.
        
        Args:
            route_info: The route information to process
            
        Returns:
            bool: True if the route was processed, False if it was ignored
        """
        try:
            # Check if this is a ULA prefix/route
            if not route_info.prefix.startswith("fd"):
                if self.logger and self.logger.verbose:
                    self.logger.ignored_route(
                        route_info.prefix,
                        route_info.prefix_len,
                        "non-ULA prefix" if route_info.is_prefix else "non-ULA route"
                    )
                return False

            # Check if already configured
            if self.route_configurator.is_configured(
                route_info.prefix,
                route_info.prefix_len,
                is_prefix=route_info.is_prefix
            ):
                if not self.initial_check_done and self.logger:
                    self.logger.info(
                        f"✓ ULA {'prefix' if route_info.is_prefix else 'route'} already configured: "
                        f"{route_info.prefix}/{route_info.prefix_len}"
                    )
                elif self.logger and self.logger.verbose:
                    self.logger.debug(
                        f"⏭️  ULA {'prefix' if route_info.is_prefix else 'route'} already configured: "
                        f"{route_info.prefix}/{route_info.prefix_len}"
                    )
                return False

            # Configure the route
            self.route_configurator.configure(
                route_info.prefix,
                route_info.prefix_len,
                route_info.router,
                is_prefix=route_info.is_prefix
            )
            return True

        except Exception as e:
            if self.logger and self.logger.verbose:
                self.logger.error(f"Error processing route info: {str(e)}")
            return False

    def process_route_infos(self, route_infos: List[RouteInfo]) -> bool:
        """Process multiple route information entries.
        
        Args:
            route_infos: List of route information entries to process
            
        Returns:
            bool: True if any routes were processed, False if all were ignored
        """
        processed_any = False
        for route_info in route_infos:
            if self.process_route_info(route_info):
                processed_any = True
        
        # Mark initial check as done after first batch
        self.initial_check_done = True
        return processed_any 