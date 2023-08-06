#! /bin/bash
/usr/bin/wget -O - http://issuedealer.nidelven-it.no/issue_dealer/check_notifications
result=`echo $?`
exit $result
