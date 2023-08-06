#! /bin/sh

reg_status=`dbus-send --system --print-reply --dest=com.nokia.phone.net /com/nokia/phone/net Phone.Net.get_registration_status | awk 'NR==5 || NR==6 {print $2}'`
echo $reg_status
