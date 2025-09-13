import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface FileMetadata {
  original_filename: string;
  saved_filename: string;
  saved_path: string;
  file_id: string;
}

interface DocumentViewerProps {
  documentTexts: { [key: string]: any };
  fileMetadata?: FileMetadata[];
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ documentTexts, fileMetadata = [] }) => {
  const [activeDocument, setActiveDocument] = useState<string | null>(null);
  const [excelData, setExcelData] = useState<{[key: string]: any}>({});

  // Load Excel data for all Excel files when fileMetadata changes
  useEffect(() => {
    fileMetadata.forEach(file => {
      if (file.original_filename.toLowerCase().endsWith('.xlsx') || file.original_filename.toLowerCase().endsWith('.xls')) {
        loadExcelData(file.saved_filename);
      }
    });
  }, [fileMetadata]);

  const findFileMetadata = (filename: string): FileMetadata | undefined => {
    return fileMetadata.find(file => 
      filename.includes(file.file_id) || filename.includes(file.original_filename)
    );
  };

  const loadExcelData = async (savedFilename: string) => {
    if (excelData[savedFilename]) return; // Already loaded
    
    try {
      const response = await axios.get(`http://localhost:8000/files/${savedFilename}/parsed`);
      setExcelData(prev => ({
        ...prev,
        [savedFilename]: response.data.sheets
      }));
    } catch (error) {
      console.error('Error loading Excel data:', error);
    }
  };

  const renderExcelTable = (sheetData: any) => {
    if (!sheetData || !sheetData.headers || !sheetData.rows) {
      return <p className="text-gray-500">No data available</p>;
    }

    return (
      <div className="overflow-auto max-h-[500px] border rounded-md">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50 sticky top-0 z-10">
            <tr>
              {sheetData.headers.map((header: string, index: number) => (
                <th
                  key={index}
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-r border-gray-200 min-w-[120px]"
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sheetData.rows.map((row: string[], rowIndex: number) => (
              <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50 hover:bg-gray-100'}>
                {row.map((cell: string, cellIndex: number) => (
                  <td
                    key={cellIndex}
                    className="px-4 py-3 text-gray-900 border-r border-gray-200 min-w-[120px] break-words"
                    title={cell}
                  >
                    <div className="max-w-[200px]">
                      {cell}
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        <div className="mt-3 px-4 py-2 bg-gray-50 text-xs text-gray-600 border-t">
          📊 {sheetData.total_rows} rows × {sheetData.total_columns} columns
        </div>
      </div>
    );
  };

  const renderFileContent = (fileData: FileMetadata) => {
    const fileUrl = `http://localhost:8000/files/${fileData.saved_filename}`;
    const isPDF = fileData.original_filename.toLowerCase().endsWith('.pdf');
    const isExcel = fileData.original_filename.toLowerCase().endsWith('.xlsx') || fileData.original_filename.toLowerCase().endsWith('.xls');
    
    if (isPDF) {
      return (
        <div className="w-full">
          <div className="mb-4 p-3 bg-red-50 rounded-md">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <svg className="h-6 w-6 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-gray-900">{fileData.original_filename}</p>
                  <p className="text-xs text-gray-500">PDF Document • Viewing inline</p>
                </div>
              </div>
              <div className="flex space-x-2">
                <a
                  href={fileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700"
                >
                  New Tab
                </a>
                <a
                  href={`${fileUrl}?download=true`}
                  className="px-3 py-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700"
                >
                  Download
                </a>
              </div>
            </div>
          </div>
          <div className="w-full h-[600px] border rounded-md bg-gray-100">
            <iframe
              src={`${fileUrl}#toolbar=1&navpanes=1&scrollbar=1&page=1&zoom=page-fit`}
              className="w-full h-full rounded-md"
              title={fileData.original_filename}
            />
          </div>
          <div className="mt-2 text-xs text-gray-500 text-center">
            PDF is displayed using your browser's built-in PDF viewer. If it doesn't display, try opening in a new tab or downloading.
          </div>
        </div>
      );
    } else if (isExcel) {
      const sheets = excelData[fileData.saved_filename];
      if (!sheets) {
        return (
          <div className="flex items-center justify-center py-8">
            <svg className="animate-spin h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="ml-2 text-gray-500">Loading Excel data...</span>
          </div>
        );
      }

      return (
        <div className="space-y-4">
          <div className="p-3 bg-green-50 rounded-md">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <svg className="h-6 w-6 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-gray-900">{fileData.original_filename}</p>
                  <p className="text-xs text-gray-500">Excel Spreadsheet • {Object.keys(sheets).length} sheet(s)</p>
                </div>
              </div>
              <a
                href={`${fileUrl}?download=true`}
                className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700"
              >
                Download
              </a>
            </div>
          </div>
          
          {Object.entries(sheets).map(([sheetName, sheetData]) => (
            <div key={sheetName} className="border rounded-md">
              <div className="bg-gray-50 px-4 py-2 border-b">
                <h4 className="text-sm font-medium text-gray-900">📊 {sheetName}</h4>
              </div>
              <div className="p-4">
                {renderExcelTable(sheetData)}
              </div>
            </div>
          ))}
        </div>
      );
    }
    
    return null;
  };

  const renderDocumentContent = (filename: string, content: any) => {
    // Check if we have file metadata for this document - if so, render the actual file
    const fileData = findFileMetadata(filename);
    if (fileData) {
      return renderFileContent(fileData);
    }

    // Fallback to text-based rendering
    if (typeof content === 'string') {
      // Check if this is a scanned PDF placeholder
      if (content.startsWith('<SCANNED_PDF:')) {
        return (
          <div className="flex items-center justify-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
            <div className="text-center">
              <svg className="mx-auto h-16 w-16 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="mt-4 text-sm font-medium text-gray-900">Scanned PDF Document</h3>
              <p className="mt-2 text-sm text-gray-500 max-w-sm">
                This appears to be a scanned PDF. The text content cannot be extracted automatically, 
                but the document was still processed for data extraction.
              </p>
              <div className="mt-4 px-3 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full inline-block">
                Content processed using vision analysis
              </div>
            </div>
          </div>
        );
      }
      
      // Regular PDF or text content
      return (
        <div className="font-mono text-sm whitespace-pre-wrap max-h-[500px] overflow-y-auto p-4 bg-gray-50 rounded-md border">
          {content.length > 3000 ? `${content.substring(0, 3000)}...` : content}
        </div>
      );
    } else if (typeof content === 'object') {
      // XLSX content (fallback for old data without file metadata)
      return (
        <div className="space-y-4 max-h-[500px] overflow-y-auto">
          {Object.entries(content).map(([sheetName, rows]: [string, any]) => (
            <div key={sheetName} className="border rounded-lg shadow-sm">
              <div className="bg-green-50 px-4 py-3 font-medium text-sm border-b">
                📊 {sheetName}
              </div>
              <div className="p-4">
                <div className="text-sm space-y-2">
                  {rows.slice(0, 15).map((row: any[], idx: number) => (
                    <div key={idx} className="pb-2 border-b border-gray-100 last:border-b-0">
                      <div className="text-gray-600 text-xs mb-1">
                        <span className="font-medium">Row {idx + 1}:</span>
                      </div>
                      <div className="pl-2 text-gray-800 break-words">
                        {row.filter(cell => cell && cell.toString().trim()).join(' | ')}
                      </div>
                    </div>
                  ))}
                  {rows.length > 15 && (
                    <div className="text-gray-500 italic text-center py-2 bg-gray-50 rounded">
                      ... and {rows.length - 15} more rows
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