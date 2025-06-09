#!/usr/bin/env python3
"""
Authentication Component for Streamlit
Handles user authentication using Supabase Auth
"""

import streamlit as st
from typing import Optional, Dict
import sys
import os

# Add utils to path
sys.path.append(os.path.dirname(__file__))

try:
    from supabase_client import get_supabase_manager
except ImportError:
    st.error("Could not import Supabase manager. Please ensure it's properly configured.")
    st.stop()

class AuthComponent:
    """Streamlit authentication component using Supabase"""
    
    def __init__(self):
        self.supabase = get_supabase_manager()
        
        # Initialize session state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'auth_mode' not in st.session_state:
            st.session_state.auth_mode = 'login'
    
    def render_auth_sidebar(self) -> Optional[Dict]:
        """Render authentication in sidebar"""
        with st.sidebar:
            if st.session_state.authenticated:
                return self._render_user_info()
            else:
                return self._render_auth_form()
    
    def render_auth_main(self) -> Optional[Dict]:
        """Render authentication in main area"""
        if st.session_state.authenticated:
            return self._render_user_dashboard()
        else:
            return self._render_auth_form_main()
    
    def _render_user_info(self) -> Dict:
        """Render logged-in user information in sidebar"""
        user = st.session_state.user
        
        st.success(f"✅ Welcome, {user.get('email', 'User')}!")
        
        # User menu
        with st.expander("👤 Account"):
            st.write(f"**Email:** {user.get('email')}")
            st.write(f"**User ID:** {user.get('id')[:8]}...")
            
            if st.button("🚪 Sign Out", type="secondary"):
                self._handle_signout()
                st.rerun()
        
        return user
    
    def _render_user_dashboard(self) -> Dict:
        """Render user dashboard in main area"""
        user = st.session_state.user
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.success(f"✅ Welcome back, {user.get('email')}!")
        
        with col2:
            st.metric("👤 User ID", f"{user.get('id')[:8]}...")
        
        with col3:
            if st.button("🚪 Sign Out"):
                self._handle_signout()
                st.rerun()
        
        return user
    
    def _render_auth_form(self) -> None:
        """Render authentication form in sidebar"""
        st.subheader("🔐 Authentication")
        
        # Toggle between login and signup
        auth_mode = st.radio(
            "Choose:",
            ["🔑 Login", "📝 Sign Up"],
            key="auth_mode_radio"
        )
        
        if auth_mode == "🔑 Login":
            self._render_login_form()
        else:
            self._render_signup_form()
    
    def _render_auth_form_main(self) -> None:
        """Render authentication form in main area"""
        st.header("🔐 Financial Analytics Hub - Authentication")
        st.info("Please sign in to save your calculations and access personalized features.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔑 Login")
            self._render_login_form(key_suffix="_main")
        
        with col2:
            st.subheader("📝 Sign Up")
            self._render_signup_form(key_suffix="_main")
    
    def _render_login_form(self, key_suffix: str = "") -> None:
        """Render login form"""
        with st.form(f"login_form{key_suffix}"):
            email = st.text_input("📧 Email", key=f"login_email{key_suffix}")
            password = st.text_input("🔒 Password", type="password", key=f"login_password{key_suffix}")
            
            if st.form_submit_button("🔑 Sign In", type="primary"):
                if email and password:
                    self._handle_login(email, password)
                else:
                    st.error("Please fill in all fields")
    
    def _render_signup_form(self, key_suffix: str = "") -> None:
        """Render signup form"""
        with st.form(f"signup_form{key_suffix}"):
            email = st.text_input("📧 Email", key=f"signup_email{key_suffix}")
            password = st.text_input("🔒 Password", type="password", key=f"signup_password{key_suffix}")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", key=f"signup_confirm{key_suffix}")
            
            # Additional metadata
            full_name = st.text_input("👤 Full Name (optional)", key=f"signup_name{key_suffix}")
            risk_tolerance = st.selectbox(
                "📊 Risk Tolerance",
                ["Conservative", "Moderate", "Aggressive"],
                key=f"signup_risk{key_suffix}"
            )
            
            if st.form_submit_button("📝 Sign Up", type="primary"):
                if email and password and confirm_password:
                    if password == confirm_password:
                        metadata = {
                            "full_name": full_name,
                            "risk_tolerance": risk_tolerance.lower()
                        }
                        self._handle_signup(email, password, metadata)
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in all required fields")
    
    def _handle_login(self, email: str, password: str) -> None:
        """Handle user login"""
        with st.spinner("Signing in..."):
            result = self.supabase.sign_in(email, password)
            
            if result['success']:
                user_data = result['data'].user
                st.session_state.authenticated = True
                st.session_state.user = {
                    'id': user_data.id,
                    'email': user_data.email,
                    'metadata': user_data.user_metadata or {}
                }
                st.success("✅ Successfully signed in!")
                st.rerun()
            else:
                st.error(f"❌ Login failed: {result['error']}")
    
    def _handle_signup(self, email: str, password: str, metadata: Dict) -> None:
        """Handle user signup"""
        with st.spinner("Creating account..."):
            result = self.supabase.sign_up(email, password, metadata)
            
            if result['success']:
                st.success("✅ Account created successfully! Please check your email for verification.")
                st.info("After verifying your email, you can sign in using the login form.")
            else:
                st.error(f"❌ Signup failed: {result['error']}")
    
    def _handle_signout(self) -> None:
        """Handle user signout"""
        result = self.supabase.sign_out()
        
        # Clear session state
        st.session_state.authenticated = False
        st.session_state.user = None
        
        # Clear other session state items
        keys_to_clear = [
            'annual_result', 'sip_result', 'fund_result', 'scenarios',
            'quick_example', 'saved_calculations', 'user_preferences'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        if result['success']:
            st.success("✅ Successfully signed out!")
        else:
            st.warning("⚠️ Signout may have encountered an issue, but you're logged out locally.")
    
    def require_auth(self) -> bool:
        """Check if user is authenticated, redirect to auth if not"""
        if not st.session_state.authenticated:
            st.warning("🔐 Please sign in to access this feature.")
            self.render_auth_main()
            return False
        return True
    
    def get_current_user(self) -> Optional[Dict]:
        """Get the current authenticated user"""
        if st.session_state.authenticated:
            return st.session_state.user
        return None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.authenticated

# Global instance
@st.cache_resource
def get_auth_component():
    """Get cached auth component instance"""
    return AuthComponent() 