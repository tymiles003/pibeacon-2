#!/usr/bin/env bash

echo "Setting permission for hcitool, hciconfig and hcidump"

sudo setcap 'cap_net_raw,cap_net_admin+eip' `which hcitool`
sudo setcap 'cap_net_raw,cap_net_admin+eip' `which hciconfig`
sudo setcap 'cap_net_raw,cap_net_admin+eip' `which hcidump`

getcap `which hcitool`
getcap `which hciconfig`
getcap `which hcidump`

echo "Done!"
