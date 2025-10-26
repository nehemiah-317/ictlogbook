from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils import timezone
from .models import VendorAssistance
from .forms import VendorAssistanceForm


class VendorAssistanceModelTest(TestCase):
    """Test suite for VendorAssistance model"""
    
    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
    def test_create_vendor_assistance(self):
        """Test creating a vendor assistance record"""
        record = VendorAssistance.objects.create(
            company_name="ABC Company",
            cashier_owner_name="John Doe",
            problem_reported="POS not working",
            phone_number="0123456789",
            status=VendorAssistance.PENDING,
            resolved_by=self.user,
            resolution_notes="Will check tomorrow"
        )
        
        self.assertEqual(record.company_name, "ABC Company")
        self.assertEqual(record.status, VendorAssistance.PENDING)
        self.assertEqual(record.resolved_by, self.user)
        self.assertIsNotNone(record.timestamp)
        self.assertIsNone(record.resolved_at)
        
    def test_vendor_assistance_str(self):
        """Test string representation"""
        record = VendorAssistance.objects.create(
            company_name="XYZ Corp",
            cashier_owner_name="Jane Smith",
            problem_reported="Network connectivity issues with the payment terminal",
            phone_number="0987654321",
            resolved_by=self.user,
            status=VendorAssistance.ONGOING
        )
        
        expected = f"XYZ Corp - Network connectivity issues with the payment ter ({VendorAssistance.ONGOING})"
        self.assertEqual(str(record), expected)
        
    def test_status_choices(self):
        """Test that status field accepts valid choices"""
        for status_value, _ in VendorAssistance.STATUS_CHOICES:
            record = VendorAssistance.objects.create(
                company_name="Test Company",
                cashier_owner_name="Test Owner",
                problem_reported="Test issue",
                phone_number="1234567890",
                resolved_by=self.user,
                status=status_value
            )
            self.assertEqual(record.status, status_value)
            
    def test_auto_set_resolved_at(self):
        """Test that resolved_at is auto-set when status changes to RESOLVED"""
        record = VendorAssistance.objects.create(
            company_name="Test Company",
            cashier_owner_name="Test Owner",
            problem_reported="Test issue",
            phone_number="1234567890",
            resolved_by=self.user,
            status=VendorAssistance.PENDING
        )
        
        # Initially resolved_at should be None
        self.assertIsNone(record.resolved_at)
        
        # Change status to RESOLVED
        record.status = VendorAssistance.RESOLVED
        record.save()
        
        # Now resolved_at should be set
        self.assertIsNotNone(record.resolved_at)


class VendorAssistanceFormTest(TestCase):
    """Test suite for VendorAssistanceForm"""
    
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'company_name': 'ABC Company',
            'cashier_owner_name': 'John Doe',
            'problem_reported': 'POS issue',
            'phone_number': '0123456789',
            'status': VendorAssistance.PENDING,
            'resolution_notes': 'In progress'
        }
        form = VendorAssistanceForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_missing_required_field(self):
        """Test form with missing required field"""
        form_data = {
            'company_name': 'ABC Company',
            # cashier_owner_name missing
            'problem_reported': 'POS issue',
            'phone_number': '0123456789',
        }
        form = VendorAssistanceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cashier_owner_name', form.errors)
        
    def test_empty_form(self):
        """Test form with no data"""
        form = VendorAssistanceForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = ['company_name', 'cashier_owner_name', 'problem_reported', 'phone_number']
        for field in required_fields:
            self.assertIn(field, form.errors)


class VendorAssistanceViewTest(TestCase):
    """Test suite for VendorAssistance views"""
    
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
        self.staff_record = VendorAssistance.objects.create(
            company_name="Staff Company",
            cashier_owner_name="Staff Contact",
            problem_reported="Issue 1",
            phone_number="0123456789",
            resolved_by=self.staff_user
        )
        
        self.other_record = VendorAssistance.objects.create(
            company_name="Other Company",
            cashier_owner_name="Other Contact",
            problem_reported="Issue 2",
            phone_number="0987654321",
            resolved_by=self.other_staff
        )
        
        self.client = Client()
        
    def test_list_view_requires_login(self):
        """Test that list view redirects unauthenticated users"""
        response = self.client.get(reverse('vendor_assistance:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        
    def test_admin_sees_all_records(self):
        """Test that admin users see all records"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('vendor_assistance:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['records']), 2)
        
    def test_staff_sees_own_records_only(self):
        """Test that staff users only see their own records"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('vendor_assistance:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['records']), 1)
        self.assertEqual(response.context['records'][0], self.staff_record)
        
    def test_create_view_get(self):
        """Test GET request to create view"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('vendor_assistance:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], VendorAssistanceForm)
        
    def test_create_view_post_valid(self):
        """Test POST request with valid data"""
        self.client.login(username='staff', password='staff123')
        form_data = {
            'company_name': 'New Company',
            'cashier_owner_name': 'New Contact',
            'problem_reported': 'New issue',
            'phone_number': '1112223333',
            'status': VendorAssistance.PENDING,
            'resolution_notes': 'Test'
        }
        response = self.client.post(reverse('vendor_assistance:create'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(VendorAssistance.objects.filter(company_name='New Company').exists())
        
    def test_detail_view(self):
        """Test detail view for a record"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('vendor_assistance:detail', args=[self.staff_record.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['record'], self.staff_record)
        
    def test_update_view(self):
        """Test update view"""
        self.client.login(username='staff', password='staff123')
        form_data = {
            'company_name': 'Updated Company',
            'cashier_owner_name': self.staff_record.cashier_owner_name,
            'problem_reported': 'Updated issue',
            'phone_number': self.staff_record.phone_number,
            'status': VendorAssistance.RESOLVED,
            'resolution_notes': 'Fixed'
        }
        response = self.client.post(
            reverse('vendor_assistance:update', args=[self.staff_record.pk]),
            data=form_data
        )
        self.assertEqual(response.status_code, 302)
        self.staff_record.refresh_from_db()
        self.assertEqual(self.staff_record.company_name, 'Updated Company')
        self.assertEqual(self.staff_record.status, VendorAssistance.RESOLVED)
        
    def test_delete_view(self):
        """Test delete view (admin only)"""
        self.client.login(username='admin', password='admin123')
        record_pk = self.staff_record.pk
        response = self.client.post(reverse('vendor_assistance:delete', args=[record_pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(VendorAssistance.objects.filter(pk=record_pk).exists())
        
    def test_staff_cannot_edit_others_records(self):
        """Test that staff cannot edit records from other staff members"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(reverse('vendor_assistance:update', args=[self.other_record.pk]))
        self.assertIn(response.status_code, [302, 403])


class VendorAssistancePermissionTest(TestCase):
    """Test suite for permissions"""
    
    def setUp(self):
        """Set up test users and records"""
        self.staff_group = Group.objects.create(name='ICT Staff')
        
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user1.groups.add(self.staff_group)
        
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.user2.groups.add(self.staff_group)
        
        self.record1 = VendorAssistance.objects.create(
            company_name="User1 Company",
            cashier_owner_name="User1 Contact",
            problem_reported="Issue",
            phone_number="1234567890",
            resolved_by=self.user1
        )
        
        self.client = Client()
        
    def test_user_cannot_view_other_users_record_detail(self):
        """Test that users cannot view detail of other users' records"""
        self.client.login(username='user2', password='pass123')
        response = self.client.get(reverse('vendor_assistance:detail', args=[self.record1.pk]))
        self.assertIn(response.status_code, [302, 403])
