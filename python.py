#!/usr/bin/python
#coding:utf-8

#this is a python exercise
import paramiko

print "input ip address："
connect_ip = raw_input()
print "login user："
user = raw_input()
print "password:"
passwd = raw_input()
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(connect_ip,22,user,passwd)
stdin,stdout,stderr = ssh.exec_command("source demo-openrc.sh;nova volume-list")
volumes_info =  stdout.readlines()
volumes = []
#volumes_id = []
#volumes_status = []
for data in volumes_info:
	if data.find('|') != -1:
		volumes.append(data.split("|"))
volumes.pop(0)
#for volume in volumes:
#	volumes_id.append(volume[1])
#	volumes_status.append(volume[2])
#for ids in volumes_id:
#	print ids
#for status in volumes_status:
#	print status
stdin,stdout,stderr = ssh.exec_command("source demo-openrc.sh;nova volume-snapshot-list")
snapshot_info = stdout.readlines()
snapshots = []
#snapshots_id = []
#snap_volume_id = []
#snapshots_status = []
for data in snapshot_info:
	if data.find('|')!= -1:
		snapshots.append(data.split("|"))
snapshots.pop(0)
#for snapshot in snapshots:
#	snapshots_id.append(snapshot[1])
#	snap_volume_id.append(snapshot[2])
#	snapshots_status.append(snapshot[3])
#for ids in snapshots_id:
#	print ids
#for di in snap_volume_id:
#	print di
#for status in snapshots_status:
#	print status
#
#for volume_id in volumes_id:
#	print volume_id
#	for snap_id in snap_volume_id:
#		if snap_id == volume_id:
#			print snap_id
#volumes_id.pop(0)
#snapshots_id.pop(0)
#snap_volume_id.pop(0)
#nvs = zip(snapshots_id,snap_volume_id)
#snapDict = dict((snapshots_id,snap_volume_id) for snapshots_id,snap_volume_id in nvs)
for volume in volumes:
	print "Volume", volume[1],volume[2]
	for snapshot in snapshots:
		if snapshot[2] == volume[1]:
			print "----Snapshot",snapshot[1],snapshot[3]
ssh.close()
