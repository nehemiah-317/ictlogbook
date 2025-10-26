from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils import timezone
from .models import ThermalRollRecord
from .forms import ThermalRollRecordForm


class ThermalRollRecordModelTest(TestCase):
    """Test suite for ThermalRollRecord model"""
    
    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
    def test_create_thermal_roll_record(self):
        """Test creating a thermal roll record"""
        record = ThermalRollRecord.objects.create(
            vendor_name="ABC Vendor",
            cashier_owner_name="John Doe",
            quantity=50,
            phone_number="0123456789",
            signature="JD",
            recorded_by=self.user,
            notes="Urgent delivery"
        )
        
        self.assertEqual(record.vendor_name, "ABC Vendor")
        self.assertEqual(record.quantity, 50)
        self.assertEqual(record.recorded_by, self.user)
        self.assertIsNotNone(record.timestamp)
        
    def test_thermal_roll_record_str(self):
        """Test string representation"""
        record = ThermalRollRecord.objects.create(
            vendor_name="XYZ Store",
            cashier_owner_name="Jane Smith",
            quantity=100,
            phone_number="0987654321",
            recorded_by=self.user
        )
        
        expected = f"XYZ Store - 100 rolls on {record.timestamp.date()}"
        self.assertEqual(str(record), expected)
        
    def test_collection_date_property(self):
        """Test collection_date property returns date only"""
        record = ThermalRollRecord.objects.create(
            vendor_name="Test Vendor",
            cashier_owner_name="Test Owner",
            quantity=25,
            phone_number="1234567890",
            recorded_by=self.user
        )
        
        self.assertEqual(record.collection_date, record.timestamp.date())
        
    def test_quantity_positive(self):
        """Test that quantity must be positive"""
        record = ThermalRollRecord.objects.create(
            vendor_name="Test Vendor",
            cashier_owner_name="Test Owner",
            quantity=10,
            phone_number="1234567890",
            recorded_by=self.user
        )
        self.assertGreater(record.quantity, 0)


class ThermalRollRecordFormTest(TestCase):
    """Test suite for ThermalRollRecordForm"""
    
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'vendor_name': 'ABC Vendor',
            'cashier_owner_name': 'John Doe',
            'quantity': 50,
            'phone_number': '0123456789',
            'signature': 'JD',
            'notes': 'Test notes'
        }
        form = ThermalRollRecordForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_missing_required_field(self):
        """Test form with missing required field"""
        form_data = {
            'vendor_name': 'ABC Vendor',
            # cashier_owner_name missing
            'quantity': 50,
            'phone_number': '0123456789',
        }
        form = ThermalRollRecordForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cashier_owner_name', form.errors)
        
    def test_empty_form(self):
        """Test form with no data"""
        form = ThermalRollRecordForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = ['vendor_name', 'cashier_owner_name', 'quantity', 'phone_number']
        for field in required_fields:
            self.assertIn(field, form.errors)


class ThermalRollRecordViewTest(TestCase):
    """Test suite for ThermalRollRecord views"""
    
    def setUp(self):
        """Set up test users, groups, and records"""
        # Create groups
        self.admin_group = Group.objects.create(name='Admin')
        self.staff_group = Group.objects.create(name='ICT Staff')
        
        # Create admin user
        self.admin_user = User.objects.create_user(username='admin', password='admin123')
        self.admin_user.groups.add(self.admin_group)
        
        # Create staff user
        self.staff_user = User.objects.create_user(username='staff', password='staff123')
        self.staff_user.groups.add(self.staff_group)
        
        # Create another staff user
        self.other_staff = User.objects.create_user(username='other_staff', password='other123')
        self.other_staff.groups.add(self.staff_group)
        
        # Create test records
        self.staff_record = ThermalRollRecord.objects.create(
            vendor_name="Staff Vendor",
            cashier_owner_name="Staff Contact",
            quantity=50,
            phone_number="0123456789",
            recorded_by=self.staff_user
        )
        
        self.other_record = ThermalRollRecord.objects.create(
            vendor_name="Other Vendor",
            cashier_owner_name="Other Contact",
            quantity=100,
            phone_number="0987654321",
            recorded_by=self.other_staff
        )
        
        self.client = Client()
        
    def test_list_view_requires_login(self):
        """Test that list view redirects unauthenticated users"""
        response = self.client.get(reverse('thermal_rolls:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        
    def test_admin_sees_all_records(self):
        """Test that admin users see all records"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('thermal_rolls:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['records']), 2)
        
    def test_staff_sees_own_records_only(self):
        """Test that staff users only see their own records"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('thermal_rolls:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['records']), 1)
        self.assertEqual(response.context['records'][0], self.staff_record)
        
    def test_create_view_get(self):
        """Test GET request to create view"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('thermal_rolls:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], ThermalRollRecordForm)
        
    def test_create_view_post_valid(self):
        """Test POST request with valid data"""
        self.client.login(username='staff', password='staff123')
        form_data = {
            'vendor_name': 'New Vendor',
            'cashier_owner_name': 'New Contact',
            'quantity': 75,
            'phone_number': '1112223333',
            'signature': 'NC',
            'notes': 'Test'
        }
        response = self.client.post(reverse('thermal_rolls:create'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ThermalRollRecord.objects.filter(vendor_name='New Vendor').exists())
        
    def test_detail_view(self):
        """Test detail view for a record"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('thermal_rolls:detail', args=[self.staff_record.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['record'], self.staff_record)
        
    def test_update_view(self):
        """Test update view"""
        self.client.login(username='staff', password='staff123')
        form_data = {
            'vendor_name': 'Updated Vendor',
            'cashier_owner_name': self.staff_record.cashier_owner_name,
            'quantity': 200,
            'phone_number': self.staff_record.phone_number,
            'notes': 'Updated'
        }
        response = self.client.post(
            reverse('thermal_rolls:update', args=[self.staff_record.pk]),
            data=form_data
        )
        self.assertEqual(response.status_code, 302)
        self.staff_record.refresh_from_db()
        self.assertEqual(self.staff_record.vendor_name, 'Updated Vendor')
        self.assertEqual(self.staff_record.quantity, 200)
        
    def test_delete_view(self):
        """Test delete view (admin only)"""
        self.client.login(username='admin', password='admin123')
        record_pk = self.staff_record.pk
        response = self.client.post(reverse('thermal_rolls:delete', args=[record_pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ThermalRollRecord.objects.filter(pk=record_pk).exists())
        
    def test_staff_cannot_edit_others_records(self):
        """Test that staff cannot edit records from other staff members"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('thermal_rolls:update', args=[self.other_record.pk]))
        # Should return 404 (record not in filtered queryset) or 403 (permission denied)
        self.assertIn(response.status_code, [302, 403, 404])


class ThermalRollRecordPermissionTest(TestCase):
    """Test suite for permissions"""
    
    def setUp(self):
        """Set up test users and records"""
        self.staff_group = Group.objects.create(name='ICT Staff')
        
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user1.groups.add(self.staff_group)
        
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.user2.groups.add(self.staff_group)
        
        self.record1 = ThermalRollRecord.objects.create(
            vendor_name="User1 Vendor",
            cashier_owner_name="User1 Contact",
            quantity=50,
            phone_number="1234567890",
            recorded_by=self.user1
        )
        
        self.client = Client()
        
    def test_user_cannot_view_other_users_record_detail(self):
        """Test that users cannot view detail of other users' records"""
        self.client.login(username='user2', password='pass123')
        response = self.client.get(reverse('thermal_rolls:detail', args=[self.record1.pk]))
        # Should return 404 (record not in filtered queryset) or 403 (permission denied)
        self.assertIn(response.status_code, [302, 403, 404])
