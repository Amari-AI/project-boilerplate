import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { DocumentForm } from "./document-form"

interface ExtractedData {
  bill_of_lading_number: string | null
  container_number: string | null
  consignee_name: string | null
  consignee_address: string | null
  date: string | null
  line_items_count: number | null
  average_gross_weight: number | null
  average_price: number | null
}

interface FileDetail {
  name: string
  type: string
  has_text: boolean
  image_count: number
}

interface FileResult {
  file_name: string
  file_info: FileDetail
  extracted_data: ExtractedData
}

interface ProcessingInfo {
  files_processed: number
  images_processed: number
}

interface ApiResponse {
  file_results: FileResult[]
  processing_info: ProcessingInfo
}

interface DocumentUploadProps {
  onFilesProcessed?: (files: FileDetail[]) => void
  selectedFile?: string
}

export function DocumentUpload({ onFilesProcessed, selectedFile }: DocumentUploadProps) {
  const [files, setFiles] = useState<FileList | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [fileResults, setFileResults] = useState<FileResult[] | null>(null)
  const [combinedData, setCombinedData] = useState<ExtractedData | null>(null)
  const [processingInfo, setProcessingInfo] = useState<ProcessingInfo | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedFileIndex, setSelectedFileIndex] = useState<number | null>(null)

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(event.target.files)
    setError(null)
  }

  const handleUpload = async () => {
    if (!files || files.length === 0) {
      setError("Please select at least one file")
      return
    }

    setIsUploading(true)
    setError(null)

    const formData = new FormData()
    
    // Append all selected files
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i])
    }

    try {
      const response = await fetch("http://localhost:8000/process-documents", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: ApiResponse = await response.json()
      setFileResults(data.file_results)
      setProcessingInfo(data.processing_info)
      
      // Merge data from all files for the main form (use first non-null value for each field)
      const mergedData: ExtractedData = {
        bill_of_lading_number: null,
        container_number: null,
        consignee_name: null,
        consignee_address: null,
        date: null,
        line_items_count: null,
        average_gross_weight: null,
        average_price: null,
      }
      
      for (const fileResult of data.file_results) {
        if (mergedData.bill_of_lading_number === null) mergedData.bill_of_lading_number = fileResult.extracted_data.bill_of_lading_number
        if (mergedData.container_number === null) mergedData.container_number = fileResult.extracted_data.container_number
        if (mergedData.consignee_name === null) mergedData.consignee_name = fileResult.extracted_data.consignee_name
        if (mergedData.consignee_address === null) mergedData.consignee_address = fileResult.extracted_data.consignee_address
        if (mergedData.date === null) mergedData.date = fileResult.extracted_data.date
        if (mergedData.line_items_count === null) mergedData.line_items_count = fileResult.extracted_data.line_items_count
        if (mergedData.average_gross_weight === null) mergedData.average_gross_weight = fileResult.extracted_data.average_gross_weight
        if (mergedData.average_price === null) mergedData.average_price = fileResult.extracted_data.average_price
      }
      
      setCombinedData(mergedData)
      
      // Notify parent component about processed files
      if (onFilesProcessed) {
        const fileDetails = data.file_results.map(result => ({
          name: result.file_name,
          type: result.file_info.type,
          has_text: result.file_info.has_text,
          image_count: result.file_info.image_count
        }))
        onFilesProcessed(fileDetails)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred during upload")
      console.error("Upload error:", err)
    } finally {
      setIsUploading(false)
    }
  }

  const resetUpload = () => {
    setFiles(null)
    setFileResults(null)
    setCombinedData(null)
    setProcessingInfo(null)
    setError(null)
    setSelectedFileIndex(null)
    
    // Clear the sidebar
    if (onFilesProcessed) {
      onFilesProcessed([])
    }
    
    // Reset the file input
    const fileInput = document.getElementById("file-input") as HTMLInputElement
    if (fileInput) {
      fileInput.value = ""
    }
  }

  // Get fields that have values from a specific file
  const getFieldsFromFile = (fileIndex: number): (keyof ExtractedData)[] => {
    if (!fileResults || !fileResults[fileIndex]) return []
    
    const fileData = fileResults[fileIndex].extracted_data
    const fieldsWithValues: (keyof ExtractedData)[] = []
    
    Object.entries(fileData).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== "") {
        fieldsWithValues.push(key as keyof ExtractedData)
      }
    })
    
    return fieldsWithValues
  }

  // Check if a field should be highlighted based on selected file
  const shouldHighlightField = (fieldName: keyof ExtractedData): boolean => {
    if (selectedFileIndex === null) return false
    const fieldsFromSelectedFile = getFieldsFromFile(selectedFileIndex)
    return fieldsFromSelectedFile.includes(fieldName)
  }

  return (
    <div className="space-y-6">
      {!combinedData ? (
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <div className="space-y-4">
            <div>
              <Label htmlFor="file-input" className="text-lg font-medium">
                Upload Documents
              </Label>
              <p className="text-sm text-gray-600 mt-1">
                Select PDF and Excel files to extract data from
              </p>
            </div>
            
            <Input
              id="file-input"
              type="file"
              multiple
              accept=".pdf,.xlsx,.xls"
              onChange={handleFileChange}
              className="max-w-md mx-auto"
            />
            
            {files && files.length > 0 && (
              <div className="text-sm text-gray-600">
                <p>{files.length} file(s) selected:</p>
                <ul className="mt-2">
                  {Array.from(files).map((file, index) => (
                    <li key={index} className="truncate">
                      {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <Button 
              onClick={handleUpload} 
              disabled={!files || files.length === 0 || isUploading}
              className="px-8"
            >
              {isUploading ? "Processing..." : "Upload & Extract Data"}
            </Button>
            
            {error && (
              <div className="text-red-600 text-sm mt-2">
                Error: {error}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Processing Information */}
          {processingInfo && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-medium text-blue-900 mb-2">Processing Summary</h3>
              <div className="text-sm text-blue-800 grid grid-cols-2 gap-2">
                <div>Files processed: {processingInfo.files_processed}</div>
                <div>Images processed: {processingInfo.images_processed}</div>
              </div>
            </div>
          )}
          
          {/* Reset Button */}
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Extracted Document Data</h2>
            <Button variant="outline" onClick={resetUpload}>
              Upload New Documents
            </Button>
          </div>
          
          {/* Document Form with extracted data */}
          <DocumentForm 
            data={combinedData} 
            shouldHighlightField={shouldHighlightField}
          />
          
          {/* File List Section */}
          {fileResults && fileResults.length > 0 && (
            <div className="mt-8">
              <h3 className="text-lg font-semibold mb-4">Extracted Files</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {fileResults.map((fileResult, index) => (
                  <div 
                    key={index} 
                    className={`border rounded-lg p-4 cursor-pointer transition-all ${
                      selectedFileIndex === index 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedFileIndex(selectedFileIndex === index ? null : index)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-sm truncate">{fileResult.file_name}</h4>
                      <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                        {fileResult.file_info.type.toUpperCase()}
                      </span>
                    </div>
                    <div className="text-xs text-gray-600 mb-2">
                      {fileResult.file_info.has_text ? "✓ Text extracted" : "✗ No text"} • 
                      {fileResult.file_info.image_count} images
                    </div>
                    <div className="text-xs text-gray-500">
                      Fields: {getFieldsFromFile(index).length} found
                    </div>
                    {selectedFileIndex === index && (
                      <div className="mt-2 pt-2 border-t border-blue-200">
                        <div className="text-xs text-blue-600">
                          <strong>Fields from this file:</strong>
                          <div className="mt-1 flex flex-wrap gap-1">
                            {getFieldsFromFile(index).map(field => (
                              <span 
                                key={field} 
                                className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs"
                              >
                                {field.replace(/_/g, ' ')}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
              {selectedFileIndex !== null && (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>Tip:</strong> Fields highlighted in blue above came from the selected file: <strong>{fileResults[selectedFileIndex].file_name}</strong>
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
