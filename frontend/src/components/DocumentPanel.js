import React from 'react';
import './DocumentPanel.css';

const DocumentPanel = ({ files, onRemoveFile }) => {
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (filename) => {
    const extension = filename.split('.').pop().toLowerCase();
    switch (extension) {
      case 'pdf':
        return '📄';
      case 'xlsx':
      case 'xls':
        return '📊';
      default:
        return '📁';
    }
  };

  return (
    <div className="document-panel">
      <div className="panel-header">
        <h3>Uploaded Documents</h3>
        <span className="file-count">{files.length} file{files.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="files-list">
        {files.length === 0 ? (
          <div className="no-files">
            <div className="no-files-icon">📂</div>
            <p>No documents uploaded yet</p>
            <p className="no-files-hint">Upload PDF or Excel files to get started</p>
          </div>
        ) : (
          files.map((file, index) => (
            <div key={index} className="file-item">
              <div className="file-info">
                <div className="file-icon">{getFileIcon(file.name)}</div>
                <div className="file-details">
                  <div className="file-name" title={file.name}>
                    {file.name}
                  </div>
                  <div className="file-meta">
                    <span className="file-size">{formatFileSize(file.size)}</span>
                    <span className="file-type">
                      {file.name.split('.').pop().toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>
              <button
                className="remove-file-btn"
                onClick={() => onRemoveFile(index)}
                title="Remove file"
              >
                ✕
              </button>
            </div>
          ))
        )}
      </div>

      {files.length > 0 && (
        <div className="panel-footer">
          <div className="total-size">
            Total: {formatFileSize(files.reduce((sum, file) => sum + file.size, 0))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentPanel; 