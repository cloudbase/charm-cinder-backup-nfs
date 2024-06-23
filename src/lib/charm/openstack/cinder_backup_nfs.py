
from charmhelpers.core.hookenv import (
    config,
    status_set
)
from charmhelpers.core.host import install_ca_cert
from base64 import b64decode

from charmhelpers.contrib.openstack.context import OSContextGenerator
from charmhelpers.contrib.openstack.utils import get_os_codename_package,\
    CompareOpenStackReleases
from charms_openstack.charm import OpenStackCharm


class CinderBackupNFSCharm(OpenStackCharm):
    name = 'cinder-backup-nfs'
    packages = ['cinder-backup']
    release = 'yoga'

    def get_nfs_backup_config(self):
        ctx = NFSBackupSubordinateContext()()
        if not ctx:
            return None, None
        status_set('active', 'Unit is ready')
        name = "cinder-backup"
        return name, NFSBackupSubordinateContext()()

    def configure_ca(self):
        ca_cert = config('ssl-ca')
        if ca_cert:
            install_ca_cert(b64decode(ca_cert))


class NFSBackupSubordinateContext(OSContextGenerator):
    interfaces = ['backup-backend']

    def __call__(self):
        """Used to generate template context to be added to cinder.conf.
        """

        release = get_os_codename_package('cinder-common')
        if CompareOpenStackReleases(release) < "yoga":
            raise Exception("Unsupported version of Openstack %s (minimum yoga)" % release)

        backup_share = config('backup-share')
        if backup_share is None or backup_share == '':
            status_set('blocked', 'Missing config: backup-share')
            return {}

        backup_container = config('backup-container')
        backup_mount_options = config('backup-mount-options')

        ctxt = [
            ('backup_driver', 'cinder.backup.drivers.nfs.NFSBackupDriver'),
            ('backup_enable_progress_timer', config('backup-enable-progress-timer')),
            ('backup_file_size', config('backup-file-size')),
            ('backup_mount_attempts', config('backup-mount-attempts')),
            ('backup_mount_point_base', config('backup-mount-point-base')),
            ('backup_posix_path', config('backup-posix-path')),
            ('backup_sha_block_size_bytes', config('backup-sha-block-size-bytes')),
            ('backup_share', config('backup-share'))
        ]

        if backup_container:
            ctxt.append(('backup_container', backup_container))
        
        if backup_mount_options:
            ctxt.append(('backup_mount_options', backup_mount_options))

        return {
            "cinder": {
                "/etc/cinder/cinder.conf": {
                    "sections": {
                        'DEFAULT': ctxt
                    }
                }
            }
        }
