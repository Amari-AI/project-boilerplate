import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import DataEditor from './components/DataEditor';
import DocumentPanel from './components/DocumentPanel';
import './App.css';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [extractedData, setExtractedData] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleFilesUploaded = (files) => {
    setUploadedFiles(prev => [...prev, ...files]);
  };

  const handleDataExtracted = (data) => {
    setExtractedData(data);
    setIsProcessing(false);
  };

  const handleProcessingStart = () => {
    setIsProcessing(true);
  };

  const handleDataUpdate = (updatedData) => {
    setExtractedData(updatedData);
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="app">
      <div className="app-header">
        <h1>Document Processing App</h1>
        <p>Upload your documents to extract and edit invoice and bill of lading data</p>
      </div>
      
      <div className="app-layout">
        <div className="main-content">
          <FileUpload 
            onFilesUploaded={handleFilesUploaded}
            onDataExtracted={handleDataExtracted}
            onProcessingStart={handleProcessingStart}
            uploadedFiles={uploadedFiles}
            isProcessing={isProcessing}
          />
          
          {isProcessing && (
            <div className="processing-indicator">
              <div className="spinner"></div>
              <p>Processing documents...</p>
            </div>
          )}
          
          {extractedData && (
            <DataEditor 
              data={extractedData}
              onDataUpdate={handleDataUpdate}
            />
          )}
        </div>
        
        <DocumentPanel 
          files={uploadedFiles}
          onRemoveFile={removeFile}
        />
      </div>
    </div>
  );
}

export default App; 