import React, { useState } from 'react';
import './App.css';
import DocumentUploader from './components/DocumentUploader';
import ShipmentForm from './components/ShipmentForm';
import DocumentViewerSimple from './components/DocumentViewerSimple';
import { ShipmentData } from './types';

function App() {
  const [shipmentData, setShipmentData] = useState<ShipmentData | null>(null);
  const [documentIds, setDocumentIds] = useState<string[]>([]);
  const [sessionId, setSessionId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleDocumentsProcessed = (data: any) => {
    console.log('App received data:', data);
    console.log('Document IDs:', data.document_ids);
    setShipmentData(data.shipment_data);
    setDocumentIds(data.document_ids || []);
    setSessionId(data.metadata?.session_id || '');
  };

  const handleDataUpdate = (updatedData: ShipmentData) => {
    setShipmentData(updatedData);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Shipment Document Processing Platform</h1>
      </header>
      
      <div className="container">
        {!shipmentData ? (
          <DocumentUploader 
            onDocumentsProcessed={handleDocumentsProcessed}
            setIsLoading={setIsLoading}
          />
        ) : (
          <div className="main-content">
            <div className="left-panel">
              <ShipmentForm 
                data={shipmentData}
                onUpdate={handleDataUpdate}
                sessionId={sessionId}
              />
              <button 
                className="reset-btn"
                onClick={() => {
                  setShipmentData(null);
                  setDocumentIds([]);
                  setSessionId('');
                }}
              >
                Process New Documents
              </button>
            </div>
            
            <div className="right-panel">
              <DocumentViewerSimple documentIds={documentIds} />
            </div>
          </div>
        )}
      </div>
      
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner">Processing documents...</div>
        </div>
      )}
    </div>
  );
}

export default App;