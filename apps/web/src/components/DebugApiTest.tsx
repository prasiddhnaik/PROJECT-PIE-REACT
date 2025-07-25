import React, { useState } from 'react';

const DebugApiTest: React.FC = () => {
  const [testResult, setTestResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const testApiConnection = async () => {
    setLoading(true);
    setTestResult('Testing...');
    
    try {
      // Test basic health endpoint
      const healthResponse = await fetch('http://localhost:8001/health');
      const healthData = await healthResponse.json();
      
      // Test crypto endpoint
      const cryptoResponse = await fetch('http://localhost:8001/api/crypto/btc/history?days=7');
      const cryptoData = await cryptoResponse.json();
      
      setTestResult(`✅ API Connection Successful!\n\nHealth: ${JSON.stringify(healthData, null, 2)}\n\nCrypto Data Points: ${cryptoData.history?.length || 'N/A'}`);
    } catch (error) {
      setTestResult(`❌ API Connection Failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded-lg">
      <h3 className="text-lg font-semibold mb-4">🔧 API Debug Test</h3>
      <button 
        onClick={testApiConnection}
        disabled={loading}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? 'Testing...' : 'Test API Connection'}
      </button>
      
      {testResult && (
        <pre className="mt-4 p-4 bg-gray-100 rounded text-sm whitespace-pre-wrap">
          {testResult}
        </pre>
      )}
    </div>
  );
};

export default DebugApiTest; 