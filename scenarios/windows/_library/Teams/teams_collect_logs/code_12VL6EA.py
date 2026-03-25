import logging

def run(scenario):
    if scenario.platform.lower() == "w365":
        raise NotImplementedError("Not working on w365 yet.")
    else:
        scenario._copy_data_from_remote(scenario.result_dir + "\\MSTeamsLogs", source=scenario.dut_data_path + "\\MSTeamsLogs")