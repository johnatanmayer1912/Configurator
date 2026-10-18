---
name: profiling-performance
description: Profile Python application performance using cProfile, profiling tools, and analysis. Identifies slow functions, memory hotspots, and suggests optimizations. Use when the platform feels slow or when performance investigation is needed.
---

# Python Performance Profiling (Adapted for NLAP)

Use this skill when the Network Log Analysis Platform feels slow, unresponsive, or when performance investigation is needed for Python code.

## Tools Available

- **cProfile**: Built-in Python profiler
- **py-spy**: Statistical profiler with low overhead
- **memory_profiler**: Memory profiling
- **line_profiler**: Line-by-line profiling
- **snakeviz**: Visualization of profiling data

## Steps

1. **Choose the right profiling tool** based on the issue:

   - CPU performance: `cProfile` or `py-spy`
   - Memory leaks: `memory_profiler`
   - Specific function: `line_profiler`
   - Visualization: `snakeviz`

2. **Install profiling tools if not available**:

   ```bash
   pip install py-spy memory-profiler line_profiler snakeviz
   ```

3. **Profile CPU performance with cProfile**:

   ```bash
   python -m cProfile -o profile.stats your_script.py
   ```

   Then analyze the results:
   ```python
   import pstats
   p = pstats.Stats('profile.stats')
   p.sort_stats('cumulative').print_stats(20)
   ```

4. **Profile with py-spy** (lower overhead, real-time):

   ```bash
   py-spy --stat your_script.py
   ```

   For specific function profiling:
   ```bash
   py-spy --stat your_script.py -k function_name
   ```

5. **Profile memory usage**:

   ```bash
   python -m memory_profiler your_script.py
   ```

   For line-by-line memory profiling:
   ```bash
   python -m memory_profiler --line-by-line your_script.py
   ```

6. **Profile specific functions** with line_profiler:

   ```python
   from line_profiler import profile
   from modules.analysis.network_incident_story import IncidentStoryGenerator

   @profile
   def generate_story_function(logs):
       generator = IncidentStoryGenerator()
       return generator.generate_story(logs)
   ```

7. **Analyze the profiling results**:

   Key metrics to examine:
   - **ncalls**: Number of function calls
   - **tottime**: Total time spent in function (excluding subcalls)
   - **cumtime**: Cumulative time (including subcalls)
   - **percall**: Average time per call

   Look for:
   - Functions with high cumulative time
   - Functions called unusually frequently
   - Unexpected call patterns
   - Functions that could benefit from memoization

8. **Identify performance bottlenecks**:

   Common Python performance issues:
   - **Excessive string concatenation** in loops
   - **Database queries in loops** (N+1 problem)
   - **Unnecessary regex compilation** (compile once)
   - **I/O operations** without caching
   - **Large data structures** in memory
   - **Blocking operations** in critical paths

9. **Suggest and implement optimizations**:

   Common optimizations for NLAP:
   - Cache regex patterns: `PATTERN = re.compile(r'pattern')`
   - Use list comprehensions instead of map/filter with lambda
   - Optimize database queries: batch operations
   - Implement memoization for expensive computations
   - Use generators instead of lists for large datasets
   - Optimize log file reading: read in chunks
   - Implement connection pooling for network connections

10. **Verify improvements**:

    Profile again after optimization and compare:
    ```bash
    python -m cProfile -o profile_optimized.stats your_script.py
    python -c "import pstats; p = pstats.Stats('profile.stats'); p2 = pstats.Stats('profile_optimized.stats'); print(f'Before: {p.total_tt:.2f}s, After: {p2.total_tt:.2f}s, Improvement: {(p.total_tt - p2.total_tt)/p.total_tt*100:.1f}%')"
    ```

## NLAP-Specific Profiling Scenarios

### Log Processing Performance
- Profile log file reading operations
- Analyze log parsing and regex operations
- Profile incident story generation
- Test with large log files (100MB+)

### Network Device Operations
- Profile Netmiko connection establishment
- Analyze SNMP query performance
- Test with multiple simultaneous device connections
- Profile timeout handling and retry logic

### Configuration Translation
- Profile configuration file parsing
- Analyze translation operations
- Test with large configuration files
- Profile regex-heavy translation patterns

### Plugin System
- Profile plugin discovery and loading
- Analyze plugin execution overhead
- Test with multiple plugins active
- Profile plugin isolation and resource cleanup

## Performance Optimization Tips for NLAP

1. **Optimize I/O operations**:
   - Read log files in chunks rather than all at once
   - Use buffered I/O for network operations
   - Implement connection pooling for device connections

2. **Optimize regex operations**:
   - Compile regex patterns once and reuse
   - Use simpler regex patterns where possible
   - Pre-compile frequently used patterns

3. **Optimize data structures**:
   - Use appropriate data structures (sets for lookups)
   - Avoid unnecessary data copying
   - Use generators for large datasets

4. **Optimize network operations**:
   - Implement proper timeout handling
   - Use connection pooling
   - Batch device operations where possible

5. **Optimize memory usage**:
   - Process data in streams rather than loading all into memory
   - Clear large data structures when no longer needed
   - Use weak references where appropriate

## Integration with NLAP

For NLAP-specific performance profiling, use context-specific tools:
- Profile with realistic network device logs
- Test with actual device connections (if available)
- Profile in offline mode to ensure no external dependencies
- Consider multi-vendor device variability in performance testing

## Notes

- Always profile with realistic data and workloads
- Profile in a clean environment (close other applications)
- Consider the cost of profiling overhead when interpreting results
- Use multiple profiling tools to get a complete picture
- Profile before and after optimizations to verify improvements