if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}

.\hobl.cmd -p $ARGS[0] -s netflix_chrome        global:training_mode=1
.\hobl.cmd -p $ARGS[0] -s netflix_edgechromium  global:training_mode=1
.\hobl.cmd -p $ARGS[0] -s netflix               global:training_mode=1
.\hobl.cmd -p $ARGS[0] -s youtube_chrome        global:training_mode=1
.\hobl.cmd -p $ARGS[0] -s youtube_edgechromium  global:training_mode=1
.\hobl.cmd -p $ARGS[0] -s youtube               global:training_mode=1

.\hobl.cmd -p $ARGS[0] -s process_idle_tasks            global:post_run_delay=600
.\hobl.cmd -p $ARGS[0] -s charge_off
# .\hobl.cmd -p $ARGS[0] -s config_check

.\hobl.cmd -p $ARGS[0] -s netflix_chrome        global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s netflix_edgechromium  global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s netflix               global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s netflix_chrome        global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s netflix_edgechromium  global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s netflix               global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s netflix_chrome        global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s netflix_edgechromium  global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s netflix               global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s youtube_chrome        global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s youtube_edgechromium  global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s youtube               global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s youtube_chrome        global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s youtube_edgechromium  global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s youtube               global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s youtube_chrome        global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s youtube_edgechromium  global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s youtube               global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s netflix_edgechromium  global:run_type=Trace global:training_mode=1 netflix:duration=300
.\hobl.cmd -p $ARGS[0] -s netflix               global:run_type=Trace global:training_mode=1 youtube:duration=300
.\hobl.cmd -p $ARGS[0] -s youtube_edgechromium  global:run_type=Trace global:training_mode=1 youtube:duration=300
.\hobl.cmd -p $ARGS[0] -s netflix_edgechromium  global:run_type=Trace netflix_edgechromium:trace_provider=full_th.wprp
.\hobl.cmd -p $ARGS[0] -s netflix               global:run_type=Trace youtube:trace_provider=full_th.wprp
.\hobl.cmd -p $ARGS[0] -s youtube_edgechromium  global:run_type=Trace youtube_edgechromium:trace_provider=multimedia.wprp

.\hobl.cmd -p $ARGS[0] -s charge_on
.\hobl.cmd -p $ARGS[0] -s study_report 
