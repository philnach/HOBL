macOS SimpleTimer

High-resolution timer utility using mach_wait_until for precise periodic
timing with configurable busy-work periods.

BUILDING:
    make

USAGE:
    ./timers <timer_period_ms> <busy_period_ms> <total_duration_s>

    timer_period_ms   - Timer fires every this many milliseconds
    busy_period_ms    - CPU busy-work duration per timer fire (milliseconds)
    total_duration_s  - Total run time in seconds

EXAMPLES:
    ./timers 1000 100 60
        1s period, 100ms busy work, run for 60 seconds

    ./timers 10 3 30
        10ms period, 3ms busy work, run for 30 seconds

    ./timers 1 0 5
        1ms period, no busy work, run for 5 seconds

HOW IT WORKS:
    1. A background thread waits on mach_wait_until (high-res timer)
    2. On each timer fire, it busy-spins for the specified busy period
    3. After total_duration_s, the main thread signals the timer thread to stop
    4. Clean shutdown via pthread_join
