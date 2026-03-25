if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}

# .\hobl.cmd -p $ARGS[0] -s config_check

#MS Teams AC On power runs
# .\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc global:post_run_delay=300
# .\hobl.cmd -p $ARGS[0] -s teams2_3x3_video global:iterations=1 global:run_type=PMU global:module_name=t21_3x3_V_AC teams:new_teams=1 global:tools="+etl_trace" etl_trace:providers=pmu.wprp
# .\hobl.cmd -p $ARGS[0] -s teams2_1on1_video global:iterations=1 global:run_type=PMU global:module_name=t21_1x1_V_AC teams:new_teams=1 global:tools="+etl_trace" etl_trace:providers=pmu.wprp
# .\hobl.cmd -p $ARGS[0] -s teams2_1on1_audio global:iterations=1 global:run_type=PMU global:module_name=t21_1x1_A_AC teams:new_teams=1 global:tools="+etl_trace" etl_trace:providers=pmu.wprp

#MS Teams DC power runs
.\hobl.cmd -p $ARGS[0] -s charge_off global:run_type=Misc global:post_run_delay=300
.\hobl.cmd -p $ARGS[0] -s teams2_3x3_video global:iterations=1 global:run_type=PMU global:module_name=t21_3x3_V_DC teams:new_teams=1 global:tools="+etl_trace" etl_trace:providers=pmu.wprp
# .\hobl.cmd -p $ARGS[0] -s teams2_1on1_video global:iterations=1 global:run_type=PMU global:module_name=t21_1x1_V_DC teams:new_teams=1 global:tools="+etl_trace" etl_trace:providers=pmu.wprp
# .\hobl.cmd -p $ARGS[0] -s teams2_1on1_audio global:iterations=1 global:run_type=PMU global:module_name=t21_1x1_A_DC teams:new_teams=1 global:tools="+etl_trace" etl_trace:providers=pmu.wprp

.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s study_report global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s version_report global:run_type=Prep global:post_run_delay=0

