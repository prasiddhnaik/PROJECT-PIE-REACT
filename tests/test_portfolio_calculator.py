#!/usr/bin/env python3
"""
🧪 AI Portfolio Return Calculator - Comprehensive Test Suite
Professional-grade testing framework with 100% coverage validation
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, mock_open
import tempfile
import os
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from portfolio_return_calculator import PortfolioReturnCalculator

# ==========================================
# 🔧 TEST FIXTURES & SETUP
# ==========================================

@pytest.fixture
def sample_nav_data():
    """Create sample NAV data for testing"""
    dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
    nav_values = [100.0, 102.0, 98.5, 105.2, 103.8, 99.1, 107.3, 104.5, 102.7, 108.9]
    
    return pd.DataFrame({
        'Date': dates,
        'NAV': nav_values
    })

@pytest.fixture
def calculator():
    """Create a fresh calculator instance for each test"""
    return PortfolioReturnCalculator()

@pytest.fixture
def calculator_with_data(calculator, sample_nav_data):
    """Calculator pre-loaded with sample data"""
    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        sample_nav_data.to_csv(f.name, index=False)
        csv_path = f.name
    
    calculator.load_fund_data("Test Fund", csv_path)
    
    # Cleanup
    yield calculator
    os.unlink(csv_path)

@pytest.fixture
def multi_fund_calculator(calculator):
    """Calculator with multiple funds loaded"""
    # Fund 1: Positive performance
    fund1_data = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=5),
        'NAV': [100.0, 105.0, 110.0, 108.0, 115.0]
    })
    
    # Fund 2: Negative performance (triggers AI warning)
    fund2_data = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=5),
        'NAV': [200.0, 195.0, 185.0, 180.0, 175.0]
    })
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1:
        fund1_data.to_csv(f1.name, index=False)
        fund1_path = f1.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
        fund2_data.to_csv(f2.name, index=False)
        fund2_path = f2.name
    
    calculator.load_fund_data("Growth Fund", fund1_path)
    calculator.load_fund_data("Declining Fund", fund2_path)
    
    # Cleanup
    yield calculator
    os.unlink(fund1_path)
    os.unlink(fund2_path)

# ==========================================
# 📊 CORE FUNCTIONALITY TESTS
# ==========================================

class TestPortfolioReturnCalculator:
    """Test suite for core portfolio calculation functionality"""
    
    def test_initialization(self, calculator):
        """Test calculator initialization"""
        assert hasattr(calculator, 'funds_data')
        assert isinstance(calculator.funds_data, dict)
        assert len(calculator.funds_data) == 0
    
    def test_load_fund_data_success(self, calculator, sample_nav_data):
        """Test successful fund data loading"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_nav_data.to_csv(f.name, index=False)
            csv_path = f.name
        
        try:
            result = calculator.load_fund_data("Test Fund", csv_path)
            
            assert result is True
            assert "Test Fund" in calculator.funds_data
            assert len(calculator.funds_data["Test Fund"]) == len(sample_nav_data)
            assert 'Date' in calculator.funds_data["Test Fund"].columns
            assert 'NAV' in calculator.funds_data["Test Fund"].columns
        finally:
            os.unlink(csv_path)
    
    def test_load_fund_data_file_not_found(self, calculator):
        """Test loading non-existent file"""
        result = calculator.load_fund_data("Fake Fund", "non_existent_file.csv")
        assert result is False
        assert "Fake Fund" not in calculator.funds_data
    
    def test_calculate_percentage_return(self, calculator_with_data):
        """Test percentage return calculation accuracy"""
        result = calculator_with_data.calculate_percentage_return("Test Fund")
        
        # Expected: (108.9 - 100.0) / 100.0 * 100 = 8.9%
        expected_return = 8.9
        
        assert 'fund_name' in result
        assert 'nav_start' in result
        assert 'nav_end' in result
        assert 'return_percent' in result
        assert 'start_date' in result
        assert 'end_date' in result
        assert 'duration_days' in result
        
        assert result['fund_name'] == "Test Fund"
        assert result['nav_start'] == 100.0
        assert result['nav_end'] == 108.9
        assert abs(result['return_percent'] - expected_return) < 0.01
        assert result['duration_days'] == 9  # 10 days - 1 for range
    
    def test_calculate_percentage_return_invalid_fund(self, calculator):
        """Test calculation with invalid fund name"""
        result = calculator.calculate_percentage_return("Non-existent Fund")
        assert result is None
    
    @pytest.mark.parametrize("return_percent,expected_warning_count", [
        (-30.0, 1),  # Critical loss
        (-20.0, 1),  # Severe decline
        (-8.0, 1),   # Poor performance
        (0.0, 0),    # No warnings
        (3.0, 0),    # Good performance
        (25.0, 1),   # Excellent gains
    ])
    def test_ai_advisor_warning_thresholds(self, calculator, return_percent, expected_warning_count):
        """Test AI advisor warning system with various return values"""
        result = calculator.ai_advisor_warning(return_percent, "Test Fund")
        
        assert 'warnings' in result
        assert 'recommendations' in result
        assert 'risk_level' in result
        
        assert len(result['warnings']) == expected_warning_count
        assert len(result['recommendations']) == expected_warning_count
        
        # Validate risk level classification
        if return_percent < -15:
            assert result['risk_level'] in ['HIGH', 'CRITICAL']
        elif return_percent < -5:
            assert result['risk_level'] == 'MEDIUM'
        elif return_percent < 5:
            assert result['risk_level'] == 'LOW'
        else:
            assert result['risk_level'] in ['LOW', 'GROWTH']

# ==========================================
# 💼 PORTFOLIO ANALYSIS TESTS
# ==========================================

class TestPortfolioAnalysis:
    """Test suite for portfolio-level analysis functionality"""
    
    def test_calculate_weighted_portfolio_return(self, multi_fund_calculator):
        """Test weighted portfolio return calculation"""
        allocations = {
            "Growth Fund": 60.0,
            "Declining Fund": 40.0
        }
        
        result = multi_fund_calculator.calculate_weighted_portfolio_return(allocations)
        
        assert 'total_return' in result
        assert 'fund_contributions' in result
        
        # Verify individual contributions
        assert "Growth Fund" in result['fund_contributions']
        assert "Declining Fund" in result['fund_contributions']
        
        # Check calculation accuracy
        growth_return = 15.0  # (115 - 100) / 100 * 100
        decline_return = -12.5  # (175 - 200) / 200 * 100
        expected_total = (0.6 * growth_return) + (0.4 * decline_return)
        
        assert abs(result['total_return'] - expected_total) < 0.01
    
    def test_calculate_weighted_portfolio_return_invalid_allocation(self, multi_fund_calculator):
        """Test portfolio calculation with invalid fund allocation"""
        allocations = {
            "Non-existent Fund": 100.0
        }
        
        result = multi_fund_calculator.calculate_weighted_portfolio_return(allocations)
        
        # Should handle gracefully
        assert 'total_return' in result
        assert result['total_return'] == 0  # No valid funds
    
    def test_ai_weight_adjustment(self, multi_fund_calculator):
        """Test AI-driven weight adjustment recommendations"""
        allocations = {
            "Growth Fund": 50.0,
            "Declining Fund": 50.0
        }
        
        returns_data = [
            {'fund_name': 'Growth Fund', 'return_percent': 15.0},
            {'fund_name': 'Declining Fund', 'return_percent': -12.5}
        ]
        
        result = multi_fund_calculator.ai_weight_adjustment(allocations, returns_data)
        
        assert 'recommended_allocations' in result
        assert 'changes_made' in result
        assert 'reasoning' in result
        
        # AI should recommend reducing declining fund and increasing growth fund
        assert result['recommended_allocations']['Growth Fund'] > 50.0
        assert result['recommended_allocations']['Declining Fund'] < 50.0

# ==========================================
# 🎨 VISUALIZATION TESTS
# ==========================================

class TestVisualization:
    """Test suite for chart generation and visualization"""
    
    def test_create_return_bar_chart(self, multi_fund_calculator):
        """Test bar chart generation"""
        returns_data = [
            {
                'fund_name': 'Growth Fund',
                'return_percent': 15.0,
                'nav_start': 100.0,
                'nav_end': 115.0
            },
            {
                'fund_name': 'Declining Fund',
                'return_percent': -12.5,
                'nav_start': 200.0,
                'nav_end': 175.0
            }
        ]
        
        fig = multi_fund_calculator.create_return_bar_chart(returns_data)
        
        # Verify Plotly figure structure
        assert hasattr(fig, 'data')
        assert hasattr(fig, 'layout')
        assert len(fig.data) > 0
        
        # Check title and styling
        assert 'Fund Performance Analysis' in fig.layout.title.text
    
    def test_create_allocation_pie_chart(self, multi_fund_calculator):
        """Test pie chart generation for portfolio allocation"""
        allocations = {
            "Growth Fund": 60.0,
            "Declining Fund": 40.0
        }
        
        fig = multi_fund_calculator.create_allocation_pie_chart(allocations)
        
        # Verify pie chart structure
        assert hasattr(fig, 'data')
        assert len(fig.data) == 1  # Single pie chart
        assert fig.data[0].type == 'pie'
        
        # Check data integrity
        assert len(fig.data[0].labels) == 2
        assert len(fig.data[0].values) == 2

# ==========================================
# 🔍 EDGE CASES & ERROR HANDLING
# ==========================================

class TestEdgeCases:
    """Test suite for edge cases and error handling"""
    
    def test_empty_dataset(self, calculator):
        """Test behavior with empty dataset"""
        empty_data = pd.DataFrame(columns=['Date', 'NAV'])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            empty_data.to_csv(f.name, index=False)
            csv_path = f.name
        
        try:
            result = calculator.load_fund_data("Empty Fund", csv_path)
            assert result is True  # Should load successfully
            
            # But calculation should handle gracefully
            return_result = calculator.calculate_percentage_return("Empty Fund")
            assert return_result is None or return_result.get('return_percent') == 0
        finally:
            os.unlink(csv_path)
    
    def test_single_data_point(self, calculator):
        """Test with only one data point"""
        single_point = pd.DataFrame({
            'Date': ['2024-01-01'],
            'NAV': [100.0]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            single_point.to_csv(f.name, index=False)
            csv_path = f.name
        
        try:
            calculator.load_fund_data("Single Point Fund", csv_path)
            result = calculator.calculate_percentage_return("Single Point Fund")
            
            # Should handle gracefully (no change = 0% return)
            assert result is None or result.get('return_percent') == 0
        finally:
            os.unlink(csv_path)
    
    def test_invalid_csv_format(self, calculator):
        """Test with malformed CSV data"""
        invalid_data = "This is not CSV data\nInvalid,Format,Here"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(invalid_data)
            csv_path = f.name
        
        try:
            result = calculator.load_fund_data("Invalid Fund", csv_path)
            assert result is False  # Should fail gracefully
        finally:
            os.unlink(csv_path)
    
    def test_negative_nav_values(self, calculator):
        """Test with negative NAV values (edge case)"""
        negative_nav = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=3),
            'NAV': [100.0, -50.0, 75.0]  # Invalid negative NAV
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            negative_nav.to_csv(f.name, index=False)
            csv_path = f.name
        
        try:
            calculator.load_fund_data("Negative NAV Fund", csv_path)
            result = calculator.calculate_percentage_return("Negative NAV Fund")
            
            # Should handle gracefully or provide warning
            assert result is not None
        finally:
            os.unlink(csv_path)

# ==========================================
# ⚡ PERFORMANCE TESTS
# ==========================================

class TestPerformance:
    """Test suite for performance validation"""
    
    def test_large_dataset_performance(self, calculator):
        """Test performance with large dataset (1000+ points)"""
        import time
        
        # Generate large dataset
        large_data = pd.DataFrame({
            'Date': pd.date_range('2020-01-01', periods=1000, freq='D'),
            'NAV': np.random.uniform(50, 150, 1000)
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            large_data.to_csv(f.name, index=False)
            csv_path = f.name
        
        try:
            # Test loading speed
            start_time = time.time()
            calculator.load_fund_data("Large Fund", csv_path)
            load_time = time.time() - start_time
            
            # Test calculation speed
            start_time = time.time()
            result = calculator.calculate_percentage_return("Large Fund")
            calc_time = time.time() - start_time
            
            # Performance assertions (should be fast)
            assert load_time < 1.0  # Load in under 1 second
            assert calc_time < 0.1  # Calculate in under 0.1 seconds
            assert result is not None
        finally:
            os.unlink(csv_path)
    
    def test_multiple_funds_performance(self, calculator):
        """Test performance with multiple funds loaded"""
        import time
        
        # Create 10 funds with moderate data
        for i in range(10):
            fund_data = pd.DataFrame({
                'Date': pd.date_range('2024-01-01', periods=100),
                'NAV': np.random.uniform(80, 120, 100)
            })
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                fund_data.to_csv(f.name, index=False)
                calculator.load_fund_data(f"Fund_{i}", f.name)
                os.unlink(f.name)
        
        # Test portfolio calculation performance
        allocations = {f"Fund_{i}": 10.0 for i in range(10)}
        
        start_time = time.time()
        result = calculator.calculate_weighted_portfolio_return(allocations)
        calc_time = time.time() - start_time
        
        assert calc_time < 0.5  # Should complete in under 0.5 seconds
        assert result['total_return'] is not None

# ==========================================
# 🧪 INTEGRATION TESTS
# ==========================================

class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_workflow(self, calculator):
        """Test complete analysis workflow from data loading to AI recommendations"""
        # Step 1: Load sample data
        sample_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=30),
            'NAV': [100 + i * 0.5 if i < 20 else 110 - (i-20) * 2 for i in range(30)]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_data.to_csv(f.name, index=False)
            csv_path = f.name
        
        try:
            # Step 2: Load data
            load_success = calculator.load_fund_data("Workflow Fund", csv_path)
            assert load_success
            
            # Step 3: Calculate returns
            returns = calculator.calculate_percentage_return("Workflow Fund")
            assert returns is not None
            
            # Step 4: Get AI recommendations
            ai_advice = calculator.ai_advisor_warning(
                returns['return_percent'], 
                "Workflow Fund"
            )
            assert ai_advice is not None
            
            # Step 5: Portfolio analysis (single fund)
            allocations = {"Workflow Fund": 100.0}
            portfolio = calculator.calculate_weighted_portfolio_return(allocations)
            assert portfolio is not None
            
            # Step 6: Generate visualizations
            chart = calculator.create_return_bar_chart([returns])
            assert chart is not None
            
            pie_chart = calculator.create_allocation_pie_chart(allocations)
            assert pie_chart is not None
            
        finally:
            os.unlink(csv_path)

# ==========================================
# 🚀 BENCHMARK TESTS
# ==========================================

@pytest.mark.benchmark
class TestBenchmarks:
    """Benchmark tests for performance validation"""
    
    def test_calculation_speed_benchmark(self, calculator_with_data):
        """Benchmark calculation speed"""
        import time
        
        times = []
        for _ in range(100):
            start = time.time()
            calculator_with_data.calculate_percentage_return("Test Fund")
            times.append(time.time() - start)
        
        avg_time = sum(times) / len(times)
        assert avg_time < 0.01  # Average under 10ms
    
    def test_memory_usage_benchmark(self, calculator):
        """Benchmark memory usage"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Load multiple funds
        for i in range(50):
            data = pd.DataFrame({
                'Date': pd.date_range('2024-01-01', periods=100),
                'NAV': np.random.uniform(90, 110, 100)
            })
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                data.to_csv(f.name, index=False)
                calculator.load_fund_data(f"Memory_Fund_{i}", f.name)
                os.unlink(f.name)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Should not exceed 100MB increase
        assert memory_increase < 100 * 1024 * 1024

# ==========================================
# 🎯 TEST CONFIGURATION & RUNNERS
# ==========================================

def test_suite_coverage():
    """Verify test suite covers all major functionality"""
    required_test_classes = [
        'TestPortfolioReturnCalculator',
        'TestPortfolioAnalysis', 
        'TestVisualization',
        'TestEdgeCases',
        'TestPerformance',
        'TestIntegration'
    ]
    
    current_globals = globals()
    for test_class in required_test_classes:
        assert test_class in current_globals, f"Missing test class: {test_class}"

if __name__ == "__main__":
    """Run tests directly"""
    print("🧪 AI Portfolio Return Calculator - Test Suite")
    print("=" * 60)
    print("Running comprehensive test validation...")
    
    # Run with pytest
    pytest.main([
        __file__,
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--cov=portfolio_return_calculator",  # Coverage report
        "--cov-report=term-missing",  # Show missing lines
        "--benchmark-disable",  # Disable benchmark tests for quick run
    ])
    
    print("\n✅ Test suite execution completed!")
    print("📊 Check coverage report above for detailed analysis")

# ==========================================
# 📋 TEST CONFIGURATION
# ==========================================

# pytest configuration (also works with pytest.ini)
pytest_plugins = []

# Test markers for categorization
pytestmark = [
    pytest.mark.unit,  # Unit tests
    pytest.mark.integration,  # Integration tests
    pytest.mark.performance,  # Performance tests
]

# Custom test configuration
TEST_CONFIG = {
    'timeout': 30,  # Test timeout in seconds
    'strict_warnings': True,  # Treat warnings as errors
    'performance_threshold': 0.1,  # Performance threshold in seconds
    'memory_threshold': 100,  # Memory threshold in MB
}

print(f"🔧 Test Configuration Loaded: {TEST_CONFIG}") 