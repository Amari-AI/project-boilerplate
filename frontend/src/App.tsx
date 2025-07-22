import { DocumentForm } from "./components/document-form"

const dummyData = {
  bill_of_lading_number: "BOL123456789",
  container_number: "CONU1234567",
  consignee_name: "John Doe Shipping",
  consignee_address: "123 Shipping Lane, Port City, 12345",
  date: "2025-07-22",
  line_items_count: 18,
  average_gross_weight: 150.75,
  average_price: 250.50,
};

const App = () => {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl p-8 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold mb-6 text-center">Extracted Document Data</h1>
        <DocumentForm data={dummyData} />
      </div>
    </div>
  )
}

export default App
