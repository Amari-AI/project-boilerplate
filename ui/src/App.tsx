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
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle')
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

  const startOver = () => {
    setResult(null)
    setFiles([])
    setFormData({})
  }

  const saveChanges = async () => {
    if (!result || 'error' in result || !result.structured_data) {
      alert('No data to save')
      return
    }

    setSaveStatus('saving')

    try {
      // Create save data object
      const saveData = {
        document_type: result.structured_data.document_type,
        extracted_fields: formData,
        original_fields: result.structured_data.extracted_fields,
        saved_at: new Date().toISOString(),
        processing_status: result.status
      }

      // Save to localStorage
      const saveKey = `document_${result.structured_data.document_type.replace(/\s+/g, '_').toLowerCase()}_${Date.now()}`
      localStorage.setItem(saveKey, JSON.stringify(saveData))

      // Also maintain a list of all saved documents
      const savedDocuments = JSON.parse(localStorage.getItem('saved_documents') || '[]')
      savedDocuments.unshift({
        key: saveKey,
        document_type: result.structured_data.document_type,
        saved_at: saveData.saved_at,
        field_count: Object.keys(formData).length
      })
      
      // Keep only the last 10 saved documents
      if (savedDocuments.length > 10) {
        const oldKey = savedDocuments[10].key
        localStorage.removeItem(oldKey)
        savedDocuments.splice(10)
      }
      
      localStorage.setItem('saved_documents', JSON.stringify(savedDocuments))

      setSaveStatus('saved')
      
      // Reset save status after 3 seconds
      setTimeout(() => {
        setSaveStatus('idle')
      }, 3000)

    } catch (error) {
      console.error('Save failed:', error)
      alert('Failed to save changes')
      setSaveStatus('idle')
    }
  }

  const exportData = () => {
    if (!result || 'error' in result || !result.structured_data) {
      alert('No data to export')
      return
    }

    const exportObject = {
      document_type: result.structured_data.document_type,
      extracted_fields: formData, // Use current form data (including any edits)
      exported_at: new Date().toISOString(),
      processing_status: result.status,
      processing_message: result.message
    }

    // Create and download JSON file
    const jsonBlob = new Blob([JSON.stringify(exportObject, null, 2)], { 
      type: 'application/json' 
    })
    const jsonUrl = URL.createObjectURL(jsonBlob)
    const jsonLink = document.createElement('a')
    jsonLink.href = jsonUrl
    jsonLink.download = `extracted_data_${result.structured_data.document_type.replace(/\s+/g, '_').toLowerCase()}_${new Date().getTime()}.json`
    jsonLink.click()
    URL.revokeObjectURL(jsonUrl)
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
      
      {!result && (
        <>
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
        </>
      )}

      {result && (
        <>
          <h1>Edit Info</h1>
          <div className="result">
            <div className="result-header">
              <h3>Results</h3>
              <button onClick={startOver} className="start-over-btn">
                🔄 Start Over
              </button>
            </div>
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
                          <button 
                            type="button" 
                            className={`save-btn ${saveStatus === 'saved' ? 'save-btn-saved' : ''}`}
                            onClick={saveChanges}
                            disabled={saveStatus === 'saving'}
                          >
                            {saveStatus === 'saving' && '⏳ Saving...'}
                            {saveStatus === 'saved' && '✅ Saved!'}
                            {saveStatus === 'idle' && '💾 Save Changes'}
                          </button>
                          <button type="button" className="export-btn" onClick={exportData}>
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
        </>
      )}
    </div>
  )
}

export default App
