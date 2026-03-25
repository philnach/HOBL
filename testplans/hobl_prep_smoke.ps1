if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s dut_setup global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s net_prep net_prep:connection=Wi-Fi global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s msa_prep global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s system_prep global:attempts=2 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s config_check_prep global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s store_prep global:attempts=2 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s edge_install global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s button_install global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s office_install global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s teams_install global:attempts=2 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s adaptive_color_disable global:attempts=2 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s process_idle_tasks global:run_type=Prep global:post_run_delay=0 daily_prep:run_idle_tasks=0
.\hobl.cmd -p $ARGS[0] -s onedrive_prep global:attempts=2 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s lvp_prep global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s cs_floor_prep global:run_type=Prep global:post_run_delay=0
# .\hobl.cmd -p $ARGS[0] -s config_check global:post_run_delay=0

.\hobl.cmd -p $ARGS[0] -s version_report global:run_type=Prep global:post_run_delay=0
