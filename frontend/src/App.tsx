import { DocumentUpload } from "./components/document-upload"

const App = () => {
  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="w-full max-w-6xl mx-auto p-8 bg-white rounded-lg shadow-md">
        <h1 className="text-3xl font-bold mb-6 text-center">Document Data Extraction</h1>
        <DocumentUpload />
      </div>
    </div>
  )
}

export default App
