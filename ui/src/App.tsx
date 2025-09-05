import { useState, useRef } from 'react'
import './App.css'

interface StructuredData {
  document_type: string
  extracted_fields: Record<string, string>
}

interface ProcessResult {
  status: string
  message: string
  extracted_data?: Record<string, unknown>
  processed_data?: string
  structured_data?: StructuredData
}

interface ErrorResult {
  error: string
}

type Result = ProcessResult | ErrorResult

function App() {
  const [files, setFiles] = useState<File[]>([])
  const [processing, setProcessing] = useState(false)
  const [result, setResult] = useState<Result | null>(null)
  const [formData, setFormData] = useState<Record<string, string>>({})
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = event.target.files
    if (selectedFiles) {
      const validFiles = Array.from(selectedFiles).filter(file => {
        const fileType = file.type
        const fileName = file.name.toLowerCase()
        return fileType === 'application/pdf' || 
               fileType === 'application/vnd.ms-excel' ||
               fileType === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
               fileName.endsWith('.pdf') || 
               fileName.endsWith('.xls') || 
               fileName.endsWith('.xlsx')
      })
      setFiles(validFiles)
    }
  }

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault()
  }

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault()
    const droppedFiles = event.dataTransfer.files
    if (droppedFiles) {
      const validFiles = Array.from(droppedFiles).filter(file => {
        const fileType = file.type
        const fileName = file.name.toLowerCase()
        return fileType === 'application/pdf' || 
               fileType === 'application/vnd.ms-excel' ||
               fileType === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
               fileName.endsWith('.pdf') || 
               fileName.endsWith('.xls') || 
               fileName.endsWith('.xlsx')
      })
      setFiles(validFiles)
    }
  }

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  const handleFormFieldChange = (fieldName: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }))
  }

  const processFiles = async () => {
    if (files.length === 0) return
    
    setProcessing(true)
    setResult(null)
    
    try {
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file)
      })

      const response = await fetch('http://localhost:8000/process-documents', {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        setResult(data)
        // Initialize form data with extracted fields if available
        if (data.structured_data?.extracted_fields) {
          setFormData(data.structured_data.extracted_fields)
        }
      } else {
        setResult({ error: 'Failed to process files' })
      }
    } catch {
      setResult({ error: 'Network error' })
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className="app">
      <h1>Document Processing</h1>
      <p>Upload PDF and Excel files for processing</p>
      
      <div 
        className="upload-zone"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="upload-content">
          <div className="upload-icon">📁</div>
          <p>Drag and drop files here or click to browse</p>
          <p className="file-types">Supported: PDF, XLS, XLSX</p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.xls,.xlsx,application/pdf,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
      </div>

      {files.length > 0 && (
        <div className="file-list">
          <h3>Selected Files:</h3>
          {files.map((file, index) => (
            <div key={index} className="file-item">
              <span className="file-name">{file.name}</span>
              <span className="file-size">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
              <button onClick={() => removeFile(index)} className="remove-btn">×</button>
            </div>
          ))}
          <button 
            onClick={processFiles} 
            disabled={processing}
            className="process-btn"
          >
            {processing ? 'Processing...' : 'Process Files'}
          </button>
        </div>
      )}

      {result && (
        <div className="result">
          <h3>Results</h3>
          {'error' in result ? (
            <div className="error">Error: {result.error}</div>
          ) : (
            <div className="result-content">
              <div className="status-message">
                <span className="status-badge">{result.status.toUpperCase()}</span>
                <span className="message">{result.message}</span>
              </div>
              
              {result.structured_data ? (
                <div className="form-container">
                  <div className="document-type">
                    <h4>📄 {result.structured_data.document_type}</h4>
                  </div>
                  <div className="extracted-form">
                    <h4>📝 Extracted Information</h4>
                    <p>Review and edit the extracted data below:</p>
                    <form className="google-form">
                      {Object.entries(formData).map(([fieldName, fieldValue]) => (
                        <div key={fieldName} className="form-field">
                          <label htmlFor={fieldName} className="form-label">
                            {fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </label>
                          <input
                            type="text"
                            id={fieldName}
                            value={fieldValue}
                            onChange={(e) => handleFormFieldChange(fieldName, e.target.value)}
                            className="form-input"
                            placeholder={`Enter ${fieldName.replace(/_/g, ' ')}`}
                          />
                        </div>
                      ))}
                      <div className="form-actions">
                        <button type="button" className="save-btn">
                          💾 Save Changes
                        </button>
                        <button type="button" className="export-btn">
                          📥 Export Data
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              ) : result.processed_data ? (
                <div className="processed-data">
                  <strong>Processed Data:</strong>
                  <pre className="formatted-text">{result.processed_data}</pre>
                </div>
              ) : null}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App
