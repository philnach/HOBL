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

#include <iostream>
#include <cstdlib>
#include <atomic>
#include <Windows.h>

static LONG g_timerPeriodMs = 1000;
static DWORD g_totalDurationS = 5;
static LONGLONG g_busyPeriodMs = 100;

static std::atomic<bool> g_running{ true };

DWORD WINAPI TimerThreadProc(LPVOID lpParam)
{
    HANDLE hTimer = static_cast<HANDLE>(lpParam);
    DWORD tickCount = 0;

    LARGE_INTEGER freq;
    QueryPerformanceFrequency(&freq);
    LONGLONG countsPerBusyPeriod = freq.QuadPart * g_busyPeriodMs / 1000;

    while (g_running.load())
    {
        DWORD waitResult = WaitForSingleObject(hTimer, INFINITE);
        if (waitResult == WAIT_OBJECT_0)
        {
            if (!g_running.load())
                break;

            ++tickCount;

            LARGE_INTEGER start, current;
            QueryPerformanceCounter(&start);
            LONGLONG iterations = 0;

            do
            {
                QueryPerformanceCounter(&current);
                ++iterations;
            } while ((current.QuadPart - start.QuadPart) < countsPerBusyPeriod);
        }
        else
        {
            std::cerr << "WaitForSingleObject failed (" << GetLastError() << ")" << std::endl;
            break;
        }
    }

    return 0;
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

    g_timerPeriodMs  = static_cast<LONG>(std::strtol(argv[1], nullptr, 10));
    g_busyPeriodMs   = static_cast<LONGLONG>(std::strtoll(argv[2], nullptr, 10));
    g_totalDurationS = static_cast<DWORD>(std::strtoul(argv[3], nullptr, 10));

    if (g_timerPeriodMs <= 0 || g_busyPeriodMs <= 0 || g_totalDurationS == 0)
    {
        std::cerr << "All arguments must be positive values." << std::endl;
        return 1;
    }

    HANDLE hTimer = CreateWaitableTimerExW(nullptr, nullptr, CREATE_WAITABLE_TIMER_HIGH_RESOLUTION, TIMER_ALL_ACCESS);
    if (!hTimer)
    {
        std::cerr << "CreateWaitableTimerEx failed (" << GetLastError() << ")" << std::endl;
        return 1;
    }

    LARGE_INTEGER dueTime;
    dueTime.QuadPart = -static_cast<LONGLONG>(g_timerPeriodMs) * 10000LL;

    if (!SetWaitableTimer(hTimer, &dueTime, g_timerPeriodMs, nullptr, nullptr, FALSE))
    {
        std::cerr << "SetWaitableTimer failed (" << GetLastError() << ")" << std::endl;
        CloseHandle(hTimer);
        return 1;
    }

    HANDLE hThread = CreateThread(nullptr, 0, TimerThreadProc, hTimer, 0, nullptr);
    if (!hThread)
    {
        std::cerr << "CreateThread failed (" << GetLastError() << ")" << std::endl;
        CancelWaitableTimer(hTimer);
        CloseHandle(hTimer);
        return 1;
    }

    Sleep(g_totalDurationS * 1000);

    g_running.store(false);
    CancelWaitableTimer(hTimer);

    // Set the timer to signal immediately so the thread wakes up and sees g_running == false.
    LARGE_INTEGER immediate;
    immediate.QuadPart = 0;
    SetWaitableTimer(hTimer, &immediate, 0, nullptr, nullptr, FALSE);

    WaitForSingleObject(hThread, INFINITE);

    CloseHandle(hThread);
    CloseHandle(hTimer);

    return 0;
}
