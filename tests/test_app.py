import pytest
from unittest.mock import patch
from app.models.database import ConversationHistory

def test_generate_conversation_starters(client):
    """Test generating conversation starters (Scenario 1)"""
    payload = {
        "description": "AI for Sustainable Cities",
        "interests": ["climate change", "urban planning"]
    }
    response = client.post("/api/conversation", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "topics" in data
    assert "suggestions" in data
    assert "id" in data
    
    assert isinstance(data["topics"], list)
    assert len(data["topics"]) > 0
    assert isinstance(data["suggestions"], list)
    assert len(data["suggestions"]) > 0

@patch("app.services.fact_checker.wikipedia.search")
@patch("app.services.fact_checker.wikipedia.page")
def test_factcheck_endpoint(mock_page, mock_search, client):
    """Test quick fact verification (Scenario 2)"""
    mock_search.return_value = ["Blockchain in Healthcare"]
    
    mock_p = mock_page.return_value
    mock_p.title = "Blockchain in Healthcare"
    mock_p.summary = "Blockchain technology is increasingly investigated for securing electronic health records..."
    mock_p.url = "https://en.wikipedia.org/wiki/Blockchain"
    
    payload = {
        "query": "blockchain in healthcare"
    }
    response = client.post("/api/factcheck", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "summary" in data
    assert "Blockchain" in data["summary"]
    assert "Source Reference:" in data["summary"]

def test_history_and_feedback(client):
    """Test retrieving logs and updating feedback (Scenario 3)"""
    # 1. Initially, history should be empty
    response = client.get("/api/history")
    assert response.status_code == 200
    assert len(response.json()) == 0
    
    # 2. Generate a conversation item to populate DB
    payload = {
        "description": "AI for Sustainable Cities",
        "interests": ["climate change", "urban planning"]
    }
    gen_response = client.post("/api/conversation", json=payload)
    assert gen_response.status_code == 200
    item_id = gen_response.json()["id"]
    
    # 3. Retrieve history and verify item exists
    hist_response = client.get("/api/history")
    assert hist_response.status_code == 200
    logs = hist_response.json()
    assert len(logs) == 1
    assert logs[0]["id"] == item_id
    assert logs[0]["description"] == "AI for Sustainable Cities"
    assert logs[0]["feedback"] is None
    
    # 4. Patch feedback to thumbs-up (True)
    feedback_payload = {
        "feedback": True
    }
    patch_response = client.post(f"/api/history/{item_id}/feedback", json=feedback_payload) # wait, PATCH is at /api/history/{id}/feedback
    # Let's check: our history route uses PATCH /api/history/{history_id}/feedback
    patch_response = client.patch(f"/api/history/{item_id}/feedback", json=feedback_payload)
    assert patch_response.status_code == 200
    assert patch_response.json()["feedback"] is True
    
    # 5. Check history again to ensure it persisted
    hist_response_2 = client.get("/api/history")
    assert hist_response_2.json()[0]["feedback"] is True

def test_analyze_event(client):
    """Test analyzing event endpoint (Scenario 4)"""
    payload = {
        "description": "AI for Sustainable Cities"
    }
    response = client.post("/api/analyze-event", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "topics" in data
    assert isinstance(data["topics"], list)
    assert len(data["topics"]) > 0

def test_json_persistence(client):
    """Test data persistence to local JSON files (Scenario 5)"""
    import os
    import json
    
    # 1. Clean previous state
    for f in ["history.json", "feedback.json"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass
            
    # 2. Call generate-conversation endpoint
    payload = {
        "description": "Virtual Reality in Modern Classrooms",
        "interests": ["edtech", "virtual reality"]
    }
    response = client.post("/api/generate-conversation", json=payload)
    assert response.status_code == 200
    data = response.json()
    item_id = data["id"]
    
    # 3. Verify history.json was created and contains the record
    assert os.path.exists("history.json")
    with open("history.json", "r", encoding="utf-8") as f:
        history_data = json.load(f)
    assert len(history_data) > 0
    assert history_data[0]["id"] == item_id
    assert history_data[0]["description"] == "Virtual Reality in Modern Classrooms"
    assert history_data[0]["feedback"] is None
    
    # 4. Patch feedback
    feedback_payload = {"feedback": True}
    patch_response = client.patch(f"/api/history/{item_id}/feedback", json=feedback_payload)
    assert patch_response.status_code == 200
    
    # 5. Verify feedback.json was created and contains the action log
    assert os.path.exists("feedback.json")
    with open("feedback.json", "r", encoding="utf-8") as f:
        feedback_data = json.load(f)
    assert len(feedback_data) > 0
    assert feedback_data[-1]["id"] == item_id
    assert feedback_data[-1]["feedback"] is True
    
    # 6. Verify history.json matches the feedback update
    with open("history.json", "r", encoding="utf-8") as f:
        history_data_2 = json.load(f)
    assert history_data_2[0]["feedback"] is True
