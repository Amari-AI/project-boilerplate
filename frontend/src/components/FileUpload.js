import React, { useState, useRef } from 'react';
import axios from 'axios';
import './FileUpload.css';

const FileUpload = ({ onFilesUploaded, onDataExtracted, onProcessingStart, uploadedFiles, isProcessing }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  const handleFiles = (files) => {
    const validFiles = files.filter(file => 
      file.type === 'application/pdf' || 
      file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    );
    
    if (validFiles.length > 0) {
      onFilesUploaded(validFiles);
    }
  };

  const processDocuments = async () => {
    if (uploadedFiles.length === 0) return;

    onProcessingStart();
    
    const formData = new FormData();
    uploadedFiles.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await axios.post('/process-documents', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      onDataExtracted(response.data);
    } catch (error) {
      console.error('Error processing documents:', error);
      alert('Error processing documents. Please try again.');
      onDataExtracted(null);
    }
  };

  return (
    <div className="file-upload-container">
      <div 
        className={`file-upload-area ${isDragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="upload-icon">📁</div>
        <h3>Upload Documents</h3>
        <p>Drag and drop PDF or Excel files here, or click to browse</p>
        <p className="file-types">Supported: PDF (.pdf), Excel (.xlsx)</p>
        
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.xlsx"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
      </div>

      {uploadedFiles.length > 0 && (
        <div className="upload-actions">
          <button 
            className="process-btn"
            onClick={processDocuments}
            disabled={isProcessing}
          >
            {isProcessing ? 'Processing...' : `Process ${uploadedFiles.length} Document${uploadedFiles.length > 1 ? 's' : ''}`}
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload; 