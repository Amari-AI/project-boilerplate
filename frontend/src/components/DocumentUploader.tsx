import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { Upload } from 'lucide-react';
import config from '../config';
import './DocumentUploader.css';

interface DocumentUploaderProps {
  onDocumentsProcessed: (data: any) => void;
  setIsLoading: (loading: boolean) => void;
}

const DocumentUploader: React.FC<DocumentUploaderProps> = ({ onDocumentsProcessed, setIsLoading }) => {
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    setIsLoading(true);
    const formData = new FormData();
    
    acceptedFiles.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await axios.post(`${config.API_URL}/process-documents`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Documents processed response:', response.data);
      onDocumentsProcessed(response.data);
    } catch (error: any) {
      console.error('Error uploading documents:', error);
      alert(error.response?.data?.detail || 'Failed to process documents');
    } finally {
      setIsLoading(false);
    }
  }, [onDocumentsProcessed, setIsLoading]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    multiple: true
  });

  return (
    <div className="upload-container">
      <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
        <input {...getInputProps()} />
        <Upload size={48} />
        <h2>Upload Shipment Documents</h2>
        <p>Drag & drop your PDF and Excel files here, or click to select</p>
        <p className="file-types">Supported: PDF (Bill of Lading), XLSX/XLS (Invoice/Packing List)</p>
      </div>
    </div>
  );
};

export default DocumentUploader;