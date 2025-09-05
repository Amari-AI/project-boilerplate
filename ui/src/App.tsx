import { useState, useRef } from 'react'
import './App.css'

function App() {
  const [files, setFiles] = useState<File[]>([])
  const [processing, setProcessing] = useState(false)
  const [result, setResult] = useState<{ error?: string; [key: string]: unknown } | null>(null)
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
          <h3>Results:</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}

export default App
