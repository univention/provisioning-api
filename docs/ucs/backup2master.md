
To run `backup2master`, will be done automatically when the backup2master script is executed, if this MR is merged:
https://git.knut.univention.de/univention/dev/ucs/-/merge_requests/1656
or manually as follows:

> /usr/lib/univention-backup2master/post/provisioning-service-backup2master.sh

This will automatically install provisioning-service-backend on the new master and reinitialize the provisioning-service app.

# Other systems
For other backups follow this article (specifically `ldap/master` need to be correct):
* https://help.univention.com/t/how-to-backup2master/19514

* On all remaing backup directory nodes run
`univention-app reinitialize provisioning-service`


* All provisioning consumers need to be restarted as well (they usually just terminate and in k8s that's enough to trigger the automatic restart, but not in UCS).