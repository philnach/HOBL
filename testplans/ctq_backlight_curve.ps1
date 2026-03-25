if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s process_idle_tasks global:study_type=CTQ_Brightness global:run_type=Power global:delay_between_runs=600
.\hobl.cmd -p $ARGS[0] -s config_check global:study_type=CTQ_Brightness
.\hobl.cmd -p $ARGS[0] -s charge_off global:study_type=CTQ_Brightness global:run_type=Misc global:delay_between_runs=300

.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=0 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=5 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=10 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=18 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=24 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=36 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=44 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=50 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=56 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=61 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=65 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=69 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=72 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=76 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=79 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=82 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=84 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=87 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=89 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=92 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=94 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=96 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=98 timer:duration=60
.\hobl.cmd -p $ARGS[0] -s timer global:study_type=CTQ_Brightness global:run_type=Power display_brightness:brightness=100 timer:duration=60

.\hobl.cmd -p $ARGS[0] -s charge_on global:study_type=CTQ_Brightness global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s study_report global:study_type=CTQ_Brightness global:run_type=Misc