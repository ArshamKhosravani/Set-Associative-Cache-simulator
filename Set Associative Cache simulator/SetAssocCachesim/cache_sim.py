#!/usr/bin/env python3

"""
Enhanced SetAssocCachesim: A Python implementation of a set-associative cache simulator
with configurable parameters, multiple replacement policies, statistics, logging, and visualization.
"""

import argparse
import datetime
import sys
import matplotlib.pyplot as plt
from typing import List, Dict

# Default Cache Configuration
DEFAULT_CACHE_SIZE = 1024    # Total cache size in bytes
DEFAULT_BLOCK_SIZE = 16      # Size of each cache block in bytes
DEFAULT_ASSOCIATIVITY = 2    # Default associativity

# Cache Line Structure
class CacheLine:
    def __init__(self):
        self.valid = False       # Valid bit (True/False)
        self.tag = 0             # Tag value for address matching
        self.last_used = 0       # For LRU: tracks last access time

# Cache Statistics Tracker
class CacheStats:
    def __init__(self):
        self.total_accesses = 0
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.hit_rate_history = []  # For plotting

    def record_access(self, is_hit: bool):
        """Records an access and updates statistics."""
        self.total_accesses += 1
        if is_hit:
            self.hits += 1
        else:
            self.misses += 1
        # Update hit rate history for visualization
        hit_rate = (self.hits / self.total_accesses) * 100 if self.total_accesses > 0 else 0
        self.hit_rate_history.append(hit_rate)

    def record_eviction(self):
        """Records an eviction event."""
        self.evictions += 1

    def print_summary(self):
        """Prints a summary of cache statistics."""
        print("\nCache Statistics Summary:")
        print(f"Total Accesses: {self.total_accesses}")
        print(f"Hits: {self.hits}")
        print(f"Misses: {self.misses}")
        print(f"Evictions: {self.evictions}")
        hit_rate = (self.hits / self.total_accesses) * 100 if self.total_accesses > 0 else 0
        miss_rate = (self.misses / self.total_accesses) * 100 if self.total_accesses > 0 else 0
        print(f"Hit Rate: {hit_rate:.2f}%")
        print(f"Miss Rate: {miss_rate:.2f}%")

    def plot_hit_rate(self):
        """Plots the hit rate over time and saves to a file."""
        plt.figure(figsize=(10, 6))
        plt.plot(self.hit_rate_history, label='Hit Rate (%)')
        plt.title('Cache Hit Rate Over Time')
        plt.xlabel('Access Number')
        plt.ylabel('Hit Rate (%)')
        plt.grid(True)
        plt.legend()
        plt.savefig('hit_rate_plot.png')
        print("\nHit rate plot saved as 'hit_rate_plot.png'")

# Cache Simulator Class
class CacheSimulator:
    def __init__(self, cache_size: int, block_size: int, associativity: int, replacement_policy: str):
        """Initializes the cache with given parameters."""
        self.cache_size = cache_size
        self.block_size = block_size
        self.associativity = associativity
        self.replacement_policy = replacement_policy.upper()
        self.num_blocks = cache_size // block_size
        self.num_sets = self.num_blocks // associativity
        self.access_counter = 0  # For LRU tracking

        # Validate configuration
        if self.cache_size <= 0 or self.block_size <= 0 or self.associativity <= 0:
            raise ValueError("Cache size, block size, and associativity must be positive integers.")
        if self.num_blocks * self.block_size != self.cache_size:
            raise ValueError("Cache size must be divisible by block size.")
        if self.num_sets * self.associativity != self.num_blocks:
            raise ValueError("Number of blocks must be divisible by associativity.")
        if self.replacement_policy not in ['FIFO', 'LRU']:
            raise ValueError("Replacement policy must be 'FIFO' or 'LRU'.")

        # Initialize cache and FIFO/LRU indices
        self.cache_array = [[CacheLine() for _ in range(self.associativity)] for _ in range(self.num_sets)]
        self.fifo_idx = [0] * self.num_sets  # For FIFO
        self.stats = CacheStats()

    def init_cache(self):
        """Initializes the cache by resetting all lines and indices."""
        for set_idx in range(self.num_sets):
            for way in range(self.associativity):
                self.cache_array[set_idx][way].valid = False
                self.cache_array[set_idx][way].tag = 0
                self.cache_array[set_idx][way].last_used = 0
            self.fifo_idx[set_idx] = 0
        print(f"Cache initialized with {self.num_sets} sets, {self.associativity}-way associativity, "
              f"using {self.replacement_policy} replacement policy.")

    def access_cache(self, address: int) -> bool:
        """Accesses the cache and returns True for hit, False for miss."""
        self.access_counter += 1
        set_index = (address >> 4) & (self.num_sets - 1)  # Block offset: 4 bits
        tag_value = address >> (4 + (self.num_sets.bit_length() - 1))  # Tag bits

        # Check for hit
        current_set = self.cache_array[set_index]
        for way in range(self.associativity):
            if current_set[way].valid and current_set[way].tag == tag_value:
                current_set[way].last_used = self.access_counter
                self.stats.record_access(True)
                print(f"[{self._get_timestamp()}] Hit for address 0x{address:08x} in set {set_index}, way {way}")
                self._print_set_state(set_index)
                return True

        # Miss: Find a way to replace
        if self.replacement_policy == 'FIFO':
            replace_idx = self.fifo_idx[set_index]
            self.fifo_idx[set_index] = (self.fifo_idx[set_index] + 1) % self.associativity
        else:  # LRU
            replace_idx = min(range(self.associativity), key=lambda w: current_set[w].last_used)

        # Evict if the selected way is valid
        if current_set[replace_idx].valid:
            self.stats.record_eviction()
            print(f"[{self._get_timestamp()}] Evicting way {replace_idx} in set {set_index}")

        # Replace the cache line
        current_set[replace_idx].valid = True
        current_set[replace_idx].tag = tag_value
        current_set[replace_idx].last_used = self.access_counter
        self.stats.record_access(False)
        print(f"[{self._get_timestamp()}] Miss for address 0x{address:08x} in set {set_index}, "
              f"placed in way {replace_idx}")
        self._print_set_state(set_index)
        return False

    def _print_set_state(self, set_index: int):
        """Prints the current state of the specified set."""
        print(f"Set {set_index} state:")
        for way in range(self.associativity):
            line = self.cache_array[set_index][way]
            print(f"  Way {way}: Valid={line.valid}, Tag=0x{line.tag:08x}, "
                  f"Last Used={line.last_used}")

    def _get_timestamp(self) -> str:
        """Returns the current timestamp as a string."""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Function to read trace from a file
def read_trace_file(filename: str) -> List[int]:
    """
    Reads memory addresses from a file, one per line, in hex format.
    
    Args:
        filename (str): Path to the trace file.
    
    Returns:
        List[int]: List of addresses.
    """
    trace = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue  # Skip empty lines and comments
                try:
                    address = int(line, 16)
                    if address < 0 or address > 0xFFFFFFFF:
                        raise ValueError(f"Address out of 32-bit range: {line}")
                    trace.append(address)
                except ValueError as e:
                    print(f"Error parsing address '{line}': {e}")
                    sys.exit(1)
    except FileNotFoundError:
        print(f"Trace file '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading trace file: {e}")
        sys.exit(1)
    return trace

# Main function
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Set-Associative Cache Simulator")
    parser.add_argument('--cache-size', type=int, default=DEFAULT_CACHE_SIZE,
                        help=f"Cache size in bytes (default: {DEFAULT_CACHE_SIZE})")
    parser.add_argument('--block-size', type=int, default=DEFAULT_BLOCK_SIZE,
                        help=f"Block size in bytes (default: {DEFAULT_BLOCK_SIZE})")
    parser.add_argument('--associativity', type=int, default=DEFAULT_ASSOCIATIVITY,
                        help=f"Associativity (default: {DEFAULT_ASSOCIATIVITY})")
    parser.add_argument('--policy', type=str, choices=['FIFO', 'LRU'], default='FIFO',
                        help="Replacement policy: FIFO or LRU (default: FIFO)")
    parser.add_argument('--trace-file', type=str,
                        help="Path to trace file (if not provided, uses default trace)")
    args = parser.parse_args()

    # Initialize cache simulator
    try:
        simulator = CacheSimulator(args.cache_size, args.block_size, args.associativity, args.policy)
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    # Load trace
    if args.trace_file:
        trace = read_trace_file(args.trace_file)
    else:
        trace = [
            0x0000A3C4, 0x0000A3D0, 0x0000A3C4, 0x0000A3D0,
            0x0000B3C4, 0x0000C3C4, 0x0000A3C4, 0x0000D3C4
        ]

    print(f"Starting SetAssocCachesim simulation...")
    print(f"Processing {len(trace)} memory addresses.")

    # Initialize cache
    simulator.init_cache()

    # Process each address
    for address in trace:
        print(f"\nAddr 0x{address:08x} -> ", end='')
        if simulator.access_cache(address):
            print("HIT")
        else:
            print("MISS")

    # Print statistics and plot hit rate
    simulator.stats.print_summary()
    simulator.stats.plot_hit_rate()

if __name__ == "__main__":
    main()