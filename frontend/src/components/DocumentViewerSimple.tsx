import React, { useState, useEffect } from 'react';
import { FileText, ChevronLeft, ChevronRight, Download, Eye, FileSpreadsheet } from 'lucide-react';
import axios from 'axios';
import config from '../config';
import ExcelPreview from './ExcelPreview';
import './DocumentViewer.css';

interface DocumentViewerProps {
  documentIds: string[];
}

const DocumentViewerSimple: React.FC<DocumentViewerProps> = ({ documentIds }) => {
  const [currentDocIndex, setCurrentDocIndex] = useState(0);
  const [documentData, setDocumentData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  console.log('DocumentViewerSimple received documentIds:', documentIds);

  useEffect(() => {
    if (documentIds.length > 0) {
      console.log('Loading document at index:', currentDocIndex, 'ID:', documentIds[currentDocIndex]);
      loadDocument(documentIds[currentDocIndex]);
    }
  }, [currentDocIndex, documentIds]);

  const loadDocument = async (docId: string) => {
    setLoading(true);
    setError(null);
    try {
      console.log('Loading document:', docId);
      const response = await axios.get(`${config.API_URL}/document/${docId}/base64`);
      console.log('Document loaded successfully:', response.data.filename);
      setDocumentData(response.data);
    } catch (error: any) {
      console.error('Error loading document:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to load document';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const goToPrevDocument = () => {
    if (currentDocIndex > 0) {
      setCurrentDocIndex(currentDocIndex - 1);
    }
  };

  const goToNextDocument = () => {
    if (currentDocIndex < documentIds.length - 1) {
      setCurrentDocIndex(currentDocIndex + 1);
    }
  };

  const downloadDocument = () => {
    if (documentData) {
      const link = document.createElement('a');
      link.href = `data:${documentData.content_type};base64,${documentData.content}`;
      // Clean the filename by removing tmp prefix
      const cleanFilename = documentData.filename.replace(/^tmp[a-z0-9_]+/i, '');
      link.download = cleanFilename;
      link.click();
    }
  };

  const openInNewTab = () => {
    if (documentData) {
      if (documentData.content_type === 'application/pdf') {
        const dataUrl = `data:${documentData.content_type};base64,${documentData.content}`;
        window.open(dataUrl, '_blank');
      } else {
        // For Excel files, trigger download instead
        downloadDocument();
      }
    }
  };

  if (documentIds.length === 0) {
    return (
      <div className="document-viewer no-documents">
        <FileText size={48} />
        <p>No documents to display</p>
      </div>
    );
  }

  return (
    <div className="document-viewer">
      <div className="viewer-header">
        <h3>Document Preview</h3>
        <div className="viewer-controls">
          <button 
            onClick={goToPrevDocument} 
            disabled={currentDocIndex === 0}
            className="nav-btn"
          >
            <ChevronLeft size={20} />
          </button>
          <span className="doc-info">
            Document {currentDocIndex + 1} of {documentIds.length}
          </span>
          <button 
            onClick={goToNextDocument} 
            disabled={currentDocIndex === documentIds.length - 1}
            className="nav-btn"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      <div className="document-content">
        {loading ? (
          <div className="loading">Loading document...</div>
        ) : error ? (
          <div className="error-message" style={{ textAlign: 'center', padding: '2rem', color: '#e53e3e' }}>
            <p>Error: {error}</p>
            <button onClick={() => loadDocument(documentIds[currentDocIndex])} style={{ marginTop: '1rem', padding: '0.5rem 1rem', background: '#667eea', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Retry
            </button>
          </div>
        ) : documentData ? (
          documentData.excel_preview ? (
            // For Excel files with preview, show the table directly
            <ExcelPreview 
              data={documentData.excel_preview} 
              filename={documentData.filename}
              onDownload={downloadDocument}
            />
          ) : (
            // For PDFs and Excel files without preview
            <div className="document-preview">
              <div className="document-icon">
                {documentData.content_type === 'application/pdf' ? (
                  <FileText size={80} style={{ color: '#dc2626' }} />
                ) : (
                  <FileSpreadsheet size={80} style={{ color: '#16a34a' }} />
                )}
              </div>
              <h3>{documentData.filename.replace(/^tmp[a-z0-9_]+/i, '')}</h3>
              <p className="document-type">
                {documentData.content_type === 'application/pdf' ? 'PDF Document' : 'Excel Spreadsheet'}
              </p>
              
              <div className="document-actions">
                {documentData.content_type === 'application/pdf' ? (
                  <>
                    <button onClick={openInNewTab} className="action-btn view-btn">
                      <Eye size={20} /> View in Browser
                    </button>
                    <button onClick={downloadDocument} className="action-btn download-btn">
                      <Download size={20} /> Download
                    </button>
                  </>
                ) : (
                  <button onClick={downloadDocument} className="action-btn download-btn" style={{ width: '200px' }}>
                    <Download size={20} /> Download Excel File
                  </button>
                )}
              </div>

              {documentData.content_type === 'application/pdf' && (
                <div className="pdf-embed">
                  <p style={{ marginTop: '20px', color: '#666', fontSize: '14px' }}>
                    PDF preview below (or use buttons above):
                  </p>
                  {/* Try iframe, but it may not work in all browsers due to security restrictions */}
                  <iframe 
                    src={`data:application/pdf;base64,${documentData.content}`}
                    width="100%"
                    height="600"
                    title="PDF Preview"
                    style={{ border: '1px solid #ddd', borderRadius: '4px', marginTop: '20px' }}
                    onError={() => console.log('Iframe failed to load PDF. Use View in Browser button instead.')}
                  />
                </div>
              )}

              {documentData.content_type !== 'application/pdf' && !documentData.excel_preview && (
                <div style={{ marginTop: '30px', padding: '20px', background: '#f3f4f6', borderRadius: '8px' }}>
                  <p style={{ color: '#4b5563', marginBottom: '10px' }}>
                    <strong>Excel Preview Loading...</strong>
                  </p>
                  <p style={{ color: '#6b7280', fontSize: '14px' }}>
                    Please download the file to view it in Microsoft Excel or Google Sheets.
                  </p>
                </div>
              )}
            </div>
          )
        ) : null}
      </div>
    </div>
  );
};

export default DocumentViewerSimple;