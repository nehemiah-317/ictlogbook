from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils import timezone
from .models import AssetRecord
from .forms import AssetRecordForm


class AssetRecordModelTest(TestCase):
    """Test suite for AssetRecord model"""
    
    def setUp(self):
        """Create test user and sample record"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
    def test_create_asset_record(self):
        """Test creating an asset record with all fields"""
        record = AssetRecord.objects.create(
            staff_name="John Doe",
            staff_id="STF001",
            problem_reported="Laptop overheating",
            asset_type="Laptop",
            division="IT Department",
            phone_number="0123456789",
            signature="JD",
            status=AssetRecord.IN_USE,
            recorded_by=self.user,
            notes="Urgent repair needed"
        )
        
        self.assertEqual(record.staff_name, "John Doe")
        self.assertEqual(record.status, AssetRecord.IN_USE)
        self.assertEqual(record.recorded_by, self.user)
        self.assertIsNotNone(record.timestamp)
        self.assertIsNone(record.returned_at)
        
    def test_asset_record_str(self):
        """Test string representation of asset record"""
        record = AssetRecord.objects.create(
            staff_name="Jane Smith",
            staff_id="STF002",
            problem_reported="Desktop not booting",
            asset_type="Desktop PC",
            division="HR",
            phone_number="0987654321",
            recorded_by=self.user,
            status=AssetRecord.IN_USE
        )
        
        expected = f"Jane Smith - Desktop PC ({AssetRecord.IN_USE})"
        self.assertEqual(str(record), expected)
        
    def test_status_choices(self):
        """Test that status field accepts valid choices"""
        for status_value, _ in AssetRecord.STATUS_CHOICES:
            record = AssetRecord.objects.create(
                staff_name="Test User",
                staff_id="TEST001",
                problem_reported="Test issue",
                asset_type="Test Asset",
                division="Test Div",
                phone_number="1234567890",
                recorded_by=self.user,
                status=status_value
            )
            self.assertEqual(record.status, status_value)
            
    def test_auto_set_returned_at(self):
        """Test that returned_at is auto-set when status changes to RETURNED"""
        record = AssetRecord.objects.create(
            staff_name="Test User",
            staff_id="TEST001",
            problem_reported="Test issue",
            asset_type="Test Asset",
            division="Test Div",
            phone_number="1234567890",
            recorded_by=self.user,
            status=AssetRecord.IN_USE
        )
        
        # Initially returned_at should be None
        self.assertIsNone(record.returned_at)
        
        # Change status to RETURNED
        record.status = AssetRecord.RETURNED
        record.save()
        
        # Now returned_at should be set
        self.assertIsNotNone(record.returned_at)


class AssetRecordFormTest(TestCase):
    """Test suite for AssetRecordForm"""
    
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'staff_name': 'John Doe',
            'staff_id': 'STF001',
            'problem_reported': 'Laptop issue',
            'asset_type': 'Laptop',
            'division': 'IT',
            'phone_number': '0123456789',
            'signature': 'JD',
            'status': AssetRecord.IN_USE,
            'notes': 'Test notes'
        }
        form = AssetRecordForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_missing_required_field(self):
        """Test form with missing required field"""
        form_data = {
            'staff_name': 'John Doe',
            # staff_id missing
            'problem_reported': 'Laptop issue',
            'asset_type': 'Laptop',
            'division': 'IT',
            'phone_number': '0123456789',
        }
        form = AssetRecordForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('staff_id', form.errors)
        
    def test_empty_form(self):
        """Test form with no data"""
        form = AssetRecordForm(data={})
        self.assertFalse(form.is_valid())
        # Check that required fields have errors
        required_fields = ['staff_name', 'staff_id', 'problem_reported', 'asset_type', 'division', 'phone_number']
        for field in required_fields:
            self.assertIn(field, form.errors)


class AssetRecordViewTest(TestCase):
    """Test suite for AssetRecord views"""
    
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
        self.staff_record = AssetRecord.objects.create(
            staff_name="Staff Record",
            staff_id="STF001",
            problem_reported="Issue 1",
            asset_type="Laptop",
            division="IT",
            phone_number="0123456789",
            recorded_by=self.staff_user
        )
        
        self.other_record = AssetRecord.objects.create(
            staff_name="Other Record",
            staff_id="STF002",
            problem_reported="Issue 2",
            asset_type="Desktop",
            division="HR",
            phone_number="0987654321",
            recorded_by=self.other_staff
        )
        
        self.client = Client()
        
    def test_list_view_requires_login(self):
        """Test that list view redirects unauthenticated users"""
        response = self.client.get(reverse('asset_management:list'))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertIn('/accounts/login/', response.url)
        
    def test_admin_sees_all_records(self):
        """Test that admin users see all records"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('asset_management:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['records']), 2)
        
    def test_staff_sees_own_records_only(self):
        """Test that staff users only see their own records"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('asset_management:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['records']), 1)
        self.assertEqual(response.context['records'][0], self.staff_record)
        
    def test_create_view_get(self):
        """Test GET request to create view"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('asset_management:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], AssetRecordForm)
        
    def test_create_view_post_valid(self):
        """Test POST request with valid data"""
        self.client.login(username='staff', password='staff123')
        form_data = {
            'staff_name': 'New Record',
            'staff_id': 'STF003',
            'problem_reported': 'New issue',
            'asset_type': 'Printer',
            'division': 'Finance',
            'phone_number': '1112223333',
            'signature': 'NR',
            'status': AssetRecord.IN_USE,
            'notes': 'Test'
        }
        response = self.client.post(reverse('asset_management:create'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(AssetRecord.objects.filter(staff_id='STF003').exists())
        
    def test_detail_view(self):
        """Test detail view for a record"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('asset_management:detail', args=[self.staff_record.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['record'], self.staff_record)
        
    def test_update_view(self):
        """Test update view"""
        self.client.login(username='staff', password='staff123')
        form_data = {
            'staff_name': 'Updated Name',
            'staff_id': self.staff_record.staff_id,
            'problem_reported': 'Updated issue',
            'asset_type': self.staff_record.asset_type,
            'division': self.staff_record.division,
            'phone_number': self.staff_record.phone_number,
            'status': AssetRecord.RETURNED,
            'notes': 'Updated'
        }
        response = self.client.post(
            reverse('asset_management:update', args=[self.staff_record.id]),
            data=form_data
        )
        self.assertEqual(response.status_code, 302)
        self.staff_record.refresh_from_db()
        self.assertEqual(self.staff_record.staff_name, 'Updated Name')
        self.assertEqual(self.staff_record.status, AssetRecord.RETURNED)
        
    def test_delete_view(self):
        """Test delete view (admin only)"""
        self.client.login(username='admin', password='admin123')
        record_id = self.staff_record.id
        response = self.client.post(reverse('asset_management:delete', args=[record_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(AssetRecord.objects.filter(id=record_id).exists())
        
    def test_staff_cannot_edit_others_records(self):
        """Test that staff cannot edit records from other staff members"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('asset_management:update', args=[self.other_record.id]))
        # Should return 404 (record not in filtered queryset) or 403 (permission denied)
        self.assertIn(response.status_code, [302, 403, 404])


class AssetRecordPermissionTest(TestCase):
    """Test suite for permissions"""
    
    def setUp(self):
        """Set up test users and records"""
        self.staff_group = Group.objects.create(name='ICT Staff')
        
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user1.groups.add(self.staff_group)
        
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.user2.groups.add(self.staff_group)
        
        self.record1 = AssetRecord.objects.create(
            staff_name="User1 Record",
            staff_id="U1001",
            problem_reported="Issue",
            asset_type="Laptop",
            division="IT",
            phone_number="1234567890",
            recorded_by=self.user1
        )
        
        self.client = Client()
        
    def test_user_cannot_view_other_users_record_detail(self):
        """Test that users cannot view detail of other users' records"""
        self.client.login(username='user2', password='pass123')
        response = self.client.get(reverse('asset_management:detail', args=[self.record1.id]))
        # Should return 404 (record not in filtered queryset) or 403 (permission denied)
        self.assertIn(response.status_code, [302, 403, 404])
