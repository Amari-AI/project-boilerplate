import React from 'react';

interface DocumentListItem {
  id: string;
  created_at: string;
  last_updated: string;
  has_data: boolean;
  filenames: string[];
  primary_filename: string | null;
}

interface DocumentsListProps {
  documents: DocumentListItem[];
  onSelectDocument: (docId: string) => void;
  selectedDocumentId?: string | null;
  loading?: boolean;
}

const DocumentsList: React.FC<DocumentsListProps> = ({ 
  documents, 
  onSelectDocument, 
  selectedDocumentId,
  loading 
}) => {
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Invalid date';
    }
  };

  if (documents.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No saved documents</h3>
          <p className="mt-1 text-sm text-gray-500">Process and save documents to see them here.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 flex items-center">
          <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          Saved Documents
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          Click on a document to view and edit its details
        </p>
      </div>

      <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
        {documents.map((document) => (
          <div
            key={document.id}
            onClick={() => onSelectDocument(document.id)}
            className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
              selectedDocumentId === document.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
            } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center">
                  <svg className="h-5 w-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-gray-900 truncate max-w-40" title={document.primary_filename || document.id}>
                      {document.primary_filename || `Document ${document.id.substring(0, 8)}...`}
                    </p>
                    {document.filenames.length > 1 && (
                      <p className="text-xs text-gray-400">
                        +{document.filenames.length - 1} more file{document.filenames.length > 2 ? 's' : ''}
                      </p>
                    )}
                    <p className="text-xs text-gray-500">
                      Created: {formatDate(document.created_at)}
                    </p>
                    {document.last_updated !== document.created_at && (
                      <p className="text-xs text-gray-500">
                        Updated: {formatDate(document.last_updated)}
                      </p>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {document.has_data && (
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Data
                  </span>
                )}
                
                <svg className="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DocumentsList;