# HOBL Tools

## audio_volume

Set specified audio volume.

## auto_charge

Turn off charger before scenario, turn it on after.

## auto_recharge

Pause run and recharge device when battery drops below [charge_threshold], then resume.

## battery_bar

Overlays a widget showing battery level.

## battery_stats

Deprecated.

## bat_logger

Surface only.  Logs battery details over time.

## collect_logs

Collect various system logs in the case of scenario failure.

## custom_trace

Periodically start ETL traces.

## debug_logs

Deprecated.

## detect_devices

Deprecated.

## display_brightness

Map display brightness slider percentage to nits value specified by scenarios.

## dumpcap

Dump Wireshark capture.

## etl_trace

Collect ETL trace from specified [providers].

## frame_data

Collect and parse framerate and timing data.  Does not have a significant impact on power consumption.

## kill_teams

Kill all instances of Teams processes.

## kill_widgets

Stops the Windows Widgets from running.

## maxim

Deprecated.

## media_perf

Deprecated.

## mep_toggle

Enable/disable specified MEP features.

## netsh

Get ETL trace of wns_client.

## network_ping

Deprecated.

## net_speed_test

Run speedtest.exe to gauge internet bandwidth.

## net_stat

Reports number of bytes transferred over Wi-Fi vs Cellular.

## perf

Calculates a MOS score from an abl_perf run.

## perfmon_util

Trace specified performance counters that report utilization.

## perf_utc

Collects and processes UTC Perftrack scenarios

## phm

Run Intel's Power House Mountain tool.

## pktmon_count

Count types of network packets transmitted and received.

## pktmon_log

Use pktmon to log network traffic.

## postures_screen_rotation

Deprecated.

## powercfg

Collect sleep study and battery reports.

## power_heavy

Collect and parse a detailed power trace.  Has a significant impact on power consumption.

## power_light

Collect and parse a lightweight power trace.  Does not have a significant impact on power consumption.

## power_mode

Switch to specified power mode (best power efficiency, recommended/balanced, better, best/best performance). Returns to last mode on test end.

## random_fail

Randomly fail a test, for devolpment/debug purposes.

## run_report

Generate a report for the test run.

## screenshot

Record periodic screen shots, for debug purposes.

## screen_record

Records a screen cast from the DUT for debug purposes.  Has considerable power impact.

## serialize_copyback

Deprecated.

## socwatch

Run Intel's SOCWatch tool.

## study_report

Generate a report for the study (all runs in the same study directory).

## surface_logger

Surface-only.  Run SurfaceLogger tool for debug.

## system_deck

AMD-only.

## tearcheck

Check stdin for 'teardown' and end test when consumed

## thermal_daq

A tool for reading thermocouple data from a thermal DAQ server.

## timeout_wake

Deprecated. Wake the DUT on timeout.

## tool_template

A template that can be used for creating new tools.

## touch_activation

Surface-only.  Digitizer debug.

## ttd

Run TTD (Time Travel Debugging)

## video_record

Record a video of the scenario using a camera attached to the Host USB, or an RTSP stream.

