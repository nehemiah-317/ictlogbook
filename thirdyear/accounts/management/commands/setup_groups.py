from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Create default user groups (Admin and ICT Staff) for the ICT Work Record System'

    def handle(self, *args, **kwargs):
        # Create Admin group
        admin_group, created = Group.objects.get_or_create(name='Admin')
        if created:
            self.stdout.write(self.style.SUCCESS('Created "Admin" group'))
            
            # Admin gets all permissions
            permissions = Permission.objects.all()
            admin_group.permissions.set(permissions)
            self.stdout.write(self.style.SUCCESS(f'Assigned {permissions.count()} permissions to Admin group'))
        else:
            self.stdout.write(self.style.WARNING('"Admin" group already exists'))

        # Create ICT Staff group
        staff_group, created = Group.objects.get_or_create(name='ICT Staff')
        if created:
            self.stdout.write(self.style.SUCCESS('Created "ICT Staff" group'))
            
            # ICT Staff gets add/view permissions for records
            staff_permissions = Permission.objects.filter(
                codename__in=[
                    'add_supportrecord', 'view_supportrecord',
                    'add_assetrecord', 'view_assetrecord',
                    'add_vendorassistance', 'view_vendorassistance',
                    'add_thermalrollrecord', 'view_thermalrollrecord',
                ]
            )
            staff_group.permissions.set(staff_permissions)
            self.stdout.write(self.style.SUCCESS(f'Assigned {staff_permissions.count()} permissions to ICT Staff group'))
        else:
            self.stdout.write(self.style.WARNING('"ICT Staff" group already exists'))

        self.stdout.write(self.style.SUCCESS('\nGroups setup completed successfully!'))
        self.stdout.write(self.style.SUCCESS('\nYou can now assign users to these groups via the Django admin panel.'))
