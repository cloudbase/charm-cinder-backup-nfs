# Cinder Backup to NFS

Build charm:

```bash
charmcraft pack
```

Deploy charm:

```bash
juju deploy ./cinder-backup-nfs_ubuntu-22.04-amd64.charm
```

Make sure you configure the `backup-share` option:

```bash
juju config cinder-backup-nfs backup-share=SERVER_IP:/path/to/backup/share
```

Add relation to cinder-backup-nfs:

```bash
juju relate cinder-backup-nfs:backup-backend cinder-backup:backup-backend
```