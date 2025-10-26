"""
Tests for Support Records module
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils import timezone
from .models import SupportRecord
from .forms import SupportRecordForm


class SupportRecordModelTest(TestCase):
    """Test cases for SupportRecord model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
    def test_create_support_record(self):
        """Test creating a support record"""
        record = SupportRecord.objects.create(
            staff_name="John Doe",
            staff_id="EMP001",
            phone_number="+1234567890",
            issue_reported="Computer not starting",
            status=SupportRecord.PENDING,
            recorded_by=self.user
        )
        self.assertEqual(record.staff_name, "John Doe")
        self.assertEqual(record.status, SupportRecord.PENDING)
        self.assertEqual(record.recorded_by, self.user)
        
    def test_support_record_str(self):
        """Test string representation"""
        record = SupportRecord.objects.create(
            staff_name="Jane Smith",
            staff_id="EMP002",
            phone_number="+1234567890",
            issue_reported="Printer issue",
            status=SupportRecord.PENDING,
            recorded_by=self.user
        )
        # String includes status in parentheses
        self.assertEqual(str(record), "Jane Smith - Printer issue (PENDING)")
        
    def test_status_choices(self):
        """Test status field choices"""
        record = SupportRecord.objects.create(
            staff_name="Test User",
            staff_id="EMP003",
            phone_number="+1234567890",
            issue_reported="Test issue",
            status=SupportRecord.IN_PROGRESS,
            recorded_by=self.user
        )
        self.assertIn(record.status, [SupportRecord.PENDING, SupportRecord.IN_PROGRESS, SupportRecord.SOLVED])
        
    def test_timestamp_auto_created(self):
        """Test that timestamp is automatically set"""
        record = SupportRecord.objects.create(
            staff_name="Test User",
            staff_id="EMP004",
            phone_number="+1234567890",
            issue_reported="Test issue",
            status=SupportRecord.PENDING,
            recorded_by=self.user
        )
        self.assertIsNotNone(record.timestamp)
        self.assertLessEqual(record.timestamp, timezone.now())


class SupportRecordFormTest(TestCase):
    """Test cases for SupportRecordForm"""
    
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'staff_name': 'John Doe',
            'staff_id': 'EMP001',
            'phone_number': '+1234567890',
            'issue_reported': 'Computer not working',
            'status': SupportRecord.PENDING
        }
        form = SupportRecordForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_missing_required_field(self):
        """Test form with missing required field"""
        form_data = {
            'staff_name': 'John Doe',
            'staff_id': 'EMP001',
            # Missing phone_number
            'issue_reported': 'Computer not working',
            'status': SupportRecord.PENDING
        }
        form = SupportRecordForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        
    def test_empty_form(self):
        """Test empty form"""
        form = SupportRecordForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 5)  # All fields are required


class SupportRecordViewTest(TestCase):
    """Test cases for Support Record views"""
    
    def setUp(self):
        """Set up test users and groups"""
        # Create groups (use 'Admin' not 'Admins' to match view logic)
        self.admin_group = Group.objects.create(name='Admin')
        self.staff_group = Group.objects.create(name='ICT Staff')
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        self.admin_user.groups.add(self.admin_group)
        
        # Create ICT staff user
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staff123',
            email='staff@example.com'
        )
        self.staff_user.groups.add(self.staff_group)
        
        # Create test records
        self.admin_record = SupportRecord.objects.create(
            staff_name="Admin Record",
            staff_id="EMP001",
            phone_number="+1234567890",
            issue_reported="Admin's issue",
            status=SupportRecord.PENDING,
            recorded_by=self.admin_user
        )
        
        self.staff_record = SupportRecord.objects.create(
            staff_name="Staff Record",
            staff_id="EMP002",
            phone_number="+1234567891",
            issue_reported="Staff's issue",
            status=SupportRecord.PENDING,
            recorded_by=self.staff_user
        )
        
        self.client = Client()
        
    def test_list_view_requires_login(self):
        """Test that list view requires authentication"""
        response = self.client.get(reverse('support_records:list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/accounts/login/', response.url)
        
    def test_admin_sees_all_records(self):
        """Test that admin can see all records"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('support_records:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['records']), 2)
        
    def test_staff_sees_own_records_only(self):
        """Test that ICT staff only sees their own records"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('support_records:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['records']), 1)
        self.assertEqual(response.context['records'][0].recorded_by, self.staff_user)
        
    def test_create_view_get(self):
        """Test GET request to create view"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('support_records:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'support_records/form.html')
        
    def test_create_view_post_valid(self):
        """Test POST request with valid data"""
        self.client.login(username='staff', password='staff123')
        data = {
            'staff_name': 'New User',
            'staff_id': 'EMP003',
            'phone_number': '+1234567892',
            'issue_reported': 'New issue',
            'status': SupportRecord.PENDING
        }
        response = self.client.post(reverse('support_records:create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertEqual(SupportRecord.objects.count(), 3)
        
    def test_detail_view(self):
        """Test detail view"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('support_records:detail', args=[self.admin_record.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.admin_record.staff_name)
        
    def test_update_view(self):
        """Test update view"""
        self.client.login(username='staff', password='staff123')
        data = {
            'staff_name': 'Updated Name',
            'staff_id': 'EMP002',
            'phone_number': '+1234567891',
            'issue_reported': 'Updated issue',
            'status': SupportRecord.IN_PROGRESS
        }
        response = self.client.post(
            reverse('support_records:update', args=[self.staff_record.pk]),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.staff_record.refresh_from_db()
        self.assertEqual(self.staff_record.staff_name, 'Updated Name')
        self.assertEqual(self.staff_record.status, SupportRecord.IN_PROGRESS)
        
    def test_delete_view(self):
        """Test delete view (admin only)"""
        self.client.login(username='admin', password='admin123')  # Changed from staff to admin
        record_pk = self.staff_record.pk
        response = self.client.post(reverse('support_records:delete', args=[record_pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SupportRecord.objects.filter(pk=record_pk).exists())
        
    def test_staff_cannot_edit_others_records(self):
        """Test that staff cannot edit records created by others"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('support_records:update', args=[self.admin_record.pk]))
        # Should either redirect or show 404/403
        self.assertNotEqual(response.status_code, 200)


class SupportRecordPermissionTest(TestCase):
    """Test permission-based access control"""
    
    def setUp(self):
        """Set up test data"""
        self.staff_group = Group.objects.create(name='ICT Staff')
        
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.user1.groups.add(self.staff_group)
        
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123'
        )
        self.user2.groups.add(self.staff_group)
        
        self.record_user1 = SupportRecord.objects.create(
            staff_name="User 1 Record",
            staff_id="EMP001",
            phone_number="+1234567890",
            issue_reported="User 1 issue",
            status=SupportRecord.PENDING,
            recorded_by=self.user1
        )
        
        self.client = Client()
        
    def test_user_cannot_view_other_users_record_detail(self):
        """Test that users cannot view other users' record details"""
        self.client.login(username='user2', password='pass123')
        response = self.client.get(reverse('support_records:detail', args=[self.record_user1.pk]))
        # Should redirect or show error since user2 didn't create this record
        self.assertIn(response.status_code, [302, 403, 404])

