"""
Test suite for plan upgrade endpoints.
Run with: pytest tests/test_plan_upgrade.py
"""

import pytest
import httpx
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.routers.billing import (
    upgrade_plan,
    record_upgrade,
    UpgradePlanRequest,
    RecordUpgradeRequest,
)
from fastapi.testclient import TestClient
from app.main import app


class TestUpgradePlanEndpoint:
    """Tests for POST /billing/upgrade-plan endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_missing_authorization_header(self, client):
        """Test that missing Authorization header returns 401."""
        response = client.post(
            "/billing/upgrade-plan",
            json={
                "plan_id": "pro",
                "uid": "test_user",
                "latitude": 40.7128,
                "longitude": -74.0060,
            },
        )
        assert response.status_code == 401
        assert "Unauthorized" in response.json()["detail"]
    
    def test_missing_uid(self, client):
        """Test that missing UID returns 400."""
        response = client.post(
            "/billing/upgrade-plan",
            json={
                "plan_id": "pro",
                "latitude": 40.7128,
                "longitude": -74.0060,
            },
            headers={"Authorization": "Bearer test_token"},
        )
        assert response.status_code == 422  # Validation error
    
    def test_invalid_plan_id(self, client):
        """Test that invalid plan ID returns 400."""
        with patch("app.routers.billing.get_auth") as mock_auth:
            mock_auth_instance = Mock()
            mock_auth.return_value = mock_auth_instance
            mock_auth_instance.verify_id_token.return_value = {"uid": "test_user"}
            
            with patch("app.routers.billing.get_db") as mock_db:
                mock_db_instance = Mock()
                mock_db.return_value = mock_db_instance
                
                # Mock user doc
                mock_doc = Mock()
                mock_doc.exists = True
                mock_doc.to_dict.return_value = {"email": "test@example.com"}
                
                mock_collection = Mock()
                mock_collection.document().get.return_value = mock_doc
                mock_db_instance.collection.return_value = mock_collection
                
                response = client.post(
                    "/billing/upgrade-plan",
                    json={
                        "plan_id": "invalid_plan",
                        "uid": "test_user",
                    },
                    headers={"Authorization": "Bearer valid_token"},
                )
        
        assert response.status_code == 400
        assert "Invalid plan ID" in response.json()["detail"]
    
    def test_user_not_found(self, client):
        """Test that non-existent user returns 404."""
        with patch("app.routers.billing.get_auth") as mock_auth:
            mock_auth_instance = Mock()
            mock_auth.return_value = mock_auth_instance
            mock_auth_instance.verify_id_token.return_value = {"uid": "test_user"}
            
            with patch("app.routers.billing.get_db") as mock_db:
                mock_db_instance = Mock()
                mock_db.return_value = mock_db_instance
                
                # Mock user doc not found
                mock_doc = Mock()
                mock_doc.exists = False
                
                mock_collection = Mock()
                mock_collection.document().get.return_value = mock_doc
                mock_db_instance.collection.return_value = mock_collection
                
                response = client.post(
                    "/billing/upgrade-plan",
                    json={
                        "plan_id": "pro",
                        "uid": "test_user",
                    },
                    headers={"Authorization": "Bearer valid_token"},
                )
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    @patch("app.routers.billing.stripe")
    def test_successful_upgrade_plan_creation(self, mock_stripe, client):
        """Test successful upgrade plan checkout session creation."""
        with patch("app.routers.billing.get_auth") as mock_auth:
            mock_auth_instance = Mock()
            mock_auth.return_value = mock_auth_instance
            mock_auth_instance.verify_id_token.return_value = {"uid": "test_user"}
            
            with patch("app.routers.billing.get_db") as mock_db:
                mock_db_instance = Mock()
                mock_db.return_value = mock_db_instance
                
                # Mock user doc
                mock_doc = Mock()
                mock_doc.exists = True
                mock_doc.to_dict.return_value = {
                    "email": "test@example.com",
                    "org_name": "Test Org",
                }
                
                mock_collection = Mock()
                mock_collection.document().get.return_value = mock_doc
                mock_db_instance.collection.return_value = mock_collection
                
                # Mock Stripe session
                mock_session = Mock()
                mock_session.id = "cs_test_123"
                mock_session.url = "https://checkout.stripe.com/pay/cs_test_123"
                mock_stripe.checkout.Session.create.return_value = mock_session
                
                # Mock environment variables
                with patch.dict("os.environ", {
                    "STRIPE_PRICE_PRO": "price_pro_123",
                }):
                    response = client.post(
                        "/billing/upgrade-plan",
                        json={
                            "plan_id": "pro",
                            "uid": "test_user",
                            "latitude": 40.7128,
                            "longitude": -74.0060,
                        },
                        headers={"Authorization": "Bearer valid_token"},
                    )
        
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "checkout.stripe.com" in data["url"]


class TestRecordUpgradeEndpoint:
    """Tests for POST /billing/public/record-upgrade endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_missing_required_fields(self, client):
        """Test that missing required fields returns 400."""
        response = client.post(
            "/billing/public/record-upgrade",
            json={
                "uid": "test_user",
                # Missing plan_id
            },
        )
        assert response.status_code == 422  # Validation error
    
    @patch("app.routers.billing.get_db")
    def test_successful_record_upgrade(self, mock_db, client):
        """Test successful upgrade recording."""
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance
        
        # Mock successful add
        mock_collection = Mock()
        mock_collection.add.return_value = (None, Mock())
        mock_db_instance.collection.return_value = mock_collection
        
        response = client.post(
            "/billing/public/record-upgrade",
            json={
                "uid": "test_user",
                "plan_id": "pro",
                "org_name": "Test Org",
                "admin_email": "admin@test.com",
                "latitude": 40.7128,
                "longitude": -74.0060,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    @patch("app.routers.billing.get_db")
    def test_database_error_handling(self, mock_db, client):
        """Test that database errors are handled gracefully."""
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance
        
        # Mock database error
        mock_collection = Mock()
        mock_collection.add.side_effect = Exception("Database error")
        mock_db_instance.collection.return_value = mock_collection
        
        response = client.post(
            "/billing/public/record-upgrade",
            json={
                "uid": "test_user",
                "plan_id": "pro",
            },
        )
        
        assert response.status_code == 500


class TestUpgradePlanRequestModel:
    """Tests for UpgradePlanRequest Pydantic model."""
    
    def test_valid_request(self):
        """Test creating valid request model."""
        request = UpgradePlanRequest(
            plan_id="pro",
            uid="test_user",
            latitude=40.7128,
            longitude=-74.0060,
        )
        assert request.plan_id == "pro"
        assert request.uid == "test_user"
    
    def test_optional_fields(self):
        """Test that latitude and longitude are optional."""
        request = UpgradePlanRequest(
            plan_id="pro",
            uid="test_user",
        )
        assert request.latitude is None
        assert request.longitude is None


class TestRecordUpgradeRequestModel:
    """Tests for RecordUpgradeRequest Pydantic model."""
    
    def test_valid_request(self):
        """Test creating valid request model."""
        request = RecordUpgradeRequest(
            uid="test_user",
            plan_id="pro",
            org_name="Test Org",
            admin_email="admin@test.com",
        )
        assert request.uid == "test_user"
        assert request.plan_id == "pro"
    
    def test_all_optional_except_required(self):
        """Test that all fields except uid and plan_id are optional."""
        request = RecordUpgradeRequest(
            uid="test_user",
            plan_id="pro",
        )
        assert request.org_name is None
        assert request.admin_email is None
        assert request.latitude is None
        assert request.longitude is None


# ===== Integration Tests =====

@pytest.mark.asyncio
class TestIntegration:
    """Integration tests with actual API calls (requires backend running)."""
    
    async def test_full_upgrade_flow(self):
        """Test complete upgrade flow: create session -> record upgrade."""
        import os
        
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        
        # This test requires:
        # 1. Backend running
        # 2. Valid Firebase token
        # 3. Stripe credentials configured
        
        pytest.skip("Requires running backend and valid credentials")


# ===== Load Testing Helpers =====

def generate_test_upgrade_requests(count: int) -> list:
    """Generate test upgrade requests for load testing."""
    requests = []
    for i in range(count):
        requests.append({
            "uid": f"test_user_{i}",
            "plan_id": ["basic", "pro", "enterprise"][i % 3],
            "org_name": f"Test Org {i}",
            "admin_email": f"admin{i}@test.com",
            "latitude": 40.7128 + (i * 0.001),
            "longitude": -74.0060 + (i * 0.001),
        })
    return requests


if __name__ == "__main__":
    # Generate sample load test data
    test_requests = generate_test_upgrade_requests(100)
    print(f"Generated {len(test_requests)} test requests")
    print(f"Sample request: {test_requests[0]}")
