if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}

.\hobl.cmd -p $ARGS[0] -s edge_install global:run_type=Prep global:post_run_delay=0 global:attempts=2 global:browser=Edge
# .\hobl.cmd -p $ARGS[0] -s edge_install global:run_type=Prep global:post_run_delay=0 global:attempts=2 global:browser=EdgeDev
.\hobl.cmd -p $ARGS[0] -s edge_install global:run_type=Prep global:post_run_delay=0 global:attempts=2 global:browser=EdgeBeta
.\hobl.cmd -p $ARGS[0] -s edge_install global:run_type=Prep global:post_run_delay=0 global:attempts=2 global:browser=EdgeCanary

.\hobl.cmd -p $ARGS[0] -s abl_training abl:sections=web global:post_run_delay=0 global:attempts=2 global:browser=Edge global:module_name=abl_edge_training
# .\hobl.cmd -p $ARGS[0] -s abl_training abl:sections=web global:post_run_delay=0 global:attempts=2 global:browser=EdgeDev global:module_name=abl_edgedev_training
.\hobl.cmd -p $ARGS[0] -s abl_training abl:sections=web global:post_run_delay=0 global:attempts=2 global:browser=EdgeBeta global:module_name=abl_edgebeta_training
.\hobl.cmd -p $ARGS[0] -s abl_training abl:sections=web global:post_run_delay=0 global:attempts=2 global:browser=EdgeCanary global:module_name=abl_edgecanary_training

# .\hobl.cmd -p $ARGS[0] -s config_check global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s version_report global:run_type=Prep global:post_run_delay=0
# .\hobl.cmd -p $ARGS[0] -s process_idle_tasks global:run_type=Prep global:post_run_delay=0
# .\hobl.cmd -p $ARGS[0] -s reboot global:run_type=Misc global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s charge_off global:run_type=Misc global:post_run_delay=900

.\hobl.cmd -p $ARGS[0] -s idle_desktop global:iterations=3 idle_desktop:duration=1200 global:run_type=Power global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edge global:tools="+power_light"
# .\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgedev  global:module_name=abl_web_dev global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgebeta global:module_name=abl_web_beta global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgecanary global:module_name=abl_web_canary global:tools="+power_light"
# .\hobl.cmd -p $ARGS[0] -s config_check

.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edge global:tools="+power_light"
# .\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgedev  global:module_name=abl_web_dev global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgebeta global:module_name=abl_web_beta global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgecanary global:module_name=abl_web_canary global:tools="+power_light"
# .\hobl.cmd -p $ARGS[0] -s config_check

.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edge global:tools="+power_light"
# .\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgedev  global:module_name=abl_web_dev global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgebeta global:module_name=abl_web_beta global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgecanary global:module_name=abl_web_canary global:tools="+power_light"
# .\hobl.cmd -p $ARGS[0] -s config_check

.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edge global:tools="+power_light"
# .\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgedev  global:module_name=abl_web_dev global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgebeta global:module_name=abl_web_beta global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgecanary global:module_name=abl_web_canary global:tools="+power_light"
# .\hobl.cmd -p $ARGS[0] -s config_check

.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edge global:tools="+power_light"
# .\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgedev  global:module_name=abl_web_dev global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgebeta global:module_name=abl_web_beta global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=Power abl:training_module=abl_edgecanary global:module_name=abl_web_canary global:tools="+power_light"
# .\hobl.cmd -p $ARGS[0] -s config_check

.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=ETL abl:training_module=abl_edge global:tools="+power_heavy"
# .\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=ETL abl:training_module=abl_edgedev  global:module_name=abl_web_dev global:tools="+power_heavy"
.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=ETL abl:training_module=abl_edgebeta global:module_name=abl_web_beta global:tools="+power_heavy"
.\hobl.cmd -p $ARGS[0] -s abl_web global:run_type=ETL abl:training_module=abl_edgecanary global:module_name=abl_web_canary global:tools="+power_heavy"
# .\hobl.cmd -p $ARGS[0] -s config_check global:post_run_delay=0

.\hobl.cmd -p $ARGS[0] -s idle_desktop global:iterations=3 idle_desktop:duration=1200 global:run_type=ETL global:tools="+power_heavy"

.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s study_report global:run_type=Misc global:post_run_delay=0

.\hobl.cmd -p $ARGS[0] -s notify global:run_type=Misc global:post_run_delay=0

