---
sidebar_position: 1
slug: /
---

# HOBL
## Introduction
* Read this file from the HOBLweb UI, Git website, or Preview pane in VS Code for proper formatting.
* "HOBL" (Hours Of Battery Life) is a test framework and set of test scenarios for the purpose of measuring power consumption on Windows devices (MacOS also has limited support).
* "ABL" (Assessment of Battery Life) is one of the HOBL scenarios and is designed to be a simpler and quicker way of projecting battery life with improved representation of background activity, albeit with reduced application coverage.  To run ABL, you still need to set up the HOBL infrastructure, but you don't need to set up Teams and Netflix. 
* Power is expected to be primarily measured with external DAQ equipement, but internal power monitor chips and battery rundown measurements are also supported.
* The HOBL test framework runs on a "Host" Windows 10/11 PC.  Test scenarios execute on the Host and send commands to the DUT (Device Under Test) over a local network to replicate user interactions.
* To ensure standardized and representative measurements, testers must not kill or disable processes or services.  The "hobl_prep" plan will put the system in a quiesced and controlled state suitable for testing.
* **Never run HOBL on a computer that is logged in with anything other than a dedicated test account.**  Files, emails, etc, may be deleted.
* For questions or issues, send mail to [HOBLsupport@microsoft.com](mailto:HOBLsupport@microsoft.com).  Attach the hobl.log file and relevant screen shots for any problematic test run.

## Lab Setup
* The HOBL UI software allows controlling multiple DUTs from a single Host, so a lab will generally have a single HOBL host computer.  
* The HOBL UI is a web server that can be accessed by multiple users simultaneously, if needed.  For larger labs, it can also be executed with IIS.
* The Hosts and DUTs should be on a local network that has internet access.
* The host should be connected with ethernet, but the DUT should be on Wi-Fi, to be representative of a user operating a device on battery.  Ethernet dongles often prevent devices from getting to lower power states.
* The Wi-Fi network should be set up to provide each device with **50 Mbps**, again for representativeness.  Significantly more or less BW has power consumption impact.  Not all AP's are good at controlling this, but we have found the Aruba IAP line of access points adept at it.  50 Mbps is also the minimum bandwidth requirement for correct functionality.
* 5 GHz channels should be used for connecting to DUTs.
* Do not domain-join the DUTs.
* Corporate network traffic can be intense, so it is recommended to deploy a firewall between the lab LAN and corporate networks that will filter out corporate traffic but still allow access to the internet.  This will improve representativeness and reduce test variability.
* HOBL supports automatic recharging of DUTs via a variety of mechanisms, as long as they can be controlled by a shell command.  The commands are specified in the charge_on and charge_off sections of the Device Profile.  The most common mechanisms are:
    1. A Raritan PX-series IP-addressable power strip
    1. <a href="https://dlidirect.com/products/new-pro-switch" target="_blank">Digital-Loggers Pro Switch</a>
    1. An iBoot controlled by either eithernet or relay.  In utilies\usb_relay is a command that will control hid-based USB relays, such as this <a href="https://www.amazon.com/KNACRO-1-Channel-Module-Square-interface/dp/B071VJ628X" target="_blank">KNACRO</a>.  These also work well for interfacing HOBL to external DAQ equipment.
* A luminance meter should be used to determine the DUT brightness setting that corresponds to 150 nits.  Measure and average all 4 counters plus center of a pure white screen.  All tests are expected to run at this brightness except JEITA-related tests (which are at 200).  A nits map should be specified in the profile to associate the appropriate slider postiions to 150 and 200 nits respectively.  <TODO: Add section on profle setup and tools>
* Tests are run with audio volume set to the out-of-box default level.  To ensure consistency, once this value is determined, it should also be specified in the device profile.

## Account Setup
The following accounts need to be created for the DUT:

1. <a href="https://outlook.live.com/owa/" target="_blank">MSA (Microsoft Account)</a> for logging into Windows, Teams, OneDrive, Office, and the Store.  Try not to have the letter 'n' or 'N' in the user name or password, as this will trigger email composition in the Outlook web scenario.  It is critical to set security for the account, otherwise it will require a phone number from you in about a week.  To secure the account, go to <a href="https://account.microsoft.com" target="_blank">https://account.microsoft.com</a> and sign in with the newly created MSA.  Then select the "Security" menu item at the top.  Then click "Get Started" on the "Advanced Security Options" card.  Select to add a verification email account (so that you don't have to use a phone number), then you will be prompted to send verification codes twice.  You can use the same verification account for all MSA's that you create.  Log into the verification account using a different web browser or computer (so you don't log out of your MSA), to retrieve the codes.  At this time, Microsoft only allows 3 MSA's to be created per IP per day, so plan ahead if you need to make a lot.
1. Office - To run the ABL scenario you will need to purchase a subscription to Microsft 365 Personal or Family (not Business), otherwise you will only have a 5-day grace period for testing after install.  The subscription needs to be tied to the MSA.  Each DUT in use needs its own MSA.  If a device is no longer actively using its MSA, then the MSA can be re-used on another DUT, along with the m365 subscription.  There is a limit to how many devices can use a single m365 subscription, so you may need to release the subscription on devices no longer used.  This can be managed at
<a href="https://account.microsoft.com/services/office/install" target="_blank">https://account.microsoft.com/services/office/install</a>.  Click "Sign out of Office" on devices no longer being used.  You may also have to do this for prior OS images on an active DUT, since new OS images may be considered a different "device".
1. Teams - The MSA account needs to be one-time associated with a Teams Organization set up for testing.  Also make sure it's only associated with one organization, otherwise the DUT will prompt for which Org to execute with, which will break the automation.  The Teams org can be shared across any number of MSA's, so generally only one Teams org needs to be set up per test house.  Once the org is set up, you assocociate the MSA by clicking the provided URL and entering the MSA email.
    * Creating a Teams Test Organization:

        1. Go to MS Teams Page:  <a href="https://www.microsoft.com/en-us/microsoft-365/microsoft-teams/group-chat-software" target="_blank">https://www.microsoft.com/en-us/microsoft-365/microsoft-teams/group-chat-software</a>
        2.	Click Sign up for Free:  <a href="https://go.microsoft.com/fwlink/p/?LinkID=2123761&clcid=0x409&culture=en-us&country=US&lm=deeplink&lmsrc=homePageWeb&cmpid=FreemiumSignUpHero" target="_blank">https://go.microsoft.com/fwlink/p/?LinkID=2123761&clcid=0x409&culture=en-us&country=US&lm=deeplink&lmsrc=homePageWeb&cmpid=FreemiumSignUpHero</a>
        3.	Enter Email info and continue with sign up.
        4.	Select “For work and organizations” or “Not a school organization” depending on which prompt you get.
        5.	Enter a Test Company Name (ex. “Test Company”, “Contoso”, “Teams Testing”, etc.).
        6.	Click Create Teams Org.
        7.	Continue to the Web Teams site.
        8.	Wait for Teams org to finish creation and the web Teams site to finish loading.
        9.	Once the page has loaded, click on the user account icon in the top right of the page.
        10.	Select “Manage Org” from the dropdown .
        11.	Click the Settings tab in the top middle of the page.
        12.	Expand the “Manage Link” Section.
        13.	Check the toggle to “Enable link”.
        14.	Check the toggle to “Enable auto-join”.
        15. The Link URL below the toggles can now be used by any test account to join the new test org. 

1. <a href="https://www.netflix.com/signup" target="_blank">Netflix Premium</a> for the Netflix scenario.  Up to 4 DUTs can be used with the same account.  No need for this if only running ABL.

## Host Setup
The host computer houses the HOBL test framework and UI.  Through this, users execute tests remotely on one or more DUTs, and view the results.

Host computer system requirements are:  Intel or AMD processor running Windows 11.  For large labs, factor approximately 1 host core per 15 devices, and 16 GB of RAM + 1 GB for every 3 devices.

**IMPORTANT:  Don't clone the repo.  Run host_setup.exe to clone the repo so that critical git hooks get installed.**

Download and execute "host_setup.exe" from the "setup" folder <a href="https://msftdevicespartners.visualstudio.com/Power/_git/hobl?version=GBmaster&path=/setup" target="_blank">here</a>.  **Make sure you are still logged into this website when executing host_setup.exe.**  It will:

1. Prompt for an install folder.  To minimize complexity, use the default "c:\hobl".
1. Install Git, because that's necessary to clone the repo and pull updates.
1. Install TortoiseGit, because it allows a handy interface to Git from File Explorer, although not required.
1. Shallow clone the HOBL source repo with filter=tree:0 to minimize transfer size, and set necessary git hooks.
1. Install python embedded into the specified hobl folder.  This way the specific version and libraries won't interfere with any existing system-wide installs.
1. Install the HOBL UI, downloading components from Azure and prompting you for credentials as needed.
    1. If you installed hobl in a folder other than "c:\hobl", then you need to hand-edit c:\hoblweb\appsettings.json and modify the "DocsPath" paramter accordingly.
    1. Likewise, if you intend to have your results go to a different base folder than "c:\hobl_results", modify the "ResultsPath" parameter accordingly.  Make sure that the "results_dir" parameter in your profile includes this base path.

To get future updates to the HOBL source code, do a "git pull" in the hobl folder.  To get future updates to the HOBL UI, rerun host_setup.exe and just select "HOBL User Interface" item.

HOBLweb UI documentation can be found here: [HOBL UI](HOBL_UI.md)

Set up a Device Profile for each DUT in the HOBLweb UI, giving it a unique name (typically we name it the name of the DUT), and modifying the parameters as appropriate.  Use the Parameters documentation as a guide.

## DUT Setup
1. Download and copy dut_setup.exe from here to a USB stick.
1. Plug the USB stick into the DUT and execute dut_setup.exe.
1. You will be prompted to change the name of the device if desired.  Click Next.
1. You will be prompted to enter Wi-Fi information.  This will be saved to the USB stick so that you can set up the device again in the future, or other devices in the lab, without having to re-enter the information.
    1. This will setup various registry settings and launch simple_remote to allow communication from the host.
    1. If you see an error when it tries to set the developer mode, this can safely be ignored.
4. Test network connection to the DUT:
    1. Host and DUT need to be on the same subnet (first 2 octets of the IP address).
    1. Run Cmd or Powershell on the Host.
    1. Make sure sure DUT responds to pings:  `ping <dut_ip>`
    1. Make sure DUT can ping host as well.
    1. Run the "comm_check" scenario to make sure that all communications needs are met.
1. Run the "hobl_prep" (or "abl_prep" if only running ABL) test plan from the Host compputer by doing the following:
    1. Some notes about the hobl_prep_plan:
        1. daily_prep - Processes any queued up Windows tasks to create a more controlled environment for testing.  This should be run at the beginning of any test plan.  It can take a long time to execute after a fresh image/setup, maybe over an hour and can include multiple reboots.
        1. office_install - Removes any existing Office installations and installs a specific version of Office365 that this version of HOBL is designed to work with.  If the remove portion fails, you may need to manually uninstall a prior version of Office.  There is an optional "activate" phase that will attempt to automatically activate an MSA account that is associated with an appropriate o365 subscription.  If you want to just use the 5-day free trial, or you are internal to Microsoft, set the activate parameter to 0.
    1. If HOBLweb is not already running in your web browser, double-click it's icon on the host desktop.
    1. On the Profiles page, right-click the profile you want to run with, then select "Launch Job".
    1. In the New Job page, in the "Load Plan" drop-down, select "hobl_prep" or "abl_prep" as appropriate.
    1. Click the "Submit" button at the top-right to execute the plan.
    1. Note any failures.  Check the log window or hobl.log files in the associated result_dir to see error messages.  If resolution isn't clear, send mail to HOBLsupport@microsoft.com and attach the relevant hobl.log files.

## Usage
After the relevant "prep" files have been run.  The test scenarios can be run similarly. The test scenarios that make up the "HOBL" suite have been pre-assembled in a "test plan", `testplans\hobl.ps1`.
* Testplans can be run from the command line, if integrating with higher level automation, but running from the HOBLweb UI is generally preferred.
* Limiting which scenarios to run, such if some need to be re-run, can be done by either commenting out lines in the test plan, or utilizing the checkboxes in the GUI interface.
### Top level
  * The HOBL framework is a general purpose test framework based on the Python UnitTest framework.  Windows Application Driver and Web Driver technologies are used to remotely control the interaction of applications and web sites.
  * hobl.cmd is the top-level file that can be executed from the command line.  Give arguments for the parameter file and the scenario to be run.  For example, to run the web scenario:
```
    hobl.cmd -p my_profile.ini -s web
```
 * However, this command is very limited and not supported for external use.  The HOBL UI is a major better way to run tests and plans.  For interfacing with external systems, ask HOBLsupport about the available REST API.

## Details

## Scenarios
* The hobl/scenarios/[os] dir contains the scenarios that can be run.
* A scenario, or test case, contains the code to interact with the DUT (Device Under Test) according to a specific user scenario.
* Most scenarios require some initial preparation.  To automate the preparation, a `<scenario>`_prep.py is included, if needed.  This is generally only needed to be run once each time the DUT is re-imaged.  The prep scenarios are executed just like any other scenario.
* A new scenario can be created by simply copy/rename/modify an existing one in this folder.

## Parameters
There are 3 levels of parameters:
* Default values of scenario-specific parameters are set in each scenario file.  Generally, the default values are set to what should be used for a proper HOBL run.  The top-level hobl.py sets the "global" default parameters, which are those common to all scenarios.
* A Device Profile file, in .ini format, can be used to override the defaults.  The file has sections for "global", as well as any relevant scenarios.  A "default.ini" is provided as a starting point, which contains the parameters that would typically need to be overwritten, such as the various credentials needed.  Users should copy this to create their own.  It is expected that a lab would have a separate Device Profile file for each DUT, as each DUT would need its own accounts.
* Finally, parameters can be overridden on the command line.  This overrides both the defaults and the Device Profile file.  The argument format is:
  ```
      <scenario>:<key>=<value>
  ```

## Tools
* One of the global parameters is "tools".
* Specify a space-separated list of tools from the tools folder to run for each scenario.
* A tool is a python file that contains specific predefined methods called a specific phases of the test flow.  This wrapper is used to call any external tools that need to be run at the appropriate time.
* Create a new tool by copy/rename/editing an existing one.
* Tools can be added to an existing list on the command line, using a "+" symbol as the first character.  i.e.
    * hobl.cmd -p my\_params.ini -s lvp global:tools="+video_record"
    * This will add "video\_record" to the list of tools specified in my_params.ini
* Available tools include:
    * auto_recharge - Turns on the charger when battery level reaches a specified low threshold, and turns off at the specified upper threshold.
    * auto_charge - Turns off the charger before each scenario and turns on after.
    * etl_trace - Records ETL traces using WPR.  Specify .wprp providers on the "providers" parameter.
    * perf - Post-processes a particularl ETL trace for performance metrics.
    * powercfg - Runs the Windows powercfg.exe command for such things as a Sleep Study Report.
    * run\_report - Rollup a report of each run.  This is needed for the study_report scenario to rollup a report of the whole study.
    * screenshot - Capture screenshots of the DUT at a specified interval.
    * screen_check - Capture screenshots at strategic points of the test and compare with expectations captured during training.  This is a critical tool for making sure the test ran correctly.
    * phm - A proprietary tool for Intel processors.
    * video_record - Record video of a scenario from a camera connected to the host.
    * screen_record - Record video of a scenario from capturing the display buffer on the DUT itself.  This consumes a lot of power and should only be done on scenarios where Power consumption is not being studied.  However, it gives very clear video for debug purposes without requiring an external camera.
    * network_ping - Pings dut from host, if pings are not all returned, enables charger and continues pinging dut until all pings are returned.  Then disables charger.


## DUT folders
* There are 2 folders created on the DUT:  c:\hobl_bin and c:\hobl_data
* hobl_bin is where any scripts, excecutables, or resources that are needed for execution are copied, ususally by a prep scenario.
* hobl_data is cleared at the beginning of each scenario.  Any data produced by the scenario and tools while running on the DUT gets put there.  At the end of the scenario everything in that folder is copied back to the host computer's result directory.  Examples, include ETL traces, log files, config_check output, etc.

## Result directory
* The global parameter "result_dir" represents the base directory where results will be stored.  Default is "c:\hobl_results".  Relative paths must not be used.
* The global parameter "run_type" allows for an additional subdirectory to be specified.  Default is blank.  This can make it easier to organize multiple studies of the same scenario with different settings.  For example, a screen brightness study might specify a base directory in the parameters file, but each run in the test plan can override the run_type parameter with a directory that represents the brightness being set.
* Finally, the leaf directory automatically created is of the form `<scenario>_<iter>`.  Where `<iter>` is a 3-digit number that auto increments for each run.
* So the final result directory is `<result_dir>\<run_type>\<scenario>_<iter>`

## Reporting
* Run Report - A report rolled up for each scenario run. To run, add "run_report" to the list of tools on your global:tools parameter.  This does two things:
    1. The tool runs an optional script specified in the script_path parameter to roll up any data collected by external equipment, such as DAQs, to a *_power_data.csv file, that just containes rows of `<key>,<val>` for any metrics you would like rolled up.  Since such a script is particular to individual lab environments, it is not provided, but we can help with creation of yours.
    2. A rollup_metrics script is run that rolls up all available .csv files, such as from other tools that may have been run, as well as the pre and post config_check runs, into a single *_metrics.csv file.  This summary file will be used by the study_report rollup.  The rollup_metrics.py script is in the "utilities" folder and can also be run manually and recursively on a full set of runs in one shot.
* Study Report - Rolls up the Run Reports for an entire study.
    * Study Report is run as a scenario when you want to rollup existing results.  It can even be run in another window while other scenarios are currently running.  It won't interfere.
        * hobl.cmd -p my_params.ini -s study_report
    * There are a number of optional parameters to direct the output:
        1. result_path - study directory to roll up, defaults to result_dir specified in .ini file.
        1. template - A spreadsheet to be used as a template.  Defaults to the HOBL spreadsheet in the docs directory.  This is the spreadsheet that should be used for any valid HOBL study.
        1. trend - Path to a higher level directory that contains a set of studies to be rolled up into a trend plot.
        1. goals - Path to a .csv file that contains the targets for each metric/scenario in the templates Scorecard sheet.
        1. adders - Path to .csv file that contains the keyboard and touch adders to be used in the HOBL calculations
        1. name - An optional name for the resulting spreadsheet.  Default is the study name (derived from the parent directory) followed by "_study_report.xlsx".
        1. active_target - Active On target for the trend plot in hours.
        1. lvp_target - LVP On target for the trend plot in hours.
        1. hobl_target - HOBL On target for the trend plot in hours.
        1. battery_capacity - Typical battery capacity in Wh.

## Log file
* A hobl.log file is created and written to during the test execution in the scenario run folder.  Lines are categorized as INFO, DEBUG, and ERROR.  INFO relays what the scenario is doing at a high level.  DEBUG is for seeing the details of what is actually happening.  And ERROR highlights what went wrong.

## Callbacks
* Callback parameters are provided for interfacing with external equipment, such as DAQs and relays.
* For each scenario there are 3 callbacks:
    1. callback_test_begin
    1. callback_test_end
    1. callback_data_ready
    1. callback_test_fail
* For each of these, a shell command can be specified to be executed.  Typically this would be another script that would trigger DAQ recording, for example.
* The cs_floor and cs_active scenarios also have callback parameters for triggering the button of the device.  Typically this is done via a script that triggers a relay or other IO to activate the power button of the device.
* The charge_on and charge_off scenarios, as well as the auto_recharge and auto_charge tools similarly have callbacks to enable and disable the charger.

## Config Check
* The config_check scenario is a critically important scenario that should be run as the first step of any study.  It dumps relavant configuration details of the DUT, as well as the version of this Git repo.
* Further, if the global config_check parameter set (default), then a pre-run and post-run small config_check is run before and after the test respectively.  This helps capture any changes in screen brightness, volume, radios, etc.

## Graphic User Interface
* Documentation of the HOBLweb UI can be found here: [HOBL UI](HOBL_UI.md)

## Test Plans
* A "test plan" is simply a sequence of runs that make up a study.
* A powershell file that makes one hobl.py call per line with appropriate command line args.  So a test plan can be executed directly on a command/powershell prompt, or via the GUI.
* The default test plans take the Device Profile as an argument so that the plan file doesn't need to be modified for different stations.
* Standard test plans are provided in the "testplans" folder.
    1. hobl_prep.ps1 - runs all the prep scenarios in a single batch.
    1. hobl.ps1 - runs all the HOBL scenarios with the recommended number of iterations as well as training runs.
    1. hobl_etl and hobl_phm - contains runs with ETL and Power House Mountain tracing respectively for debug purposes.

## SimpleRemote
* SimpleRemote is a console application that runs in the background on the DUT to accept network commands (JSON RPC) for executing commands/programs and transferring files.
* Part of dut_setup is to install SimpleRemote and set it to execute automatically upon system boot.
* InputInject is a plugin to SimpleRemote that very efficiently handles injecting keystrokes and mouse clicks on the DUT, as well as taking screen shots.

## Windows Application Driver
* Windows Application Driver is similar to WebDriver, but controls Windows applications or desktop instead of web sites in a browser.
* It uses the same JSON Wire Protocol as webdriver, so the client-side code on the Host is essentially the same, just communicates through a different port.
* On the DUT (server) side, it translates Webdriver commands to Windows UI Automation protocol for controlling apps.
* Scenarios that need WinAppDriver will launch the server on the DUT at the beginning of the scenario and shut it down at the end.
* Use of WinAppDriver is being phased out in favor of image-based automation, using the ScenarioMaker tool.  No new scenarios using WinAppDriver will be permitted to be added to the codebase.

## Scenario Maker
* ScenarioMaker is an application that facilitates the creation of new test scenarios (or editing existing oens), and is only availabe with the dev host setup.
* Run Scenario Maker by execution hobl\ScenarioMaker\ScenarioMaker.pyw.
* It starts with a remote connection to a DUT (specify IP address in Settings), then allows you to compose a sequence of actions for the scenario using the menu.
* Record mode records you interacting with the DUT as a user would, and generates the appropriate action sequence for the test quickly and easily.  Caution, though, as these won't be optimized for power consumption.  To minimize power consumption, only take new screen captures when what you want to capture wasn't in a previous capture, and only capture as much of the screen as necessary.  Smaller screen region captures are faster and use less power.

