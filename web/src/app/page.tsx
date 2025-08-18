"use client";

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { DocumentForm } from '@/components/DocumentForm';
import { DocumentPreview } from '@/components/DocumentPreview';
import { DocumentPagination } from '@/components/DocumentPagination';
import { FileUpload } from '@/components/FileUpload';
import { useDocuments } from '@/hooks/useDocuments';

export default function Home() {
  const {
    documents,
    currentIndex,
    isProcessing,
    aggregatedFormData,
    addDocuments,
    addMoreDocuments,
    removeDocument,
    processDocuments,
    goToPrevious,
    goToNext,
    resetDocuments,
    getCurrentDocument,
    updateAggregatedFormData,
    hasProcessedDocuments,
  } = useDocuments();

  const currentDocument = getCurrentDocument();

  // Update form when document changes
  useEffect(() => {
    // This will be handled by the DocumentForm component internally
  }, [currentIndex, documents]);

  if (hasProcessedDocuments) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-4">Document Processing Results</h1>
            
            <div className="flex items-center justify-between">
              <Button 
                variant="outline" 
                onClick={resetDocuments}
              >
                Process New Documents
              </Button>
              
              <DocumentPagination
                currentIndex={currentIndex}
                totalDocuments={documents.length}
                onPrevious={goToPrevious}
                onNext={goToNext}
                disabled={isProcessing}
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.25fr] gap-8">
            <DocumentForm
              formData={aggregatedFormData}
              totalDocuments={documents.length}
              onFormChange={updateAggregatedFormData}
            />
            
            <DocumentPreview document={currentDocument} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <FileUpload
        documents={documents}
        isProcessing={isProcessing}
        onFilesChange={addDocuments}
        onAddMoreFiles={addMoreDocuments}
        onRemoveFile={removeDocument}
        onProcess={processDocuments}
      />
    </div>
  );
}