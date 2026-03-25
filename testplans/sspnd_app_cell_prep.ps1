if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}

.\hobl.cmd -p $ARGS[0] -s sspnd_app_cell_prep global:run_type=prep global:post_run_delay=0 global:scenarios_dir=.\android_scenarios

.\hobl.cmd -p $ARGS[0] -s manual_android global:run_type="Power" global:module_name="sspnd_app_cell_0s" global:attempts="1" global:scenarios_dir=.\android_scenarios manual_android:duration="3600" manual_android:delay="600" manual_android:status_prompt="1"

