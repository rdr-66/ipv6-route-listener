"""Packet parsing for Router Advertisements."""

from scapy.all import IPv6, ICMPv6ND_RA, ICMPv6NDOptPrefixInfo, ICMPv6NDOptRouteInfo
from .route_info import RouteInfo

class PacketParser:
    """Handles parsing of Router Advertisement packets."""
    
    def __init__(self, logger=None):
        """Initialize the packet parser.
        
        Args:
            logger: Optional logger instance for debug output
        """
        self.logger = logger

    def parse(self, packet):
        """Parse a Router Advertisement packet.
        
        Args:
            packet: The packet to parse
            
        Returns:
            list[RouteInfo]: List of route information found in the packet
        """
        try:
            # Ensure we have an IPv6 packet
            if not IPv6 in packet:
                if self.logger and self.logger.verbose:
                    self.logger.debug("⏭️  Ignoring non-IPv6 packet")
                return []
                
            # Check if it's a Router Advertisement
            if not ICMPv6ND_RA in packet:
                if self.logger and self.logger.verbose:
                    self.logger.debug("⏭️  Ignoring non-RA packet")
                return []
                
            src_addr = packet[IPv6].src
            
            # Get the Router Advertisement layer
            ra = packet[ICMPv6ND_RA]
            
            # Now we can log the packet details if in debug mode
            if self.logger and self.logger.verbose:
                self.logger.debug(f"🔍 Raw RA data: {ra.show()}")
                self.logger.debug(f"🔍 RA options: {ra.payload}")
            
            # Extract route information from options
            route_infos = []
            
            # Get all options from the RA packet
            options = ra.payload if hasattr(ra, 'payload') else []
            if isinstance(options, list):
                # If options is a list, process each option
                for opt in options:
                    self._process_option(opt, src_addr, route_infos)
            else:
                # If options is a single option or chain, process it
                opt = options
                while opt and not isinstance(opt, bytes):
                    self._process_option(opt, src_addr, route_infos)
                    opt = opt.payload if hasattr(opt, 'payload') else None
            
            return route_infos
                    
        except Exception as e:
            if self.logger and self.logger.verbose:
                self.logger.error(f"Error parsing packet: {str(e)}")
            return []
                
    def _process_option(self, opt, src_addr, route_infos):
        """Process a single RA option."""
        if self.logger and self.logger.verbose:
            self.logger.debug(f"🔍 Processing option: {type(opt).__name__}")
            self.logger.debug(f"🔍 Option data: {opt.show()}")
        
        if isinstance(opt, ICMPv6NDOptPrefixInfo):
            try:
                prefix_str = str(opt.prefix)
                prefix_len = opt.prefixlen
                if self.logger and self.logger.verbose:
                    self.logger.debug(f"🔍 Found on-link prefix: {prefix_str}/{prefix_len}")
                    self.logger.info(f"📡 On-link prefix: {prefix_str}/{prefix_len} (directly connected)")
                route_infos.append(RouteInfo(
                    prefix=prefix_str,
                    prefix_len=prefix_len,
                    router=src_addr,
                    is_prefix=True,
                    valid_time=opt.validlifetime,
                    pref_time=opt.preferredlifetime
                ))
            except AttributeError as e:
                if self.logger and self.logger.verbose:
                    self.logger.error(f"❌ Error processing prefix option: Missing required attribute - {str(e)}")
                    self.logger.debug(f"Option data: {opt}")
        elif isinstance(opt, ICMPv6NDOptRouteInfo):
            try:
                prefix_str = str(opt.prefix)
                prefix_len = opt.plen  # Route Info uses 'plen' instead of 'prefixlen'
                if self.logger and self.logger.verbose:
                    self.logger.debug(f"🔍 Found off-link route: {prefix_str}/{prefix_len}")
                    self.logger.info(f"🛣️  Off-link route: {prefix_str}/{prefix_len} (via {src_addr})")
                route_infos.append(RouteInfo(
                    prefix=prefix_str,
                    prefix_len=prefix_len,
                    router=src_addr,
                    is_prefix=False,
                    lifetime=opt.rtlifetime
                ))
            except AttributeError as e:
                if self.logger and self.logger.verbose:
                    self.logger.error(f"❌ Error processing route option: {str(e)}")
                    self.logger.debug(f"Option data: {opt}")
        else:
            if self.logger and self.logger.verbose:
                self.logger.debug(f"⏭️  Ignoring option type: {type(opt).__name__}") 