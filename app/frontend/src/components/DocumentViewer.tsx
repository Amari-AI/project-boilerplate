import React, { useState } from 'react';

interface DocumentViewerProps {
  documentTexts: { [key: string]: any };
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ documentTexts }) => {
  const [activeDocument, setActiveDocument] = useState<string | null>(null);

  const renderDocumentContent = (filename: string, content: any) => {
    if (typeof content === 'string') {
      // PDF content or simple text
      return (
        <div className="font-mono text-xs whitespace-pre-wrap max-h-96 overflow-y-auto">
          {content.length > 2000 ? `${content.substring(0, 2000)}...` : content}
        </div>
      );
    } else if (typeof content === 'object') {
      // XLSX content
      return (
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {Object.entries(content).map(([sheetName, rows]: [string, any]) => (
            <div key={sheetName} className="border rounded-md">
              <div className="bg-gray-100 px-3 py-2 font-medium text-sm border-b">
                📊 {sheetName}
              </div>
              <div className="p-3">
                <div className="text-xs space-y-1">
                  {rows.slice(0, 10).map((row: any[], idx: number) => (
                    <div key={idx} className="grid grid-cols-1 gap-1">
                      <div className="text-gray-600">
                        <span className="font-medium">Row {idx + 1}:</span>
                      </div>
                      <div className="pl-4 text-gray-800 break-words">
                        {row.filter(cell => cell && cell.trim()).join(' | ')}
                      </div>
                    </div>
                  ))}
                  {rows.length > 10 && (
                    <div className="text-gray-500 italic">
                      ... and {rows.length - 10} more rows
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  const getFileIcon = (filename: string) => {
    if (filename.toLowerCase().includes('pdf')) {
      return (
        <svg className="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
        </svg>
      );
    } else {
      return (
        <svg className="h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
        </svg>
      );
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 flex items-center">
          <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Document Preview
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          Review extracted content for accuracy
        </p>
      </div>

      <div className="p-6">
        {/* Document Tabs */}
        {Object.keys(documentTexts).length > 1 && (
          <div className="flex space-x-1 mb-4">
            {Object.keys(documentTexts).map((filename) => (
              <button
                key={filename}
                onClick={() => setActiveDocument(activeDocument === filename ? null : filename)}
                className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                  activeDocument === filename
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                {getFileIcon(filename)}
                <span className="ml-2 truncate max-w-24">
                  {filename.replace(/^(pdf_|xlsx_)/, '').split('.')[0]}
                </span>
              </button>
            ))}
          </div>
        )}

        {/* Document Content */}
        <div className="space-y-4">
          {Object.entries(documentTexts).map(([filename, content]) => {
            // Show all documents if there's only one, or show the selected one
            const shouldShow = Object.keys(documentTexts).length === 1 || 
                             activeDocument === filename || 
                             activeDocument === null;
            
            if (!shouldShow) return null;

            return (
              <div key={filename} className="border rounded-lg">
                <div className="bg-gray-50 px-4 py-3 border-b flex items-center justify-between">
                  <div className="flex items-center">
                    {getFileIcon(filename)}
                    <span className="ml-2 text-sm font-medium text-gray-900">
                      {filename.replace(/^(pdf_|xlsx_)/, '')}
                    </span>
                  </div>
                  <button
                    onClick={() => setActiveDocument(activeDocument === filename ? null : filename)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    {activeDocument === filename ? (
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                      </svg>
                    ) : (
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    )}
                  </button>
                </div>
                
                {(activeDocument === filename || Object.keys(documentTexts).length === 1) && (
                  <div className="p-4">
                    {renderDocumentContent(filename, content)}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {Object.keys(documentTexts).length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="mt-2">No documents to preview</p>
            <p className="text-sm">Upload and process documents to see content here</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentViewer;