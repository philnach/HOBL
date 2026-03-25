if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s youtube_training global:prep_tools="+live_translation" global:module_name="youtube_lt" global:attempts=2 global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s recall_training global:attempts=2 global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s copilot_training global:attempts=2 global:post_run_delay=0