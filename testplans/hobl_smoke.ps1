if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
# .\hobl.cmd -p $ARGS[0] -s process_idle_tasks global:run_type=Power
# .\hobl.cmd -p $ARGS[0] -s config_check
# .\hobl.cmd -p $ARGS[0] -s charge_off global:run_type=Misc

.\hobl.cmd -p $ARGS[0] -s idle_desktop global:run_type=Power global:tools="+power_light" duration=5
.\hobl.cmd -p $ARGS[0] -s cs_floor global:run_type=Power global:tools="+powercfg power_light" cs_floor:button_to_record_delay=5 cs_floor:cs_duration=10
.\hobl.cmd -p $ARGS[0] -s abl_active global:run_type=Power global:tools="+power_light" idle_time=5
.\hobl.cmd -p $ARGS[0] -s abl_standby global:run_type=Power global:tools="+powercfg power_light" standby_duration=5
.\hobl.cmd -p $ARGS[0] -s web global:run_type=Power global:tools="+power_light" duration=5
.\hobl.cmd -p $ARGS[0] -s productivity global:run_type=Power global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s idle_apps global:run_type=Power global:tools="+power_light" idle_time=5
.\hobl.cmd -p $ARGS[0] -s netflix global:run_type=Power global:tools="+power_light" duration=5
.\hobl.cmd -p $ARGS[0] -s youtube global:run_type=Power global:tools="+power_light" duration=5
.\hobl.cmd -p $ARGS[0] -s lvp global:run_type=Power global:tools="+power_light" duration=5
.\hobl.cmd -p $ARGS[0] -s teams2_3x3_video global:run_type=Power global:tools="+power_light" duration=5
.\hobl.cmd -p $ARGS[0] -s teams2_1on1_audio global:run_type=Power global:tools="+power_light" duration=5
.\hobl.cmd -p $ARGS[0] -s teams2_idle global:run_type=Power global:tools="+power_light" duration=5

.\hobl.cmd -p $ARGS[0] -s idle_desktop global:run_type=ETL global:tools="+power_heavy" duration=120

# .\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s study_report global:run_type=Misc

