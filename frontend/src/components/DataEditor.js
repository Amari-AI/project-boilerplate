import React, { useState, useEffect } from 'react';
import './DataEditor.css';

const DataEditor = ({ data, onDataUpdate }) => {
  const [editedData, setEditedData] = useState(data);

  useEffect(() => {
    setEditedData(data);
  }, [data]);

  const updateInvoiceData = (field, value) => {
    const newData = {
      ...editedData,
      invoice_list: {
        ...editedData.invoice_list,
        [field]: value
      }
    };
    setEditedData(newData);
    onDataUpdate(newData);
  };

  const updateBillOfLading = (field, value) => {
    const newData = {
      ...editedData,
      bill_of_lading_list: {
        ...editedData.bill_of_lading_list,
        [field]: value
      }
    };
    setEditedData(newData);
    onDataUpdate(newData);
  };

  const calculateInvoiceItemsSummary = () => {
    const items = editedData.invoice_list?.invoice_items || [];
    
    if (items.length === 0) {
      return {
        totalItems: 0,
        averageWeightByQuantity: 0,
        averagePrice: 0
      };
    }

    const totalItems = items.length;
    
    // Calculate average price (simple average of unit values)
    // const totalPrice = items.reduce((sum, item) => sum + (item.unit_value || 0), 0);
    const totalQuantity = items.reduce((sum, item) => sum + (item.quantity || 0), 0);
    
    // Calculate average gross weight weighted by quantity
    const totalWeightedWeight = items.reduce((sum, item) => {
      const weight = item.total_weight || 0;
      return sum + weight;
    }, 0);

    const totalWeightedValue = items.reduce((sum, item) => {
      const quantity = item.quantity || 0;
      const value = item.unit_value || 0;
      return sum + (value * quantity);
    }, 0);
    
    const averageWeightByQuantity = totalQuantity > 0 ? totalWeightedWeight / totalItems : 0;
    const averagePriceByQuantity = totalQuantity > 0 ? totalWeightedValue / totalQuantity : 0;
    
    return {
      totalItems,
      averageWeightByQuantity: averageWeightByQuantity.toFixed(2),
      averagePrice: averagePriceByQuantity.toFixed(2)
    };
  };

  const downloadJSON = () => {
    const dataStr = JSON.stringify(editedData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'extracted_data.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  const invoiceItemsSummary = calculateInvoiceItemsSummary();

  return (
    <div className="data-editor">
      <div className="editor-header">
        <h2>Extracted Data</h2>
        <button className="download-btn" onClick={downloadJSON}>
          📥 Download JSON
        </button>
      </div>

      {editedData.invoice_list && (
        <div className="invoice-section">
          <h3>Invoice Data</h3>
          <div className="form-group">
            <label>Invoice Number:</label>
            <input
              type="text"
              value={editedData.invoice_list.invoice_number || ''}
              onChange={(e) => updateInvoiceData('invoice_number', e.target.value)}
            />
          </div>

          <div className="invoice-items-summary">
            <h4>Invoice Items Summary</h4>
            <div className="summary-grid">
              <div className="summary-item">
                <label>Line Items Count:</label>
                <span className="summary-value">{invoiceItemsSummary.totalItems}</span>
              </div>
              
              <div className="summary-item">
                <label>Average Gross Weight (weighted by quantity):</label>
                <span className="summary-value">{invoiceItemsSummary.averageWeightByQuantity}</span>
              </div>
              
              <div className="summary-item">
                <label>Average Price per Item:</label>
                <span className="summary-value">${invoiceItemsSummary.averagePrice}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {editedData.bill_of_lading_list && (
        <div className="bill-of-lading-section">
          <h3>Bill of Lading Data</h3>
          
          <div className="form-grid">
            <div className="form-group">
              <label>Bill of Lading Number:</label>
              <input
                type="text"
                value={editedData.bill_of_lading_list.bill_of_landing_number || ''}
                onChange={(e) => updateBillOfLading('bill_of_landing_number', e.target.value)}
              />
            </div>
            
            <div className="form-group">
              <label>Container Number:</label>
              <input
                type="text"
                value={editedData.bill_of_lading_list.container_number || ''}
                onChange={(e) => updateBillOfLading('container_number', e.target.value)}
              />
            </div>
            
            <div className="form-group">
              <label>Consignee Name:</label>
              <input
                type="text"
                value={editedData.bill_of_lading_list.consignee_name || ''}
                onChange={(e) => updateBillOfLading('consignee_name', e.target.value)}
              />
            </div>
            
            <div className="form-group">
              <label>Consignee Address:</label>
              <textarea
                value={editedData.bill_of_lading_list.consignee_address || ''}
                onChange={(e) => updateBillOfLading('consignee_address', e.target.value)}
                rows={3}
              />
            </div>
            
            <div className="form-group">
              <label>Date:</label>
              <input
                type="text"
                value={editedData.bill_of_lading_list.date || ''}
                onChange={(e) => updateBillOfLading('date', e.target.value)}
              />
            </div>
          </div>
        </div>
      )}

      {!editedData.invoice_list && !editedData.bill_of_lading_list && (
        <div className="no-data">
          <p>No data extracted from the documents. Please try uploading different files.</p>
        </div>
      )}
    </div>
  );
};

export default DataEditor; 