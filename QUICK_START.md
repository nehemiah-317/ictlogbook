# 🚀 Quick Start Guide

## Step 1: Create Superuser

Open terminal in the `thirdyear` directory and run:

```bash
python manage.py createsuperuser
```

Enter the following:
- Username: `admin`
- Email: `admin@ictlogbook.local`
- Password: (choose a strong password, e.g., `Admin@123`)
- Password confirmation: (same password)

## Step 2: Assign Admin to Admin Group

1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Open browser and go to: `http://127.0.0.1:8000/admin/`

3. Login with the superuser credentials you just created

4. Navigate to **Authentication and Authorization** → **Users**

5. Click on the **admin** user

6. Scroll down to **Groups** section

7. Select **Admin** from the "Available groups" and click the arrow to move it to "Chosen groups"

8. Click **Save** at the bottom

## Step 3: Test the Application

1. Logout from Django admin (click "LOG OUT" in top right)

2. Go to: `http://127.0.0.1:8000/`

3. You should see the login page

4. Login with your admin credentials

5. You should now see the **Dashboard** with:
   - Statistics cards showing 0 records (we haven't created any yet)
   - Quick action buttons (marked as "Coming Soon")
   - Your username and "Admin" badge in the navigation bar

## Step 4: Create Sample Data via Django Admin

1. Go back to: `http://127.0.0.1:8000/admin/`

2. Create some test records in each module:

   **Support Records:**
   - Click "Support Records" → "Add Support Record"
   - Fill in the details (Staff name, ID, Issue, Phone, Status)
   - The "Recorded by" will be auto-set to you
   - Click "Save"

   **Asset Records:**
   - Click "Asset Records" → "Add Asset Record"
   - Fill in staff details and asset information
   - Click "Save"

   **Vendor Assistance:**
   - Click "Vendor Assistance Records" → "Add Vendor Assistance Record"
   - Fill in vendor and problem details
   - Click "Save"

   **Thermal Roll Records:**
   - Click "Thermal Roll Records" → "Add Thermal Roll Record"
   - Fill in vendor name and quantity
   - Click "Save"

3. Go back to the main dashboard: `http://127.0.0.1:8000/`

4. You should now see the counts updated on the dashboard!

## Step 5: Create an ICT Staff User (Optional)

1. In Django admin, go to **Users** → **Add User**

2. Create a new user (e.g., username: `john_ict`, password: `Test@123`)

3. Click "Save and continue editing"

4. Scroll down to **Groups**

5. Select **ICT Staff** from available groups

6. Add their first name and last name

7. Click "Save"

8. Logout and login as this new user

9. You'll see they can only view their own records in the admin panel

## Step 6: Explore Features

### As Admin:
- ✅ View all records from all users
- ✅ Full CRUD access in Django admin
- ✅ See total counts on dashboard

### As ICT Staff:
- ✅ View only their own records
- ✅ Create new records
- ✅ See only their counts on dashboard

## Common Issues

### Issue 1: "No module named 'accounts'"
**Solution:** Make sure you're in the `thirdyear` directory when running commands

### Issue 2: Login redirects to admin instead of dashboard
**Solution:** Clear your browser cookies or use incognito mode

### Issue 3: Groups don't exist
**Solution:** Run: `python manage.py setup_groups`

### Issue 4: Database errors
**Solution:** Delete `db.sqlite3` and run:
```bash
python manage.py migrate
python manage.py setup_groups
python manage.py createsuperuser
```

## Next Steps

Once you've tested the basic functionality, we'll implement:
- ✨ CRUD views with forms for the frontend
- ✨ List/detail pages for each module
- ✨ Advanced dashboard with charts
- ✨ Export functionality
- ✨ Search and filtering UI

## URLs Currently Available

- `/` - Dashboard (requires login)
- `/accounts/login/` - Login page
- `/accounts/logout/` - Logout
- `/accounts/profile/` - User profile
- `/admin/` - Django admin panel

Enjoy testing! 🎉
