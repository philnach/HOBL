if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}

# .\hobl.cmd -p $ARGS[0] -s abl_web             global:training_mode=1 abl:web_workload=abl_recording global:web_replay_action=record global:web_replay_run=0
.\hobl.cmd -p $ARGS[0] -s wr_record_start     global:run_type=Misc global:web_replay_recording=abl
.\hobl.cmd -p $ARGS[0] -s abl_web             global:training_mode=1 abl:web_workload=abl_record global:web_replay_action=record abl:training_module=abl
.\hobl.cmd -p $ARGS[0] -s wr_record_stop      global:run_type=Misc
