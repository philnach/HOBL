if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
# .\hobl.cmd -p $ARGS[0] -s config_check global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s charge_off global:run_type=Misc global:post_run_delay=60

.\hobl.cmd -p $ARGS[0] -s manual global:run_type=Power global:post_run_delay=0 manual:duration=180 global:module_name="Enter Name(Use Underscore)" global:iterations=1 global:attempts=1 global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc global:post_run_delay=0

# .\hobl.cmd -p $ARGS[0] -s reboot global:run_type="Prep" global:post_run_delay=120
# .\hobl.cmd -p $ARGS[0] -s study_report global:run_type=Misc
