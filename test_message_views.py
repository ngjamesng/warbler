"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


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


class MessageViewTestCase(TestCase):
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


    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_remove_message(self):
        """Can a user remove their own message? Assert YES"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})
            msg = Message.query.one()

            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects = True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(Message.query.all()), 0)

    def test_remove_other_user_msg(self):
        """Can a user remove another user's message? Assert NO"""
        msg = Message(text="Removal Test", user_id=self.testuser.id)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2.id

            msg = Message.query.one()
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertEqual(len(Message.query.all()), 1)

    def test_add_message_while_logged_out(self):
        """Can user add a message if they aren't logged in?"""

        with self.client as c:
            resp = c.post("/messages/new",
                          data={"text": "Hello"},
                          follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertEqual(len(Message.query.all()), 0)

    def test_remove_message_while_logged_out(self):
        """Can a user remove a message if they aren't logged in? Assert NO"""
        msg = Message(text="Removal Test", user_id=self.testuser.id)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            msg = Message.query.one()
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertEqual(len(Message.query.all()), 1)

