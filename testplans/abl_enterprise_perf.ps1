if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s utc_prep global:run_type=Prep global:post_run_delay=600
.\hobl.cmd -p $ARGS[0] -s charge_off global:run_type=Misc global:post_run_delay=300
.\hobl.cmd -p $ARGS[0] -s abl_enterprise_web global:iterations=1  global:run_type=Perf global:tools="+perf_utc mep_toggle" abl_enterprise:background_timers=1 abl_enterprise:background_onedrive_copy=1 abl_enterprise:background_teams=1 abl_enterprise:simple_office_launch=1 mep_toggle:blur=1 mep_toggle:standardblur=1
.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s utc_prep global:run_type=Prep utc_prep:enable=0
