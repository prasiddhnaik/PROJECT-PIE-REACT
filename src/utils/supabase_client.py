#!/usr/bin/env python3
"""
Supabase Client Configuration and Utilities
Handles database operations, authentication, and real-time subscriptions
"""

import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta
import pandas as pd

# Load environment variables
load_dotenv()

class SupabaseManager:
    """Manage Supabase operations for the Financial Analytics Hub"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            st.error("⚠️ Supabase configuration missing. Please set SUPABASE_URL and SUPABASE_KEY in your environment.")
            st.stop()
        
        self.client = create_client(self.supabase_url, self.supabase_key)
        self.admin_client = None
        
        if self.supabase_service_key:
            self.admin_client = create_client(self.supabase_url, self.supabase_service_key)
    
    def get_client(self) -> Client:
        """Get the Supabase client"""
        return self.client
    
    def get_admin_client(self) -> Optional[Client]:
        """Get the admin Supabase client"""
        return self.admin_client
    
    # ===== Authentication Methods =====
    
    def sign_up(self, email: str, password: str, metadata: Dict = None) -> Dict:
        """Sign up a new user"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": metadata} if metadata else {}
            })
            return {"success": True, "data": response}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sign_in(self, email: str, password: str) -> Dict:
        """Sign in an existing user"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {"success": True, "data": response}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sign_out(self) -> Dict:
        """Sign out the current user"""
        try:
            self.client.auth.sign_out()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_current_user(self) -> Optional[Dict]:
        """Get the current authenticated user"""
        try:
            user = self.client.auth.get_user()
            return user.user if user else None
        except Exception as e:
            return None
    
    # ===== SIP Calculations Storage =====
    
    def save_sip_calculation(self, user_id: str, calculation_data: Dict) -> Dict:
        """Save a SIP calculation to the database"""
        try:
            # Prepare data for insertion
            data = {
                "user_id": user_id,
                "calculation_type": calculation_data.get("type", "monthly_sip"),
                "monthly_sip": calculation_data.get("monthly_sip", 0),
                "annual_rate": calculation_data.get("annual_rate", 0),
                "time_years": calculation_data.get("time_years", 0),
                "final_value": calculation_data.get("final_value", 0),
                "total_invested": calculation_data.get("total_invested", 0),
                "profit": calculation_data.get("profit", 0),
                "total_return_percent": calculation_data.get("total_return_percent", 0),
                "risk_level": calculation_data.get("risk_level", ""),
                "fund_name": calculation_data.get("fund_name"),
                "calculation_metadata": json.dumps(calculation_data),
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("sip_calculations").insert(data).execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_calculations(self, user_id: str, limit: int = 50) -> Dict:
        """Get all SIP calculations for a user"""
        try:
            response = self.client.table("sip_calculations")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_calculation(self, calculation_id: str, user_id: str) -> Dict:
        """Delete a specific calculation"""
        try:
            response = self.client.table("sip_calculations")\
                .delete()\
                .eq("id", calculation_id)\
                .eq("user_id", user_id)\
                .execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ===== Portfolio Management =====
    
    def save_portfolio(self, user_id: str, portfolio_data: Dict) -> Dict:
        """Save user portfolio data"""
        try:
            data = {
                "user_id": user_id,
                "portfolio_name": portfolio_data.get("name", "My Portfolio"),
                "total_invested": portfolio_data.get("total_invested", 0),
                "current_value": portfolio_data.get("current_value", 0),
                "holdings": json.dumps(portfolio_data.get("holdings", [])),
                "risk_tolerance": portfolio_data.get("risk_tolerance", "moderate"),
                "investment_goals": json.dumps(portfolio_data.get("goals", [])),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("portfolios").insert(data).execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_portfolios(self, user_id: str) -> Dict:
        """Get all portfolios for a user"""
        try:
            response = self.client.table("portfolios")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("updated_at", desc=True)\
                .execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ===== User Preferences =====
    
    def save_user_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """Save user preferences and settings"""
        try:
            data = {
                "user_id": user_id,
                "default_sip_amount": preferences.get("default_sip", 5000),
                "preferred_investment_duration": preferences.get("duration", 10),
                "risk_tolerance": preferences.get("risk_tolerance", "moderate"),
                "notification_preferences": json.dumps(preferences.get("notifications", {})),
                "dashboard_layout": json.dumps(preferences.get("layout", {})),
                "favorite_funds": json.dumps(preferences.get("favorite_funds", [])),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Upsert (insert or update)
            response = self.client.table("user_preferences")\
                .upsert(data, on_conflict="user_id")\
                .execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences"""
        try:
            response = self.client.table("user_preferences")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ===== Analytics and Insights =====
    
    def get_analytics_data(self, user_id: str, days: int = 30) -> Dict:
        """Get user analytics data for the dashboard"""
        try:
            since_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Get recent calculations
            calc_response = self.client.table("sip_calculations")\
                .select("*")\
                .eq("user_id", user_id)\
                .gte("created_at", since_date)\
                .execute()
            
            # Get portfolio performance
            portfolio_response = self.client.table("portfolios")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()
            
            return {
                "success": True,
                "data": {
                    "recent_calculations": calc_response.data,
                    "portfolios": portfolio_response.data,
                    "period_days": days
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ===== Database Schema Setup =====
    
    def setup_database_schema(self) -> Dict:
        """Setup the database schema (requires admin privileges)"""
        if not self.admin_client:
            return {"success": False, "error": "Admin client not available"}
        
        try:
            # This would typically be done via SQL in Supabase dashboard
            # or using migrations. For demo purposes, we'll document the schema
            schema_info = {
                "tables": [
                    {
                        "name": "sip_calculations",
                        "description": "Store SIP calculation results",
                        "columns": [
                            "id (uuid, primary key)",
                            "user_id (uuid, foreign key to auth.users)",
                            "calculation_type (text)",
                            "monthly_sip (numeric)",
                            "annual_rate (numeric)",
                            "time_years (numeric)",
                            "final_value (numeric)",
                            "total_invested (numeric)",
                            "profit (numeric)",
                            "total_return_percent (numeric)",
                            "risk_level (text)",
                            "fund_name (text, nullable)",
                            "calculation_metadata (jsonb)",
                            "created_at (timestamp with time zone)"
                        ]
                    },
                    {
                        "name": "portfolios",
                        "description": "Store user portfolio data",
                        "columns": [
                            "id (uuid, primary key)",
                            "user_id (uuid, foreign key to auth.users)",
                            "portfolio_name (text)",
                            "total_invested (numeric)",
                            "current_value (numeric)",
                            "holdings (jsonb)",
                            "risk_tolerance (text)",
                            "investment_goals (jsonb)",
                            "created_at (timestamp with time zone)",
                            "updated_at (timestamp with time zone)"
                        ]
                    },
                    {
                        "name": "user_preferences",
                        "description": "Store user preferences and settings",
                        "columns": [
                            "id (uuid, primary key)",
                            "user_id (uuid, foreign key to auth.users, unique)",
                            "default_sip_amount (numeric)",
                            "preferred_investment_duration (numeric)",
                            "risk_tolerance (text)",
                            "notification_preferences (jsonb)",
                            "dashboard_layout (jsonb)",
                            "favorite_funds (jsonb)",
                            "created_at (timestamp with time zone)",
                            "updated_at (timestamp with time zone)"
                        ]
                    }
                ]
            }
            return {"success": True, "schema": schema_info}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global instance
@st.cache_resource
def get_supabase_manager():
    """Get cached Supabase manager instance"""
    return SupabaseManager() 