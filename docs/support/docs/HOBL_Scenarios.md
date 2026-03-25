# HOBL Scenarios

## cinebench

The Cinebench benchmark.

## collect_logs

Collect various system logs.

## daily_prep

Preforms various tasks that prepare a device for testing.  This includes queuing background maintenance tasks in Windows so they will not be running during tests.  To ensure consistent results, please run this scenario at least once per day on devices before starting tests.

## lvp

Plays a video on full screen for a specified amount of time.  

## lvp_jeita

Plays a video in full screen mode in accordance with reqirements set by the Japan Electronics and Information Technology Industries Association for battery operated electronic devices being released in Japan.

Please do not alter parameters as they have been set to meet the requirements of that governing body

## system_prep

Preforms various tasks that prepare a device for testing.

## teams2_1on1_audio

Microsoft Teams audio call with 1 bot participant.
Local camera is off and mic is on, other participant is a bot sending audio.

## teams2_1on1_video

Microsoft Teams video call with 1 bot participant.
Local camera and mic are on, other participant is a bot sending video and audio.

## teams2_3x3_audio

Microsoft Teams audio call with 9 bot participants.
Local camera is off and mic is on, other 9 participants are bots sending audio.

## teams2_3x3_present

Microsoft Teams video call with 9 bot participants.
Local camera and mic are on, other 9 participants are bots sending video and audio.
Local users is sharing screen.

## teams2_3x3_video

Microsoft Teams video call with 9 bot participants.
Local camera and mic are on, other 9 participants are bots sending video and audio.

## teams2_3x3_vid_share

Microsoft Teams video call with 9 bot participants.
Local camera and mic are on, other 9 participants are bots sending video and audio.
One of the bots is sharing a video.

## teams2_9b_audio_desktop

Microsoft Teams audio call with 9 bot participants.
Local camera is off and mic is on, other 9 participants are bots sending audio.
Local user is sharing desktop.

## teams2_audio_desktop

Microsoft Teams audio call with 1 bot participant.
Local camera is off and mic is on, other participant is a bot sending audio.
Local user is sharing desktop.

## teams2_idle

Teams is launched and then minimized to run in the background for the duration of the test.

## youtube

Plays a YouTube video in a web browser in Default View mode.

Steps:

1. Navigate to Tears of Steel YouTube video URL: [youtu.be/41hv2tW5Lc4](https://youtu.be/41hv2tW5Lc4)
2. Change video quality to 1080p.
3. Let video play for specified duration and loops.
4. Close web browser.

## comm_check

Checks for valid communications between host and DUT.

Steps:

1. Ping DUT
2. SimpleRemote RPC call
3. SimpleRemote Async call
4. WinAppDriver launch and communication
5. Report results

## mac_cinebench

Scenario to run Cinebench on Mac, supporting singleCore and multiCore runs, collecting scores and battery rundown.

