//--------------------------------------------------------------
//
// HOBL
// Copyright(c) Microsoft Corporation
// All rights reserved.
//
// MIT License
//
// Permission is hereby granted, free of charge, to any person obtaining
// a copy of this software and associated documentation files(the "Software"),
// to deal in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies
// of the Software, and to permit persons to whom the Software is furnished to do so,
// subject to the following conditions :
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
// FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE AUTHORS
// OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
// WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
// OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//
//--------------------------------------------------------------
//
// SimpleTimer for macOS
// Uses mach_wait_until for high-resolution periodic timing
// with configurable busy-work periods.
//

#include <iostream>
#include <cstdlib>
#include <atomic>
#include <pthread.h>
#include <mach/mach.h>
#include <mach/mach_time.h>
#include <unistd.h>

static long g_timerPeriodMs = 1000;
static long long g_busyPeriodMs = 100;
static unsigned long g_totalDurationS = 5;

static std::atomic<bool> g_running{ true };

static mach_timebase_info_data_t g_timebase;

void* TimerThreadProc(void* arg)
{
    (void)arg;

    // Elevate to real-time scheduling so macOS doesn't preempt our tight timing.
    // THREAD_TIME_CONSTRAINT_POLICY tells the Mach scheduler this thread has
    // hard deadlines.  Values are in mach absolute-time ticks.
    {
        uint64_t periodTicks_rt = (uint64_t)g_timerPeriodMs * 1000000ULL
                                  * g_timebase.denom / g_timebase.numer;
        uint64_t busyTicks_rt   = (uint64_t)g_busyPeriodMs  * 1000000ULL
                                  * g_timebase.denom / g_timebase.numer;

        thread_time_constraint_policy_data_t policy;
        policy.period      = (uint32_t)periodTicks_rt;          // nominal period
        policy.computation = (uint32_t)busyTicks_rt;            // max computation per period
        policy.constraint  = (uint32_t)(periodTicks_rt * 9 / 10); // must finish within 90% of period
        policy.preemptible = 1;                                 // allow preemption if needed

        kern_return_t kr = thread_policy_set(
            mach_thread_self(),
            THREAD_TIME_CONSTRAINT_POLICY,
            (thread_policy_t)&policy,
            THREAD_TIME_CONSTRAINT_POLICY_COUNT);

        if (kr != KERN_SUCCESS)
            std::cerr << "Warning: failed to set real-time thread policy ("
                      << kr << "). Timing may be inaccurate." << std::endl;
    }

    // Convert period and busy durations to mach absolute time ticks
    uint64_t periodTicks = (uint64_t)g_timerPeriodMs * 1000000ULL * g_timebase.denom / g_timebase.numer;
    uint64_t busyTicks   = (uint64_t)g_busyPeriodMs  * 1000000ULL * g_timebase.denom / g_timebase.numer;

    uint64_t deadline = mach_absolute_time() + periodTicks;

    while (g_running.load())
    {
        // Wait until next timer period (high-resolution)
        mach_wait_until(deadline);

        if (!g_running.load())
            break;

        // Advance deadline from previous deadline (not current time) to maintain
        // fixed-interval periodicity.
        // If busy work takes 3ms of a 10ms period, next wait is only ~7ms.
        deadline += periodTicks;

        // Busy-work for the specified busy period
        uint64_t start = mach_absolute_time();

        do
        {
            // spin
        } while ((mach_absolute_time() - start) < busyTicks);
    }

    return nullptr;
}

int main(int argc, char* argv[])
{
    if (argc != 4)
    {
        std::cerr << "Usage: " << argv[0]
                  << " <timer_period_ms> <busy_period_ms> <total_duration_s>"
                  << std::endl;
        return 1;
    }

    g_timerPeriodMs  = std::strtol(argv[1], nullptr, 10);
    g_busyPeriodMs   = std::strtoll(argv[2], nullptr, 10);
    g_totalDurationS = std::strtoul(argv[3], nullptr, 10);

    if (g_timerPeriodMs <= 0 || g_busyPeriodMs <= 0 || g_totalDurationS == 0)
    {
        std::cerr << "All arguments must be positive values." << std::endl;
        return 1;
    }

    // Get mach timebase for tick <-> nanosecond conversions
    if (mach_timebase_info(&g_timebase) != KERN_SUCCESS)
    {
        std::cerr << "mach_timebase_info failed" << std::endl;
        return 1;
    }

    // Create timer thread
    pthread_t thread;
    int result = pthread_create(&thread, nullptr, TimerThreadProc, nullptr);
    if (result != 0)
    {
        std::cerr << "pthread_create failed (" << result << ")" << std::endl;
        return 1;
    }

    // Sleep for the total duration
    sleep(g_totalDurationS);

    // Signal thread to stop
    g_running.store(false);

    // Wait for thread to exit
    pthread_join(thread, nullptr);

    return 0;
}
