import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# TURN OFF DEBUG TOOLBAR
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions"""
        db.session.rollback()

    def test_see_followers_logged_in(self):
        """Can a logged in user see followers of any user?"""

        user2 = User.query.filter_by(username="testuser2").first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{user2.id}/followers")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="row">', html)

    def test_see_following_logged_in(self):
        """Can a logged in user see who other users follow?"""

        user2 = User.query.filter_by(username="testuser2").first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{user2.id}/following")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="row">', html)

# ##################
# logged out tests

    def test_see_followers_logged_out(self):
        """Can a logged out user see followers of any user?"""

        user2 = User.query.filter_by(username="testuser2").first()

        with self.client as c:

            resp = c.get(f"/users/{user2.id}/followers", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in to see who follows', html)

    def test_see_following_logged_out(self):
        """Can a logged out user see who a user follows?"""

        user2 = User.query.filter_by(username="testuser2").first()

        with self.client as c:

            resp = c.get(f"/users/{user2.id}/following", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in to see who', html)

    def test_see_user_detail_logged_out(self):
        """Can a logged out user see a user?"""

        user2 = User.query.filter_by(username="testuser2").first()

        with self.client as c:

            resp = c.get(f"/users/{user2.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4 id="sidebar-username">', html)