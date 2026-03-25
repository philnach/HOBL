# HOBL 25 Release Notes

## 2025.5.0 Release (10/11/2025)
* New host_setup.exe that addresses two problems:
    1. Large transfer size - host_setup now does a shallow clone to reduce transfer time by 5x.
    1. Conflicting versions of python and/or libraries - host_setup now installs a python distribution embedded into the hobl directory itself, isolated from any system python installs.

## 2025.4.0 Release (10/2/2025)
* idle_desktop has been increased to 20 minutes to better capture sporatic background activity and reduce run-to-run variation.
* Teams scenarios have been rewritten using image-based automation.  Since, this interactivity occurs only during setup and teardown, there is no power delta for the part of the call being measured.

## 2025.3.0 Release (9/19/2025)
* Since Microsoft is no longer supporting the purchase of movies in the Microsoft Store, the "halo2" scenario has been removed from all test plans and study reports.  Accordingly, the weighting for "netflix" has been doubled to compensate.

## 2025.2.0 Release (6/15/2025)
* web - Moved cursor position during scrolling to the left side of the screen, to match hobl 24.  May have minor power impact.
* Added mac_web, web scenario for Mac.
* Added Mac support to display_brightness, audio_volume, and screen_record tools.

## 2025.1.0 Release (5/16/2025)
* May update to Office that fixes the high power in Outlook Classic.
* Productivity_prep now sets reg key to keep Office in "mouse mode" even when a blade is detached, to resolve automation issues.

## 2025.0.1 Release (4/18/2025)
* Signed setup binaries.
* dut_scaling_override global parameter added for use in the case the DUT is not reporting its Windows Scaling factor properly.  The value is a fraction, like "2.0" to represent 200%.
* study_report and run_report scenarios now completely offline (don't try to communicate with DUT).
* host_setup_dev.exe updated with latest versions of tools.
* HOBL 24 scenarios and test plans are available in case you need to go back for some reason, without changing the repo.  They are designatied with "_24" in the name.
* Delay added to the Outlook scenario to accommodate slow devices.
* Larger capture added to web_prep to accommodate favorites bar.


## 2025.0.0 Release (4/5/2025)
### IMPORTANT ###
* Additional python libraries need to be installed.  To upgrade to this release, you'll need to run the host_setup_dev.exe and select the "Python" item to install the new libraries.
* The HOBL UI also needs to be updated to at least version 0.81, so select that in host_setup_dev.exe as well.
* A new InputInject library is required on the DUT.  To get this run the setup\dut_setup.exe on the DUT.
### POWER IMPACT ###
* The 2502 version of Outlook Classic has been found to have elevated power while typing, ~8W on tested platforms.  This currently results in ~90% increase of SOC power and ~30% increase to total power for the overall productivity scenario.  This is bugged, and we'll move to the fixed version of Office as soon as it's available.
* No other significant power impacts.
### NEW FEATURES
* HOBL 25 implements a whole new way to do UI automation, using image recognition instead of relying on accessibility tags.  This has the following benefits:
    * No need for training runs.  Elements are found in real-time, by taking a partial screen capture, filtering/scaling the image, and template-matching with image of desired UI element to find the appropriate click coordinates.
    * Ability to automate MacOS, W365, and other operating systems that don't have available accessibility tags.
    * No need for screen_check tool.  Since elements are found at runtime, checking is built-in.
    * Hedge against WinAppDriver end of support.
    * Greater ability to work elements not being found, resulting in less work blockage.
    * Can automate apps that don't have tags, like Adobe products and games.
* Initially, the scenarios implemented this new mechanism are: abl_active, abl_standby, web, idle_apps, productivity, youtube, netflix, and halo2.  Other scenarios will be converted as need arises.
* Activity timing for these new scenarios has also been revamped.  Timing of each event is now based on a fixed reference point, specifically the beginning of the scenario.  This prevents variability from accumulated delays in network or processing of actions.
* Power consumption of the new implementations of web and productivity are actually a little bit lower than before with screen_check due to optimizations in the screen capture and input injection.
* The old WinAppDriver based mechanism still exists and the other scenarios still use that.
* The web archive has been refreshed with latest copies of the sits.  Minor changes include being logged in to Instagram and a different search in Amazon.  There seems to be a small increase in power with the new pages, but generally insignificant.
* Office was advanced to version 2502.  Power consumption is generally a little lower, except for Outlook, which jumps to ~8W while typing.  A high-priority bug has been filed on this.
* Parameter overrides no longer need the section specified.  For example, instead of "lvp:duration=300", you can write "duration=300".  The infrastructure will know to apply it to the scenario you're running.  But beware of self-referencing parameters in your profile.  For example "study_report:product=[product]" will cause an infinite loop and needs to be removed.  In this case, study_report now references the global:product directly.
* ScenarioMaker application to easily create code-free test scenarios with point-and-click operations.
* Remote - In the new HOBL UI, right-clicking on a profile will show "Remote" in the context menu, which allows you to efficiently remote into the DUT for manual operations.  Copy-paste are supported, as well as transferring files to a file share.  To do the latter set up global parameters in your profile for "remote_share_path", "remote_share_username", and "remote_share_password".  A Z: share will be mounted to the specified path during your remote session.  Since Remote is not a scenario (like Quick Assist was), you are able to remote to a DUT while a test is in progress, but there is a sizeable power impact from that so you will be prompted with a warning first.

