import React from 'react';

interface ShipmentData {
  bill_of_lading_number?: string | null;
  container_number?: string | null;
  consignee_name?: string | null;
  consignee_address?: string | null;
  date?: string | null;
  line_items_count?: string | null;
  average_gross_weight?: string | null;
  average_price?: string | null;
}

interface ExtractedDataFormProps {
  data: ShipmentData;
  onUpdateField: (field: keyof ShipmentData, value: string) => void;
  onSave: () => void;
  onReset?: () => void;
  saving?: boolean;
}

const ExtractedDataForm: React.FC<ExtractedDataFormProps> = ({ data, onUpdateField, onSave, onReset, saving }) => {
  const handleChange = (field: keyof ShipmentData) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    onUpdateField(field, e.target.value);
  };

  const fieldLabels = {
    bill_of_lading_number: 'Bill of Lading Number',
    container_number: 'Container Number',
    consignee_name: 'Consignee Name',
    consignee_address: 'Consignee Address',
    date: 'Date (MM/DD/YYYY)',
    line_items_count: 'Line Items Count',
    average_gross_weight: 'Average Gross Weight',
    average_price: 'Average Price'
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <svg className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Extracted Data (Editable)
      </h2>

      <form className="space-y-6">
        {/* First Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="bill_of_lading_number" className="block text-sm font-medium text-gray-700 mb-2">
              {fieldLabels.bill_of_lading_number}
            </label>
            <input
              type="text"
              id="bill_of_lading_number"
              value={data.bill_of_lading_number || ''}
              onChange={handleChange('bill_of_lading_number')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter bill of lading number"
            />
          </div>

          <div>
            <label htmlFor="container_number" className="block text-sm font-medium text-gray-700 mb-2">
              {fieldLabels.container_number}
            </label>
            <input
              type="text"
              id="container_number"
              value={data.container_number || ''}
              onChange={handleChange('container_number')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter container number"
            />
          </div>
        </div>

        {/* Second Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="consignee_name" className="block text-sm font-medium text-gray-700 mb-2">
              {fieldLabels.consignee_name}
            </label>
            <input
              type="text"
              id="consignee_name"
              value={data.consignee_name || ''}
              onChange={handleChange('consignee_name')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter consignee name"
            />
          </div>

          <div>
            <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-2">
              {fieldLabels.date}
            </label>
            <input
              type="text"
              id="date"
              value={data.date || ''}
              onChange={handleChange('date')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="MM/DD/YYYY"
            />
          </div>
        </div>

        {/* Third Row - Address */}
        <div>
          <label htmlFor="consignee_address" className="block text-sm font-medium text-gray-700 mb-2">
            {fieldLabels.consignee_address}
          </label>
          <textarea
            id="consignee_address"
            rows={3}
            value={data.consignee_address || ''}
            onChange={handleChange('consignee_address')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter consignee address"
          />
        </div>

        {/* Fourth Row - Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label htmlFor="line_items_count" className="block text-sm font-medium text-gray-700 mb-2">
              {fieldLabels.line_items_count}
            </label>
            <input
              type="text"
              id="line_items_count"
              value={data.line_items_count || ''}
              onChange={handleChange('line_items_count')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="0"
            />
          </div>

          <div>
            <label htmlFor="average_gross_weight" className="block text-sm font-medium text-gray-700 mb-2">
              {fieldLabels.average_gross_weight}
            </label>
            <div className="relative">
              <input
                type="text"
                id="average_gross_weight"
                value={data.average_gross_weight || ''}
                onChange={handleChange('average_gross_weight')}
                className="w-full px-3 py-2 pr-8 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="0.00"
              />
              <span className="absolute right-3 top-2 text-sm text-gray-500">kg</span>
            </div>
          </div>

          <div>
            <label htmlFor="average_price" className="block text-sm font-medium text-gray-700 mb-2">
              {fieldLabels.average_price}
            </label>
            <div className="relative">
              <input
                type="text"
                id="average_price"
                value={data.average_price || ''}
                onChange={handleChange('average_price')}
                className="w-full px-3 py-2 pr-8 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="0.00"
              />
              <span className="absolute right-3 top-2 text-sm text-gray-500">$</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
          {onReset && (
            <button
              type="button"
              onClick={onReset}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              Reset
            </button>
          )}
          <button
            type="button"
            onClick={onSave}
            disabled={saving}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {saving && (
              <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            )}
            {saving ? 'Saving...' : 'Save Data'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ExtractedDataForm;