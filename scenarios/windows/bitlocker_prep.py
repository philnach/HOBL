"""
//--------------------------------------------------------------
//
// HOBL
// Copyright(c) Microsoft Corporation
// All rights reserved.
//
// MIT License
//
// Permission is hereby granted, free of charge, to any person obtaining
// a copy of this software and associated documentation files(the ""Software""),
// to deal in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies
// of the Software, and to permit persons to whom the Software is furnished to do so,
// subject to the following conditions :
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
// FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE AUTHORS
// OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
// WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
// OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//
//--------------------------------------------------------------
"""

##
# Enable or disable bitlocker
##

import time
import logging
from core.parameters import Params
import core.app_scenario


class BitlockerPrep(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]

    # Set default parameters
    Params.setDefault(module, 'enable', '1')  # Set to 0 to disable bitlocker

    # Get parameters
    enable = Params.get(module, 'enable')

    is_prep = True


    def runTest(self):
        if self.enable == '1':
            # If already encrypted, exit
            if self.getStatus() == "FullyEncrypted":
                logging.info("Drive already encrypted, exiting")        
                self.createPrepStatusControlFile()
                return
            
            # Encrypt with TPM
            logging.info("Enabling drive encryption")        
            self._call(["powershell.exe", 'Enable-bitlocker -MountPoint "C:" -TpmProtector'])

            # Reboot to pass hardware check
            logging.info("Rebooting DUT for hardware check")        
            self._call(["shutdown.exe", "/r /f /t 5"])
            time.sleep(15)
            self._wait_for_dut_comm()

            # Wait until fully encrypted
            while(True):
                progress = self.getPercentage()
                logging.info(f"Encryption percentage: {progress}%")
                if progress == "100":
                    break
                else:    
                    time.sleep(30)   
            status =  self.getStatus()
            logging.info(f"Drive status: {status}")        
            if status != "FullyEncrypted":
                logging.error ("Drive encryption failed")
                self.fail("Drive encryption failed.")
            
            # Add recovery
            logging.info("Adding recovery: '111111-111111-111111-111111-111111-111111-111111-111111'")
            self._call(["powershell.exe", 'Add-BitLockerKeyProtector -MountPoint "C:" -RecoveryPasswordProtector -RecoveryPassword "111111-111111-111111-111111-111111-111111-111111-111111"'])

            self.createPrepStatusControlFile()

        else:
            # If already decrypted, exit
            if self.getStatus() == "FullyDecrypted":
                logging.info("Drive already decrypted, exiting")        
                self.createPrepStatusControlFile()
                return
            
            # Decrypt
            logging.info("Disabling drive encryption")        
            self._call(["powershell.exe", 'Disable-bitlocker -MountPoint "C:"'])

            # Wait until fully decrypted
            while(True):
                progress = self.getPercentage()
                logging.info(f"Encryption percentage: {progress}%")
                if progress == "0":
                    break
                else:    
                    time.sleep(30)   
            status =  self.getStatus()
            logging.info(f"Drive status: {status}")        
            if status != "FullyDecrypted":
                logging.error ("Drive decryption failed")
                self.fail("Drive decryption failed.")
            self.createPrepStatusControlFile()


    def getStatus(self):
        result = self._call(["powershell.exe", '(Get-BitLockerVolume -MountPoint "C:").VolumeStatus'])
        return result

    def getPercentage(self):
        result = self._call(["powershell.exe", '(Get-BitLockerVolume -MountPoint "C:").EncryptionPercentage'])
        return result

