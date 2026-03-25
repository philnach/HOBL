if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}

# .\hobl.cmd -p $ARGS[0] -s config_check global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s version_report global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s process_idle_tasks global:post_run_delay=600
.\hobl.cmd -p $ARGS[0] -s charge_off

.\hobl.cmd -p $ARGS[0] -s abl_web global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s adk_web global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s abl_web global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s adk_web global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s abl_web global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s adk_web global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s abl_web global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s adk_web global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s abl_web global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s adk_web global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s abl_web global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s adk_web global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s abl_web global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s adk_web global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s abl_web global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s adk_web global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s abl_web global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s adk_web global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s abl_web global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s adk_web global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s charge_on global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s study_report global:post_run_delay=0
