"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

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

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """test the repr"""

        user = User.query.filter_by(username="TESTUSERNAME").first()

        self.assertEqual(str(user), f"<User #{user.id}: {user.username}, {user.email}>")
        
    def test_is_following(self):
        """test if user1 is following user2"""

        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        user2 = User.query.filter_by(username="TESTUSERNAME").first()

        user1.following.append(user2)
        db.session.add(user1)
        db.session.commit()

        self.assertEqual(user1.is_following(user2), True) 
        self.assertEqual(user2.is_following(user1), False)

    def test_is_followed_by(self):
        """test if user1 is following user2"""

        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        user2 = User.query.filter_by(username="TESTUSERNAME").first()

        user1.following.append(user2)
        db.session.add(user1)
        db.session.commit()
        
        self.assertEqual(user1.is_followed_by(user2), False) 
        self.assertEqual(user2.is_followed_by(user1), True)

    def test_signup(self):

        with self.client as client:

            user = User.signup("user1", "user1@email.com", "password1", None)
            db.session.commit()
            # user2 = User.signup("user1", "user1@email.com", "password1", None)
            # db.session.commit()

            # self.assertIsInstance(user, User)
            # with self.assertRaises(IntegrityError):
            #     User.signup("user1", "user1@email.com", "password1", None)
            #     db.session.commit()

            self.assertIsInstance(user, User)
            with self.assertRaises(InvalidRequestError):
                User.signup("user1", "user1@email.com", "password1", None)
                db.session.commit()
