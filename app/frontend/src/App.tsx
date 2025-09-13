import React, { useState, useEffect } from "react";
import axios from "axios";
import DocumentUploader from "./components/DocumentUploader";
import ExtractedDataForm from "./components/ExtractedDataForm";
import DocumentViewer from "./components/DocumentViewer";
import DocumentsList from "./components/DocumentsList";

interface ShipmentData {
  bill_of_lading_number?: string | null;
  container_number?: string | null;
  consignee_name?: string | null;
  consignee_address?: string | null;
  date?: string | null;
  line_items_count?: string | null;
  average_gross_weight?: string | null;
  average_price?: string | null;
}

interface DocumentListItem {
  id: string;
  created_at: string;
  last_updated: string;
  has_data: boolean;
  filenames: string[];
  primary_filename: string | null;
}

function App() {
  const [files, setFiles] = useState<File[]>([]);
  const [processing, setProcessing] = useState(false);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [extractedData, setExtractedData] = useState<ShipmentData | null>(null);
  const [documentTexts, setDocumentTexts] = useState<any>({});
  const [fileMetadata, setFileMetadata] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedDocuments, setSavedDocuments] = useState<DocumentListItem[]>([]);
  const [loading, setLoading] = useState(false);

  // Load saved documents on app startup
  useEffect(() => {
    loadSavedDocuments();
  }, []);

  const loadSavedDocuments = async () => {
    try {
      const response = await axios.get("http://localhost:8000/documents");
      setSavedDocuments(response.data.documents || []);
    } catch (err: any) {
      console.error("Error loading saved documents:", err);
    }
  };

  const handleFileSelect = (selectedFiles: File[]) => {
    const validFiles = selectedFiles.filter((file) => {
      const extension = file.name.toLowerCase().split(".").pop();
      return ["pdf", "xlsx", "xls"].includes(extension || "");
    });

    if (validFiles.length !== selectedFiles.length) {
      setError(
        "Some files were ignored. Only PDF and Excel files are supported."
      );
    }

    setFiles(validFiles);
    setError(null);
  };

  const processDocuments = async () => {
    if (files.length === 0) {
      setError("Please select files to process");
      return;
    }

    setProcessing(true);
    setError(null);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await axios.post("http://localhost:8000/process-documents", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      console.log(response.data);

      // Document ID will be set when user saves manually
      setExtractedData(response.data.extracted_data);
      setDocumentTexts(response.data.document_texts || {});
      setFileMetadata(response.data.file_metadata || []);
    } catch (err: any) {
      setError(
        `Error processing documents: ${
          err.response?.data?.detail || err.message
        }`
      );
    } finally {
      setProcessing(false);
    }
  };

  const updateField = (field: keyof ShipmentData, value: string) => {
    // Just update local state - no backend save until user clicks Save
    setExtractedData((prev) =>
      prev
        ? {
            ...prev,
            [field]: value,
          }
        : null
    );
  };

  const saveDocument = async () => {
    if (!extractedData || !documentTexts) {
      setError("No data to save");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      const response = await axios.post("http://localhost:8000/documents/save", {
        extracted_data: extractedData,
        document_texts: documentTexts,
        file_metadata: fileMetadata
      });

      setDocumentId(response.data.document_id);
      // Reload the documents list to include the new document
      await loadSavedDocuments();
      // Show success message or update UI
      console.log("Document saved successfully:", response.data.document_id);
    } catch (err: any) {
      setError(
        `Error saving document: ${
          err.response?.data?.detail || err.message
        }`
      );
    } finally {
      setSaving(false);
    }
  };

  const selectDocument = async (docId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`http://localhost:8000/documents/${docId}`);
      const documentData = response.data;
      
      setDocumentId(docId);
      setExtractedData(documentData.extracted_data || {});
      setDocumentTexts(documentData.document_texts || {});
      setFileMetadata(documentData.file_metadata || []);
      
      // Clear any current file selection since we're loading from saved
      setFiles([]);
    } catch (err: any) {
      setError(
        `Error loading document: ${
          err.response?.data?.detail || err.message
        }`
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-blue-600 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <svg
                  className="h-8 w-8 text-white mr-3"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <h1 className="text-white text-xl font-semibold">
                  Shipment Document Processor
                </h1>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Sidebar - Saved Documents */}
            <div className="lg:col-span-2">
              <DocumentsList
                documents={savedDocuments}
                onSelectDocument={selectDocument}
                selectedDocumentId={documentId}
                loading={loading}
              />
            </div>

            {/* Middle Column - Upload and Form */}
            <div className="lg:col-span-4 space-y-6">
              <DocumentUploader
                files={files}
                onFileSelect={handleFileSelect}
                onProcess={processDocuments}
                processing={processing}
                error={error}
              />

              {extractedData && (
                <ExtractedDataForm
                  data={extractedData}
                  onUpdateField={updateField}
                  onSave={saveDocument}
                  saving={saving}
                />
              )}
            </div>

            {/* Right Column - Document Viewer (Now Much Wider) */}
            <div className="lg:col-span-6">
              {Object.keys(documentTexts).length > 0 && (
                <DocumentViewer 
                  documentTexts={documentTexts} 
                  fileMetadata={fileMetadata}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
