1. Introduction :

*a video link is at the of this report including slides and running the project demo 
In this project, I aimed to replicate and expand upon a previously implemented cache simulation 
system that was originally written in ARMv7-M assembly for the Cortex-M3 platform. The 
primary purpose of this exercise was to simulate a 2-way set-associative cache using FIFO 
replacement and to process a fixed trace of memory addresses. However, due to limitations in 
the semihosting output functionality of Keil MDK Community Edition, I decided to reimplement 
the entire simulator in Python to facilitate better visualization, customization, and verification 
capabilities. This shift allowed me to preserve the core architectural behavior while leveraging 
Python’s higher-level abstractions for rapid feature development, including statistics tracking, 
replacement policy comparison, and cache visualization. 

2. Design/Implementation :

The design and implementation began with defining a basic structure in Python that could 
emulate a 2-way set-associative cache. Key parameters such as cache size (1024 bytes), block 
size (16 bytes), and associativity (2) were configured as constants. This setup determined that 
there would be 64 total blocks and 32 cache sets. A CacheLine class was created to hold each 
line’s state, including its validity and tag, and a two-dimensional list 
cache_array[NUM_SETS][ASSOCIATIVITY] was used to represent the full cache. 
The cache simulator was then wrapped in a modular Python class, CacheSimulator, which 
managed initialization, access logic, and statistics. FIFO replacement was implemented by 
tracking indices in a fifo_idx array, while support for LRU was added later by maintaining and 
updating a last_used timestamp for each line in the set. 
To mimic the original behavior, I started with a hardcoded memory trace that included addresses 
like 0x0000A3C4, 0x0000A3D0, and so on. These were processed to compute set indices and 
tags, check for hits, and update the cache appropriately. A formatted print output displayed each 
result as “Addr 0xXXXXXXXX -> HIT/MISS.” 
Once the baseline functionality was in place, I expanded the design with several enhancements 
to provide deeper insights into cache behavior. These included: 
● Command-line Configuration: Using argparse, the program could be run with custom 
cache parameters (e.g., block size, associativity) and replacement policies (FIFO or 
LRU). 
● Trace File Support: In addition to the hardcoded trace, external trace files could be 
loaded, parsed, and validated with support for comments and malformed input handling. 
● Logging and State Visualization: For each memory access, the simulator printed 
detailed logs showing the tag comparison, set contents, and which way was updated or 
evicted. 
● Statistics and Plotting: A CacheStats class tracked total accesses, hits, misses, 
evictions, and the hit rate over time. The hit rate trend was plotted using Matplotlib and 
saved as an image. 
● Error Handling: Robust input validation and exception handling ensured that incorrect 
configurations or trace errors resulted in clear messages rather than crashes. 
The result was a Python script, complete with comments and logging, that closely mimicked the 
structure and functionality of hardware cache behavior. 

3. Verification :

Verification of the simulator was carried out through a combination of test traces, configuration 
scenarios, and internal state monitoring. I began by running the simulator with the default 
hardcoded trace. As expected, the first two accesses were misses due to an initially empty 
cache. Subsequent repeated accesses to those addresses resulted in hits, demonstrating 
correct retention and indexing behavior. 
To verify the replacement logic, I carefully traced accesses that would trigger a replacement. In 
FIFO mode, I observed the fifo_idx toggling between 0 and 1 in each set, and for LRU 
mode, I monitored the last_used timestamps, confirming that the least recently used block 
was correctly evicted. 
I ran the simulator with --policy LRU and compared results against FIFO. The replacement 
behavior differed, as expected, confirming that the simulator responded correctly to policy 
changes. I also tested invalid configurations like non-divisible cache sizes or zero associativity 
to ensure error messages were raised. 
For visualization, I examined the hit_rate_plot.png file generated during execution. The 
plotted graph correctly tracked hit rate trends, showing a gradual increase with repeated 
accesses to cached values. 
All printed logs, internal data structures, and statistics summaries were examined and confirmed 
to be accurate through step-by-step debugging in Visual Studio Code. I placed breakpoints in 
the access_cache method and inspected the cache state after each operation to confirm 
correctness. 

4. Conclusions :

This project successfully demonstrated the ability to reimplement a hardware-inspired system in 
software, simulating a set-associative cache with both FIFO and LRU replacement strategies. 
The project began as a direct translation from ARMv7-M assembly but was expanded with 
powerful new features such as trace file input, configuration flexibility, visual performance 
analysis, and detailed logging. Through comprehensive testing, all core and advanced 
functionalities were verified to behave correctly. 
In the process, I gained deeper insight into how caching mechanisms work, especially in regard 
to set indexing, replacement logic, and the impact of cache parameters on performance. The 
simulator serves both as an educational tool and as a diagnostic platform for analyzing memory 
access patterns. If extended further, the simulator could incorporate more advanced features 
such as write-back/write-through behavior or multilevel caches. 

5. Appendix :
![image](https://github.com/user-attachments/assets/86694a17-f025-4b16-a0df-853031678f44)


Link to video demo on YouTube:  
https://www.youtube.com/watch?v=LHTJewuwCYQ 

 
 
 
