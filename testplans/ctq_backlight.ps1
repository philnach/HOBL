if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s process_idle_tasks global:study_type=CTQ_Brightness global:run_type=Power global:post_run_delay=600
# .\hobl.cmd -p $ARGS[0] -s config_check global:study_type=CTQ_Brightness
.\hobl.cmd -p $ARGS[0] -s charge_off global:study_type=CTQ_Brightness global:run_type=Misc global:post_run_delay=300

.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=5
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=10
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=25
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=50
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=75
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=100

.\hobl.cmd -p $ARGS[0] -s charge_on global:study_type=CTQ_Brightness global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s study_report global:study_type=CTQ_Brightness global:run_type=Misc