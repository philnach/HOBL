if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
# .\hobl.cmd -p $ARGS[0] -s config_check
.\hobl.cmd -p $ARGS[0] -s charge_off global:run_type=Misc global:post_run_delay=60

.\hobl.cmd -p $ARGS[0] -s teams2_1on1_video global:iterations=3 global:attempts=2 global:run_type=NewTeamsAI global:tools="+power_light mep_toggle" global:module_name=baseline1x1 teams:new_teams=1

.\hobl.cmd -p $ARGS[0] -s teams2_1on1_video global:iterations=3 global:attempts=2 global:run_type=NewTeamsAI global:tools="+power_light mep_toggle" global:module_name=framing1x1 mep_toggle:framing=1 teams:new_teams=1

.\hobl.cmd -p $ARGS[0] -s teams2_1on1_video global:iterations=3 global:attempts=2 global:run_type=NewTeamsAI global:tools="+power_light mep_toggle" global:module_name=eyestandard1x1 mep_toggle:eye_gaze=1 mep_toggle:standardeye=1 teams:new_teams=1
.\hobl.cmd -p $ARGS[0] -s teams2_1on1_video global:iterations=3 global:attempts=2 global:run_type=NewTeamsAI global:tools="+power_light mep_toggle" global:module_name=eyeenhanced1x1 mep_toggle:eye_gaze=1 mep_toggle:enhancedeye=1 teams:new_teams=1

.\hobl.cmd -p $ARGS[0] -s teams2_1on1_video global:iterations=3 global:attempts=2 global:run_type=NewTeamsAI global:tools="+power_light mep_toggle" global:module_name=standardblur1x1 mep_toggle:blur=1 mep_toggle:standardblur=1 teams:new_teams=1
.\hobl.cmd -p $ARGS[0] -s teams2_1on1_video global:iterations=3 global:attempts=2 global:run_type=NewTeamsAI global:tools="+power_light mep_toggle" global:module_name=portraitblur1x1 mep_toggle:blur=1 mep_toggle:portraitblur=1 teams:new_teams=1

.\hobl.cmd -p $ARGS[0] -s teams2_1on1_video global:iterations=3 global:attempts=2 global:run_type=NewTeamsAI global:tools="+power_light mep_toggle" global:module_name=illustrated1x1 mep_toggle:creative=1 mep_toggle:illustrated=1 teams:new_teams=1
.\hobl.cmd -p $ARGS[0] -s teams2_1on1_video global:iterations=3 global:attempts=2 global:run_type=NewTeamsAI global:tools="+power_light mep_toggle" global:module_name=animated1x1 mep_toggle:creative=1 mep_toggle:animated=1 teams:new_teams=1
.\hobl.cmd -p $ARGS[0] -s teams2_1on1_video global:iterations=3 global:attempts=2 global:run_type=NewTeamsAI global:tools="+power_light mep_toggle" global:module_name=watercolor1x1 mep_toggle:creative=1 mep_toggle:watercolor=1 teams:new_teams=1

.\hobl.cmd -p $ARGS[0] -s teams2_1on1_video global:iterations=3 global:attempts=2 global:run_type=NewTeamsAI global:tools="+power_light mep_toggle" global:module_name=portraitlight1x1 mep_toggle:portraitlight=1 teams:new_teams=1

.\hobl.cmd -p $ARGS[0] -s teams2_1on1_video global:iterations=3 global:attempts=2 global:run_type=NewTeamsAI global:tools="+power_light mep_toggle" global:module_name=all1x1 mep_toggle:framing=1 mep_toggle:eye_gaze=1 mep_toggle:enhancedeye=1 mep_toggle:blur=1 mep_toggle:portraitblur=1 mep_toggle:portraitlight=1 mep_toggle:creative=1 mep_toggle:illustrated=1 teams:new_teams=1

.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s study_report global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s version_report global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s notify global:run_type=Misc

