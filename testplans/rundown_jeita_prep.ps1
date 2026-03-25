if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s net_prep global:attempts=2 net_prep:connection=Wi-Fi global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s os_install global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s wifi_switch global:run_type=Misc global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s version_report global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s config_check_prep global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s store_prep global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s adaptive_color_disable global:attempts=2 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s surface_app_prep global:attempts=2 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s clipboard_suggestions_disable global:attempts=2 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s reboot global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s lvp_jeita_prep global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s system_prep global:run_type=Prep global:post_run_delay=0 system_prep:wallpaper=JB3_0-IMAGE.jpg
.\hobl.cmd -p $ARGS[0] -s config_check global:attempts=2 global:post_run_delay=0
