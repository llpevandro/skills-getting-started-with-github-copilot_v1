"""
FastAPI endpoint tests for the High School Activities API.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and conditions
- Act: Execute the action being tested
- Assert: Verify the results
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Test that GET /activities returns the complete activities list.
        
        Arrange: No setup needed - activities are pre-populated
        Act: Make GET request to /activities
        Assert: Response status is 200 and contains all activities
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        assert len(activities_data) > 0
        assert "Chess Club" in activities_data

    def test_get_activities_contains_required_fields(self, client, reset_activities):
        """
        Test that each activity in the response has required fields.
        
        Arrange: No setup needed
        Act: Make GET request to /activities
        Assert: Each activity contains description, schedule, max_participants, and participants
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for activity_name, activity_details in activities_data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity_success(
        self, client, reset_activities, sample_activity_name, sample_email
    ):
        """
        Test successful signup for an activity.
        
        Arrange: Use sample activity name and email
        Act: Make POST request to sign up
        Assert: Response is 200 and participant is added
        """
        # Arrange
        activity_name = sample_activity_name
        email = sample_email
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        
        # Verify participant was actually added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client, reset_activities, sample_email):
        """
        Test signup fails when activity does not exist.
        
        Arrange: Use a non-existent activity name
        Act: Make POST request to sign up
        Assert: Response is 404 with appropriate error message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = sample_email
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_prevents_duplicate_registration(
        self, client, reset_activities, sample_activity_name
    ):
        """
        Test that a student cannot sign up twice for the same activity.
        
        Arrange: Get an email already registered for the activity
        Act: Try to sign up the same student again
        Assert: Response is 400 with duplicate registration error
        """
        # Arrange
        activity_name = sample_activity_name
        # Get an existing participant from the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        existing_email = activities[activity_name]["participants"][0]
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_adds_new_participant(self, client, reset_activities, sample_activity_name):
        """
        Test that signup correctly adds a new participant to the activity.
        
        Arrange: Get initial participant count
        Act: Sign up a new student
        Assert: Participant count increases by 1
        """
        # Arrange
        activity_name = sample_activity_name
        email = "new.student@mergington.edu"
        
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        new_count = len(activities_response.json()[activity_name]["participants"])
        assert new_count == initial_count + 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client, reset_activities, sample_activity_name):
        """
        Test successful unregistration from an activity.
        
        Arrange: Get an existing participant
        Act: Make DELETE request to unregister
        Assert: Response is 200 and participant is removed
        """
        # Arrange
        activity_name = sample_activity_name
        activities_response = client.get("/activities")
        email = activities_response.json()[activity_name]["participants"][0]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        
        # Verify participant was actually removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client, reset_activities, sample_email):
        """
        Test unregister fails when activity does not exist.
        
        Arrange: Use a non-existent activity name
        Act: Make DELETE request to unregister
        Assert: Response is 404 with appropriate error message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = sample_email
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_student_not_registered(
        self, client, reset_activities, sample_activity_name, sample_email
    ):
        """
        Test unregister fails when student is not registered for the activity.
        
        Arrange: Use an email that is not registered for the activity
        Act: Make DELETE request to unregister
        Assert: Response is 400 with appropriate error message
        """
        # Arrange
        activity_name = sample_activity_name
        email = sample_email
        
        # Ensure the email is not registered
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_reduces_participant_count(
        self, client, reset_activities, sample_activity_name
    ):
        """
        Test that unregister correctly reduces the participant count.
        
        Arrange: Get initial participant count
        Act: Unregister a student
        Assert: Participant count decreases by 1
        """
        # Arrange
        activity_name = sample_activity_name
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()[activity_name]["participants"])
        email = activities_response.json()[activity_name]["participants"][0]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        new_count = len(activities_response.json()[activity_name]["participants"])
        assert new_count == initial_count - 1


class TestIntegrationSignupAndUnregister:
    """Integration tests combining signup and unregister operations."""

    def test_signup_then_unregister_cycle(self, client, reset_activities, sample_activity_name):
        """
        Test complete signup and unregister cycle.
        
        Arrange: Select a new email not currently registered
        Act: Sign up, then unregister the same student
        Assert: Student is registered then removed, no errors occur
        """
        # Arrange
        activity_name = sample_activity_name
        email = "integration.test@mergington.edu"
        
        # Act: Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup worked
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]
        
        # Act: Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Assert: Participant removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]

    def test_cannot_signup_after_unregister_then_signup_again(
        self, client, reset_activities, sample_activity_name
    ):
        """
        Test that a student can sign up again after unregistering.
        
        Arrange: Get a student and unregister them
        Act: Try to sign up the same student again
        Assert: Second signup succeeds (not blocked by previous registration)
        """
        # Arrange
        activity_name = sample_activity_name
        email = "reregister.test@mergington.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Act: Try signup again
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Second signup should succeed
        assert response2.status_code == 200
        
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]
