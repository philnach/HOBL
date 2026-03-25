if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s recharge global:run_type="Misc" global:tools="+power_light auto_charge" recharge:resume_threshold="97"
# .\hobl.cmd -p $ARGS[0] -s button_install global:attempts=2 global:run_type=Prep global:post_run_delay=0
# .\hobl.cmd -p $ARGS[0] -s cs_floor_prep global:attempts=2 global:run_type=Prep global:post_run_delay=0
# .\hobl.cmd -p $ARGS[0] -s config_check global:run_type="Misc"
.\hobl.cmd -p $ARGS[0] -s discharge global:run_type="Misc" global:tools="+power_light auto_charge" discharge:resume_threshold="95"
.\hobl.cmd -p $ARGS[0] -s idle_desktop idle_desktop:duration="3600" global:run_type="Power"
.\hobl.cmd -p $ARGS[0] -s cs_floor cs_floor:cs_duration="3600" cs_floor:button_to_record_delay="900" global:post_run_delay="60" global:run_type="Power"
.\hobl.cmd -p $ARGS[0] -s idle_desktop idle_desktop:duration="3600" global:run_type="Power"
.\hobl.cmd -p $ARGS[0] -s cs_floor cs_floor:cs_duration="3600" cs_floor:button_to_record_delay="900" global:post_run_delay="60" global:run_type="Power"
.\hobl.cmd -p $ARGS[0] -s idle_desktop idle_desktop:duration="3600" global:run_type="Power"
.\hobl.cmd -p $ARGS[0] -s cs_floor cs_floor:cs_duration="3600" cs_floor:button_to_record_delay="900" global:post_run_delay="60" global:run_type="Power"
.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type="Misc" global:tools="+power_light auto_charge"
.\hobl.cmd -p $ARGS[0] -s study_report global:attempts="1" global:tools="+power_light auto_charge"
.\hobl.cmd -p $ARGS[0] -s process_idle_tasks global:post_run_delay="600" daily_prep:timeout=7200 daily_prep:loops=1
.\hobl.cmd -p $ARGS[0] -s reboot global:run_type="Misc" 