"""
API Client Integration for Plan Upgrade Endpoints
This module provides utility functions for integrating with the backend plan upgrade endpoints.

These utilities should be imported in your frontend or backend service code.
"""

import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PlanUpgradeClient:
    """Client for interacting with plan upgrade endpoints."""
    
    def __init__(self, backend_url: str, api_timeout: int = 30):
        """
        Initialize the plan upgrade client.
        
        Args:
            backend_url: Base URL of the backend API (e.g., http://localhost:8000)
            api_timeout: Timeout for API requests in seconds
        """
        self.backend_url = backend_url.rstrip("/")
        self.api_timeout = api_timeout
        self.client = httpx.AsyncClient(timeout=api_timeout)
    
    async def create_upgrade_checkout_session(
        self,
        plan_id: str,
        uid: str,
        firebase_token: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Create a Stripe checkout session for plan upgrade.
        
        Args:
            plan_id: ID of the plan to upgrade to (basic, pro, enterprise)
            uid: Firebase user ID
            firebase_token: Firebase ID token for authentication
            latitude: Optional user latitude for location update
            longitude: Optional user longitude for location update
        
        Returns:
            Dictionary with checkout URL: {"url": "https://checkout.stripe.com/..."}
        
        Raises:
            httpx.HTTPError: If the API request fails
            ValueError: If response doesn't contain URL
        """
        try:
            payload = {
                "plan_id": plan_id,
                "uid": uid,
                "latitude": latitude,
                "longitude": longitude,
            }
            
            headers = {
                "Authorization": f"Bearer {firebase_token}",
                "Content-Type": "application/json",
            }
            
            response = await self.client.post(
                f"{self.backend_url}/billing/upgrade-plan",
                json=payload,
                headers=headers,
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "url" not in data:
                raise ValueError("Response missing checkout URL")
            
            logger.info(f"Checkout session created for user {uid} plan {plan_id}")
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise
    
    async def record_upgrade(
        self,
        uid: str,
        plan_id: str,
        org_name: Optional[str] = None,
        admin_email: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Record a plan upgrade in the backend database.
        This is a public endpoint that doesn't require authentication.
        
        Args:
            uid: Firebase user ID
            plan_id: ID of the plan being upgraded to
            org_name: Optional organization name
            admin_email: Optional admin email address
            latitude: Optional user latitude
            longitude: Optional user longitude
        
        Returns:
            Dictionary with status: {"status": "ok", "message": "..."}
        
        Raises:
            httpx.HTTPError: If the API request fails
        """
        try:
            payload = {
                "uid": uid,
                "plan_id": plan_id,
                "org_name": org_name,
                "admin_email": admin_email,
                "latitude": latitude,
                "longitude": longitude,
            }
            
            response = await self.client.post(
                f"{self.backend_url}/billing/public/record-upgrade",
                json=payload,
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Upgrade recorded for user {uid} to plan {plan_id}")
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to record upgrade: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client connection."""
        await self.client.aclose()


# ===== Synchronous Client (for non-async contexts) =====

class PlanUpgradeClientSync:
    """Synchronous client for plan upgrade endpoints (blocking API calls)."""
    
    def __init__(self, backend_url: str, api_timeout: int = 30):
        """
        Initialize the synchronous plan upgrade client.
        
        Args:
            backend_url: Base URL of the backend API
            api_timeout: Timeout for API requests in seconds
        """
        self.backend_url = backend_url.rstrip("/")
        self.api_timeout = api_timeout
        self.client = httpx.Client(timeout=api_timeout)
    
    def create_upgrade_checkout_session(
        self,
        plan_id: str,
        uid: str,
        firebase_token: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Create a Stripe checkout session for plan upgrade (synchronous).
        
        Args:
            plan_id: ID of the plan to upgrade to
            uid: Firebase user ID
            firebase_token: Firebase ID token
            latitude: Optional user latitude
            longitude: Optional user longitude
        
        Returns:
            Dictionary with checkout URL
        """
        try:
            payload = {
                "plan_id": plan_id,
                "uid": uid,
                "latitude": latitude,
                "longitude": longitude,
            }
            
            headers = {
                "Authorization": f"Bearer {firebase_token}",
                "Content-Type": "application/json",
            }
            
            response = self.client.post(
                f"{self.backend_url}/billing/upgrade-plan",
                json=payload,
                headers=headers,
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "url" not in data:
                raise ValueError("Response missing checkout URL")
            
            logger.info(f"Checkout session created for user {uid}")
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise
    
    def record_upgrade(
        self,
        uid: str,
        plan_id: str,
        org_name: Optional[str] = None,
        admin_email: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Record a plan upgrade (synchronous, blocking).
        
        Args:
            uid: Firebase user ID
            plan_id: Plan ID
            org_name: Optional organization name
            admin_email: Optional admin email
            latitude: Optional latitude
            longitude: Optional longitude
        
        Returns:
            Dictionary with status
        """
        try:
            payload = {
                "uid": uid,
                "plan_id": plan_id,
                "org_name": org_name,
                "admin_email": admin_email,
                "latitude": latitude,
                "longitude": longitude,
            }
            
            response = self.client.post(
                f"{self.backend_url}/billing/public/record-upgrade",
                json=payload,
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Upgrade recorded for user {uid}")
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to record upgrade: {e}")
            raise
    
    def close(self):
        """Close the HTTP client connection."""
        self.client.close()


# ===== Example Usage =====

if __name__ == "__main__":
    import asyncio
    
    async def example_async():
        """Example of using the async client."""
        client = PlanUpgradeClient("http://localhost:8000")
        
        try:
            # Create checkout session
            result = await client.create_upgrade_checkout_session(
                plan_id="pro",
                uid="test_user_id",
                firebase_token="your_firebase_token",
                latitude=40.7128,
                longitude=-74.0060,
            )
            print(f"Checkout URL: {result['url']}")
            
            # Record the upgrade
            record_result = await client.record_upgrade(
                uid="test_user_id",
                plan_id="pro",
                org_name="Test Organization",
                admin_email="admin@test.com",
            )
            print(f"Record result: {record_result}")
            
        finally:
            await client.close()
    
    def example_sync():
        """Example of using the synchronous client."""
        client = PlanUpgradeClientSync("http://localhost:8000")
        
        try:
            # Create checkout session
            result = client.create_upgrade_checkout_session(
                plan_id="pro",
                uid="test_user_id",
                firebase_token="your_firebase_token",
            )
            print(f"Checkout URL: {result['url']}")
            
            # Record the upgrade
            record_result = client.record_upgrade(
                uid="test_user_id",
                plan_id="pro",
            )
            print(f"Record result: {record_result}")
            
        finally:
            client.close()
    
    # Run async example
    print("=== Async Example ===")
    asyncio.run(example_async())
    
    # Or run sync example
    # print("=== Sync Example ===")
    # example_sync()
