if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s timer global:run_type=Power
.\hobl.cmd -p $ARGS[0] -s timer global:run_type=Power
.\hobl.cmd -p $ARGS[0] -s test_fail global:run_type=Power
.\hobl.cmd -p $ARGS[0] -s timer global:run_type=Power
.\hobl.cmd -p $ARGS[0] -s notify global:run_type=Misc
