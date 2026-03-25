# HOBL UI Release Notes

## 0.63 (4/23/2024)
* Analysis page
    * From Results or Jobs, you can now right-click in a folder and select "Create Analysis".  This will prompt you to select metrics for the columns, rows, and any filters to roll up.  Multiple metrics can be selected.
    * Resulting table will be shown on Analysis page, and will auto-update as new jobs finish.
    * Matching metrics are averaged.
    * Rows can be selected for filtering or plotting.
    * Double click cell to see individual values or link to run folders.
* Confirmation dialog before running multiple profiles.
* Serializing jobs based on dut_ip rather than profile name.
* Changing profile assignment changes it for all profiles associated with the same DUT.

## 0.60 (3/26/2024)
* Devices page adds Battery Status and Charge information.  This is obtained by polling the device every 15 minutes via the "device\_ping" hobl command.  This can be disabled by setting the parameter "global:disable\_device_ping=1" in a profile.
* The error signature of failed tests are rolled up and presented in their own column in the UI for easier triage.
* On the Job Create page, there is a separate column for tools.  It will show the tools (blue) and prep_tools (yellow) currently set in the profile and plan, and allow you to add or remove tools there.  You can also click a tool to set its parameters.
* Support for installation as an app.

## 0.54
* Support for authentication and authorization.  Disabled by default.
* Ability to view camera feed in Scenarios page while scenarios are running.

## 0.51
* Support for dialog popups, such as with "manual" HOBL scenario.
* Searchable and indexed documentation.
* Update results page to include file pinning and deletion, alignment changes for multiple files, and minimizing the file explorer.
* Added checks within the profile copy page to ensure the profile name is different and valid.
* Added "Rerun Failed Scenarios" button to scenarios page.
* Fixed issue re-ordering scenarios on Create Job page.
* Fixed confusion with results file views sticking when moving to other directories.
* Fixed issue trying to open breadcrumb of result path in new tab.

## 0.50
* Devices page added to show what each device is doing.
* New button on Jobs page to rerun failed scenarios.

## 0.49
* Button to copy current path to clipboard in Results view
* Ability to right-click and copy folders in Results view

## 0.48
* API endpoints for launch plans and getting status to support auto-launching of plans from HOBL and email notifications with status.

## 0.47 
* Further improvements to file handling in Results pages.
* Can hit enter in Results search box to perform search.  Clear button added.
* Plan and Scenario selection inputs on Launch page improved.

## 0.46
* Improvements to file handling and viewing in Results pages.
* If INFO view of a log or ini file shows no lines, then raw content will be displayed.

## 0.45
* Trace viewing features including: Adding and overlaying traces, selecting series', and showing average for zoomed region.
* Recursive results search.

## 0.44
* Added support for hyperlinks in log file.

## 0.43
* Fixed issue sorting files by name on Results page
* Job Launch page - Separation of plans and scenarios into categories.
* Job Launch page - Display of result directory.
* Job Launch page - Ability to override Study Type, so that multiple studies of different types can be queued up.
* Job Launch page - Add button for scenarios to allow multiple additions of same scenario and to prevent accidental addition by selecting wrong scenario.

## 0.42
* Fixed bug with ordering files and folders by date
* Installer now sets scheduled task to "poke" site every minute, which will terminate any zombie scenarios and allow jobs to continue.

## 0.41
* Fixed bug with critical section implementation.

## 0.40
* Implemented critical section for launching scenarios to prevent multiple scenarios running on DUT at same time.
* Fixed bug on reloading test plans that prevented rows from being re-ordered.
* Option to download any file or folder from Results view.

## 0.35
* Fixed auto-scrolling of the log window on the Scenarios page.
* Prevent user from trying to PASS/FAIL a file by popping up an alert that says it can only be done on folders.
* Updated .net version dependency for UpdateIcon that may have prevented it from changing the File Explorer icon properly on hosts that didn't have the old library present.

## 0.30
* Features in this release requires HOBL version 2022.2.1 or higher.
* Added descriptive browser tab titles so that when you open multiple tabs you can tell which one has the content you are looking for.
* Ability to bulk PASS/FAIL run folders on Results page.  Just hold shift or control to multi-select folders, then press the "mark PASS" or "mark FAIL" button.
* Added syntax highlighting for log files.
* Added tag to prevent browser caching when downloading files.
* Results now list "Created" time instead of "Modified" time, to allow chronological viewing of execution flow.
* When terminating a job, Poke will automatically happen to allow progress in the case the job had already exited.
* New Job page will show params color-coded on individual lines for improved readability.
* New Job page adds "+" button to open a dialog to select available parameters instead of having to memorize or look at code.  Unlisted sections or parameters can still be entered.


## 0.20
* Fixed exception when clicking "New Job" from Jobs page when a profile cookie wasn't present.
* Fixed issue when copying profiles and simultaneously removing values.  Removed values weren't saved.  Now they are.
* Updated to .NET 6 libraries to comply with security requirements.
* On Profiles page, the Profile column will now expand to the longest name.  Columns are now resizable by dragging grab handle.
* Pause and Resume has been added to the Jobs and Scenarios pages.
* Jobs page now lists jobs in order of most recent on top, by popular demand.

## 0.14
* Support for viewing RTSP camera from context menu of profile.  Requires running RTSPtoWS server found in hobl\utilities.
* Support for "Quick Actions" (3-dot icon on far right).  These will quickly run common jobs for toggling charger, reboot, etc.
* Support for Quick Assist to remote into a DUT over the internet.
* Added version number in bottom left.
* Profile .ini files will be written to disk (c:\profiles) when Editing is saved, in addition to when they are launched.

## 0.13_beta
* Profile page icons will now work when there is only 1 profile under a folder.
* Partial live camera support

## 0.12
* Proper accounting of Pending jobs on the Jobs page in the case of runs with multiple attempts fail.
* Icons on the buttons on the Jobs page.
* "Poke Jobs" button on the Jobs page that will check for and terminate orphaned processes (such as if host reboots).

## 0.11
* Added more default parameters to profile
* Added support for reference videos in the Documentation section

## 0.10
* Fixed crashes when Profile page buttons were pressed with no profiles selected.
* Recent runs page will default to descending ordering.
* Initial documentation support.  Pulls html files from c:\hobl\docs\support.
* Removed Details button on Profile page.

## 0.9
* Modified Summary page to only update once per minute.
* Modified RecentRuns page to never update.

## 0.8
* On Jobs page, last scenario run will remain under the "Active Scenario" column, even after it has completed, so user will know what custom plans might were run.
* The job's standard output will now be visible in the log view on the Scenarios page, so that any syntax errors or other exceptions can be visible.  However, the "Debug" button will need to be pressed to see these.
* Standard output logs over 1 week old will automatically be deleted, to prevent pile up.  They are now kept in a c:\hobl_scratch folder instead of c:\temp.
* CSV file viewing now formatted into columns.
* Default to downloading files that are not known to be viewable in web, such as .xlsx and .etl.
* Support for watchdog scheduled task that will terminate zombied jobs and continue with plans.  This should automate recovery from server reboots, for example.
* Marking PASS or FAIL will now change folder icon in File Explorer as well.
* Selection in log on Scenarios page, will pause log updates.  Clearing the selection will resume.
* Fixed issue with copying profiles, where dropdown selections were not carried over.
* Fixed errors in Summary view.
* Fixed length of parameters box in Job Create page.

## 0.7
* Can support different urls and ports via an environment variable, HOBLWEB_URL.  The default is "http://localhost:80".  If your environment blocks port 80, then set the enironment variable to something like "http://localhost:5000".
* Optimize single device job launch by going directly to scenarios page after launch.
* Scenarios page has a "Relaunch" button to launch that same plan on that same device.
* Some cosmetic fixes.

## 0.6
* Recent Runs view is operational.
* Added Active Scenario filter box on Jobs page.
* Summary view is operational.
* Fixed profile export download error in stand-alone version.
* Fixed profile export so that it exports full folder hierarchy.
* Fixed profile import bug regarding null values in csv causing null entries in DB.
* Fixed issues with parameter entry on Launch page.
