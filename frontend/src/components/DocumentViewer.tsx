import React, { useState, useEffect } from 'react';
import { FileText, ChevronLeft, ChevronRight, Download } from 'lucide-react';
import axios from 'axios';
import config from '../config';
import './DocumentViewer.css';

// Import react-pdf without worker initially
import { Document, Page } from 'react-pdf';

// Disable worker to avoid dynamic import issues
import { pdfjs } from 'react-pdf';
pdfjs.GlobalWorkerOptions.workerSrc = false as any;

interface DocumentViewerProps {
  documentIds: string[];
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ documentIds }) => {
  const [currentDocIndex, setCurrentDocIndex] = useState(0);
  const [documentData, setDocumentData] = useState<any>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [numPages, setNumPages] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [pdfError, setPdfError] = useState<string | null>(null);

  useEffect(() => {
    if (documentIds.length > 0) {
      loadDocument(documentIds[currentDocIndex]);
    }
  }, [currentDocIndex, documentIds]);

  const loadDocument = async (docId: string) => {
    setLoading(true);
    setPdfError(null);
    try {
      const response = await axios.get(`${config.API_URL}/document/${docId}/base64`);
      setDocumentData(response.data);
      setPageNumber(1);
    } catch (error) {
      console.error('Error loading document:', error);
      setPdfError('Failed to load document');
    } finally {
      setLoading(false);
    }
  };

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
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
      link.download = documentData.filename;
      link.click();
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
          <button onClick={downloadDocument} className="download-btn">
            <Download size={20} /> Download
          </button>
        </div>
      </div>

      <div className="document-content">
        {loading ? (
          <div className="loading">Loading document...</div>
        ) : documentData ? (
          documentData.content_type === 'application/pdf' ? (
            <div className="pdf-container">
              <Document
                file={`data:application/pdf;base64,${documentData.content}`}
                onLoadSuccess={onDocumentLoadSuccess}
                onLoadError={(error: Error) => {
                  console.error('PDF load error:', error);
                  setPdfError('Unable to load PDF preview');
                }}
                loading={<div>Loading PDF...</div>}
                error={
                  <div className="pdf-error">
                    <FileText size={48} />
                    <p>Unable to preview PDF</p>
                    <button onClick={downloadDocument} className="download-btn">
                      Download to View
                    </button>
                  </div>
                }
              >
                <Page 
                  pageNumber={pageNumber} 
                  width={600}
                  renderTextLayer={false}
                  renderAnnotationLayer={false}
                />
              </Document>
              
              {numPages && numPages > 1 && (
                <div className="page-controls">
                  <button 
                    onClick={() => setPageNumber(Math.max(1, pageNumber - 1))}
                    disabled={pageNumber <= 1}
                  >
                    Previous Page
                  </button>
                  <span>Page {pageNumber} of {numPages}</span>
                  <button 
                    onClick={() => setPageNumber(Math.min(numPages, pageNumber + 1))}
                    disabled={pageNumber >= numPages}
                  >
                    Next Page
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="excel-preview">
              <FileText size={64} />
              <h4>{documentData.filename}</h4>
              <p>Excel file preview not available</p>
              <button onClick={downloadDocument} className="download-excel-btn">
                Download to View
              </button>
            </div>
          )
        ) : null}
      </div>
    </div>
  );
};

export default DocumentViewer;