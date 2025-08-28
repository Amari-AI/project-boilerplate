import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Download, FileSpreadsheet } from 'lucide-react';
import './ExcelPreview.css';

interface ExcelPreviewProps {
  data: { [sheetName: string]: string[][] };
  filename: string;
  onDownload: () => void;
}

const ExcelPreview: React.FC<ExcelPreviewProps> = ({ data, filename, onDownload }) => {
  const sheetNames = Object.keys(data);
  const [currentSheetIndex, setCurrentSheetIndex] = useState(0);
  
  if (sheetNames.length === 0) {
    return (
      <div className="excel-preview-empty">
        <FileSpreadsheet size={48} />
        <p>No data available in this Excel file</p>
      </div>
    );
  }

  const currentSheetName = sheetNames[currentSheetIndex];
  const currentSheetData = data[currentSheetName];

  const goToPrevSheet = () => {
    if (currentSheetIndex > 0) {
      setCurrentSheetIndex(currentSheetIndex - 1);
    }
  };

  const goToNextSheet = () => {
    if (currentSheetIndex < sheetNames.length - 1) {
      setCurrentSheetIndex(currentSheetIndex + 1);
    }
  };

  return (
    <div className="excel-preview-container">
      <div className="excel-header">
        <div className="excel-file-info">
          <FileSpreadsheet size={24} style={{ color: '#16a34a' }} />
          <span className="excel-filename">{filename.replace(/^tmp[a-z0-9_]+/i, '')}</span>
        </div>
        <button onClick={onDownload} className="excel-download-btn">
          <Download size={18} /> Download Full File
        </button>
      </div>

      {sheetNames.length > 1 && (
        <div className="sheet-navigation">
          <button 
            onClick={goToPrevSheet} 
            disabled={currentSheetIndex === 0}
            className="sheet-nav-btn"
          >
            <ChevronLeft size={18} />
          </button>
          <span className="sheet-info">
            Sheet: <strong>{currentSheetName}</strong> ({currentSheetIndex + 1} of {sheetNames.length})
          </span>
          <button 
            onClick={goToNextSheet} 
            disabled={currentSheetIndex === sheetNames.length - 1}
            className="sheet-nav-btn"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      )}

      <div className="excel-table-wrapper">
        <table className="excel-table">
          <tbody>
            {currentSheetData.map((row, rowIndex) => (
              <tr key={rowIndex} className={rowIndex === 0 ? 'header-row' : ''}>
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex} className={rowIndex === 0 ? 'header-cell' : ''}>
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {currentSheetData.length >= 100 && (
        <div className="excel-preview-note">
          Note: Showing first 100 rows. Download the file to see all data.
        </div>
      )}
    </div>
  );
};

export default ExcelPreview;