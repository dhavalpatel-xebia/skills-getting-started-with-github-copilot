import copy

import pytest
from fastapi.testclient import TestClient
import src.app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    saved_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(saved_activities))


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_root_redirects_to_static_index(client):
    # Arrange & Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list(client):
    # Arrange & Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_adds_participant(client):
    # Arrange
    email = "new.student@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in app_module.activities[activity]["participants"]


def test_signup_for_missing_activity_returns_404(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/Nonexistent/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_existing_participant_returns_400(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    assert email not in app_module.activities[activity]["participants"]


def test_remove_nonexistent_participant_returns_404(client):
    # Arrange
    activity = "Chess Club"
    email = "unknown@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
