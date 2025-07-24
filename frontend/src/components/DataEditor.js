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

  const updateInvoiceItem = (index, field, value) => {
    const items = [...(editedData.invoice_list?.invoice_items || [])];
    items[index] = { ...items[index], [field]: value };
    
    const newData = {
      ...editedData,
      invoice_list: {
        ...editedData.invoice_list,
        invoice_items: items
      }
    };
    setEditedData(newData);
    onDataUpdate(newData);
  };

  const addInvoiceItem = () => {
    const newItem = {
      serial_number: '',
      description: '',
      quantity: 0,
      unit_value: 0,
      total_weight: 0,
      other_identifier: ''
    };
    
    const items = [...(editedData.invoice_list?.invoice_items || []), newItem];
    const newData = {
      ...editedData,
      invoice_list: {
        ...editedData.invoice_list,
        invoice_items: items
      }
    };
    setEditedData(newData);
    onDataUpdate(newData);
  };

  const removeInvoiceItem = (index) => {
    const items = (editedData.invoice_list?.invoice_items || []).filter((_, i) => i !== index);
    const newData = {
      ...editedData,
      invoice_list: {
        ...editedData.invoice_list,
        invoice_items: items
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

          <div className="invoice-items">
            <div className="items-header">
              <h4>Invoice Items</h4>
              <button className="add-item-btn" onClick={addInvoiceItem}>
                + Add Item
              </button>
            </div>

            {editedData.invoice_list.invoice_items?.map((item, index) => (
              <div key={index} className="invoice-item">
                <div className="item-header">
                  <span>Item {index + 1}</span>
                  <button 
                    className="remove-item-btn"
                    onClick={() => removeInvoiceItem(index)}
                  >
                    ✕
                  </button>
                </div>
                
                <div className="item-grid">
                  <div className="form-group">
                    <label>Serial Number:</label>
                    <input
                      type="text"
                      value={item.serial_number || ''}
                      onChange={(e) => updateInvoiceItem(index, 'serial_number', e.target.value)}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Description:</label>
                    <input
                      type="text"
                      value={item.description || ''}
                      onChange={(e) => updateInvoiceItem(index, 'description', e.target.value)}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Quantity:</label>
                    <input
                      type="number"
                      value={item.quantity || 0}
                      onChange={(e) => updateInvoiceItem(index, 'quantity', parseInt(e.target.value) || 0)}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Unit Value:</label>
                    <input
                      type="number"
                      step="0.01"
                      value={item.unit_value || 0}
                      onChange={(e) => updateInvoiceItem(index, 'unit_value', parseFloat(e.target.value) || 0)}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Total Weight:</label>
                    <input
                      type="number"
                      step="0.01"
                      value={item.total_weight || 0}
                      onChange={(e) => updateInvoiceItem(index, 'total_weight', parseFloat(e.target.value) || 0)}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Other Identifier:</label>
                    <input
                      type="text"
                      value={item.other_identifier || ''}
                      onChange={(e) => updateInvoiceItem(index, 'other_identifier', e.target.value)}
                    />
                  </div>
                </div>
              </div>
            ))}
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