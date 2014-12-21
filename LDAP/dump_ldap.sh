#!/usr/bin/env bash

backup_dirs=("/etc/ldap/" "/var/lib/ldap/")
for dir in $backup_dirs; do
	if [ ! -d $dir ]; then
		echo "Cannot backup files that does not exist..." >&2
		echo "Missing at least: $dir"
		echo "OpenLDAP not installed?" >&1
		exit 1
	fi
done
date=$(date "+%F")
output_file="ldap_dump-$date.tar.gz"
sudo tar --exclude=backup -cPvzf $output_file ${backup_dirs[*]} 

echo "Created $output_file" >&2

