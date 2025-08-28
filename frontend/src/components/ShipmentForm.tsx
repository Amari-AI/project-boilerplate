import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Save, Edit2 } from 'lucide-react';
import { ShipmentData } from '../types';
import config from '../config';
import './ShipmentForm.css';

interface ShipmentFormProps {
  data: ShipmentData;
  onUpdate: (data: ShipmentData) => void;
  sessionId: string;
}

const ShipmentForm: React.FC<ShipmentFormProps> = ({ data, onUpdate, sessionId }) => {
  const [formData, setFormData] = useState<ShipmentData>(data);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    setFormData(data);
  }, [data]);

  const handleInputChange = (field: keyof ShipmentData, value: string | number | null) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await axios.post(`${config.API_URL}/update-shipment`, {
        shipment_data: formData,
        session_id: sessionId
      });
      
      onUpdate(formData);
      setIsEditing(false);
      alert('Data saved successfully!');
    } catch (error) {
      console.error('Error saving data:', error);
      alert('Failed to save data');
    } finally {
      setIsSaving(false);
    }
  };

  const fields = [
    { key: 'bill_of_lading_number', label: 'Bill of Lading Number', type: 'text' },
    { key: 'container_number', label: 'Container Number', type: 'text' },
    { key: 'consignee_name', label: 'Consignee Name', type: 'text' },
    { key: 'consignee_address', label: 'Consignee Address', type: 'text' },
    { key: 'date', label: 'Date', type: 'date' },
    { key: 'line_items_count', label: 'Line Items Count', type: 'number' },
    { key: 'average_gross_weight', label: 'Average Gross Weight', type: 'text' },
    { key: 'average_price', label: 'Average Price', type: 'text' }
  ];

  return (
    <div className="shipment-form">
      <div className="form-header">
        <h2>Extracted Shipment Data</h2>
        <div className="form-actions">
          {!isEditing ? (
            <button className="edit-btn" onClick={() => setIsEditing(true)}>
              <Edit2 size={16} /> Edit
            </button>
          ) : (
            <>
              <button className="save-btn" onClick={handleSave} disabled={isSaving}>
                <Save size={16} /> {isSaving ? 'Saving...' : 'Save'}
              </button>
              <button className="cancel-btn" onClick={() => {
                setFormData(data);
                setIsEditing(false);
              }}>
                Cancel
              </button>
            </>
          )}
        </div>
      </div>

      <div className="form-fields">
        {fields.map(field => (
          <div key={field.key} className="form-field">
            <label>{field.label}:</label>
            {isEditing ? (
              <input
                type={field.type}
                value={formData[field.key as keyof ShipmentData] ?? ''}
                onChange={(e) => {
                  const value = field.type === 'number' 
                    ? (e.target.value ? parseInt(e.target.value) : null)
                    : e.target.value;
                  handleInputChange(field.key as keyof ShipmentData, value);
                }}
                className="form-input"
              />
            ) : (
              <span className="form-value">
                {formData[field.key as keyof ShipmentData] || 'Not provided'}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ShipmentForm;