if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s system_prep global:run_type="Prep"
.\hobl.cmd -p $ARGS[0] -s store_prep global:run_type="Prep"
.\hobl.cmd -p $ARGS[0] -s lvp_prep global:run_type="Prep"
.\hobl.cmd -p $ARGS[0] -s button_install global:run_type="Prep"
.\hobl.cmd -p $ARGS[0] -s version_report global:run_type="Prep"
.\hobl.cmd -p $ARGS[0] -s process_idle_tasks process_idle_tasks:timeout=3600 process_idle_tasks:loops=1 global:run_type="Prep"
.\hobl.cmd -p $ARGS[0] -s reboot global:run_type="Prep"
.\hobl.cmd -p $ARGS[0] -s config_check_prep global:run_type="Prep"
