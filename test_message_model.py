"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app


from app import app
app.config['TESTING'] = True
app.config['SQLALCHEMY_ECHO'] = False


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class MessageModelTestCase(TestCase):
    """Test Message Model."""

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        user = User(
            email="OURTEST@test.com",
            username="TESTUSERNAME",
            password="HASHED_PASSWORD"
        )

        db.session.add(user)
        db.session.commit()

        message = Message(
            text="Hello World",
            user_id=user.id
        )

        db.session.add(message)
        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions"""
        db.session.rollback()

    def test_message_model(self):
        """Does basic model work as expected?"""
        m = Message(
            text="This is a test.",
            user_id=self.user.id
        )
        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(m.user), 1)
