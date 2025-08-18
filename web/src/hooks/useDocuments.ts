import { useState } from 'react';
import { toast } from 'sonner';
import { DocumentData, DocumentFormData, DocumentProcessingState, ExtractedData } from '@/types';
import { aggregateExtractedData } from '@/lib/dataTransform';
import { analyzeFile, generateFileFingerprint } from '@/lib/fileAnalysis';

export function useDocuments() {
  const [state, setState] = useState<DocumentProcessingState>({
    documents: [],
    currentIndex: 0,
    isProcessing: false,
    aggregatedFormData: null,
  });

  const isDuplicateFile = (file: File, existingDocuments: DocumentData[]): boolean => {
    const fingerprint = generateFileFingerprint(file);
    return existingDocuments.some(doc => doc.stats.fingerprint === fingerprint);
  };

  const addDocuments = async (files: File[]) => {
    const validFiles: DocumentData[] = [];
    let invalidCount = 0;
    let duplicateCount = 0;

    for (const file of files) {
      const fileType = file.type;
      const fileName = file.name.toLowerCase();
      
      // First check if it's a valid file type
      if (
        fileType === "application/pdf" ||
        fileType === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
        fileType === "application/vnd.ms-excel" ||
        fileName.endsWith('.pdf') ||
        fileName.endsWith('.xlsx') ||
        fileName.endsWith('.xls')
      ) {
        // Check for duplicates (including in the current batch)
        if (isDuplicateFile(file, state.documents) || isDuplicateFile(file, validFiles)) {
          duplicateCount++;
        } else {
          const stats = await analyzeFile(file);
          validFiles.push({
            id: `${file.name}-${Date.now()}-${Math.random()}`,
            file,
            stats,
            rawApiData: null,
            documentUrl: URL.createObjectURL(file),
            isProcessed: false,
          });
        }
      } else {
        invalidCount++;
      }
    }

    // Show appropriate toast messages
    if (invalidCount > 0) {
      toast.error(`${invalidCount} file(s) skipped. Please select only PDF or Excel files`);
    }
    
    if (duplicateCount > 0) {
      toast.error(`${duplicateCount} duplicate file(s) skipped`);
    }

    if (validFiles.length > 0) {
      setState(prev => ({
        ...prev,
        documents: validFiles,
        currentIndex: 0,
      }));
      toast.success(`${validFiles.length} file(s) selected`);
    }
  };

  const addMoreDocuments = async (files: File[]) => {
    const validFiles: DocumentData[] = [];
    let invalidCount = 0;
    let duplicateCount = 0;

    for (const file of files) {
      const fileType = file.type;
      const fileName = file.name.toLowerCase();
      
      // First check if it's a valid file type
      if (
        fileType === "application/pdf" ||
        fileType === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
        fileType === "application/vnd.ms-excel" ||
        fileName.endsWith('.pdf') ||
        fileName.endsWith('.xlsx') ||
        fileName.endsWith('.xls')
      ) {
        // Check for duplicates (including existing documents and current batch)
        if (isDuplicateFile(file, state.documents) || isDuplicateFile(file, validFiles)) {
          duplicateCount++;
        } else {
          const stats = await analyzeFile(file);
          validFiles.push({
            id: `${file.name}-${Date.now()}-${Math.random()}`,
            file,
            stats,
            rawApiData: null,
            documentUrl: URL.createObjectURL(file),
            isProcessed: false,
          });
        }
      } else {
        invalidCount++;
      }
    }

    // Show appropriate toast messages
    if (invalidCount > 0) {
      toast.error(`${invalidCount} file(s) skipped. Please select only PDF or Excel files`);
    }
    
    if (duplicateCount > 0) {
      toast.error(`${duplicateCount} duplicate file(s) skipped`);
    }

    if (validFiles.length > 0) {
      setState(prev => ({
        ...prev,
        documents: [...prev.documents, ...validFiles],
      }));
      toast.success(`${validFiles.length} additional file(s) added`);
    }
  };

  const removeDocument = (id: string) => {
    setState(prev => {
      const documentToRemove = prev.documents.find(doc => doc.id === id);
      if (documentToRemove) {
        URL.revokeObjectURL(documentToRemove.documentUrl);
      }
      
      const newDocuments = prev.documents.filter(doc => doc.id !== id);
      const newCurrentIndex = prev.currentIndex >= newDocuments.length 
        ? Math.max(0, newDocuments.length - 1) 
        : prev.currentIndex;
      
      return {
        ...prev,
        documents: newDocuments,
        currentIndex: newCurrentIndex,
      };
    });
    toast.success('File removed');
  };

  const processDocuments = async () => {
    if (state.documents.length === 0) return;

    setState(prev => ({ ...prev, isProcessing: true }));
    toast.loading("Processing documents...", { id: "processing" });

    try {
      const formData = new FormData();
      state.documents.forEach(doc => {
        formData.append("files", doc.file);
      });

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/process-documents`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ExtractedData | ExtractedData[] = await response.json();
      
      // Handle response based on API structure
      const processedDocuments = state.documents.map((doc, index) => {
        const apiData = Array.isArray(data) ? data[index] : (index === 0 ? data : null);
        return {
          ...doc,
          rawApiData: apiData,
          isProcessed: true,
        };
      });

      // Aggregate all extracted data into a single form
      const allExtractedData = processedDocuments.map(doc => doc.rawApiData);
      const aggregatedFormData = aggregateExtractedData(allExtractedData);

      setState(prev => ({
        ...prev,
        documents: processedDocuments,
        aggregatedFormData,
        isProcessing: false,
      }));
      
      toast.success("Documents processed successfully!", { id: "processing" });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to process documents";
      toast.error(errorMessage, { id: "processing" });
      setState(prev => ({ ...prev, isProcessing: false }));
    }
  };

  const goToDocument = (index: number) => {
    if (index >= 0 && index < state.documents.length) {
      setState(prev => ({ ...prev, currentIndex: index }));
    }
  };

  const goToPrevious = () => {
    setState(prev => ({
      ...prev,
      currentIndex: Math.max(0, prev.currentIndex - 1),
    }));
  };

  const goToNext = () => {
    setState(prev => ({
      ...prev,
      currentIndex: Math.min(prev.documents.length - 1, prev.currentIndex + 1),
    }));
  };

  const resetDocuments = () => {
    // Cleanup object URLs
    state.documents.forEach(doc => {
      URL.revokeObjectURL(doc.documentUrl);
    });
    
    setState({
      documents: [],
      currentIndex: 0,
      isProcessing: false,
      aggregatedFormData: null,
    });
  };

  const getCurrentDocument = (): DocumentData | null => {
    return state.documents[state.currentIndex] || null;
  };
  const updateAggregatedFormData = (formData: DocumentFormData) => {
    setState(prev => ({
      ...prev,
      aggregatedFormData: formData,
    }));
  };

  const hasProcessedDocuments = state.documents.some(doc => doc.isProcessed);

  return {
    ...state,
    addDocuments,
    addMoreDocuments,
    removeDocument,
    processDocuments,
    goToDocument,
    goToPrevious,
    goToNext,
    resetDocuments,
    getCurrentDocument,
    updateAggregatedFormData,
    hasProcessedDocuments,
  };
}