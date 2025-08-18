import { useForm } from '@tanstack/react-form';
import { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { DatePicker } from '@/components/DatePicker';
import { DocumentFormData } from '@/types';

interface DocumentFormProps {
  formData?: DocumentFormData | null;
  totalDocuments?: number;
  onFormChange?: (data: DocumentFormData) => void;
}

const defaultFormData: DocumentFormData = {
  billOfLadingNumber: '',
  containerNumber: '',
  consigneeName: '',
  consigneeAddress: '',
  date: '',
  lineItemsCount: '',
  averageGrossWeight: '',
  averagePrice: '',
};

export function DocumentForm({ formData, totalDocuments, onFormChange }: DocumentFormProps) {
  const form = useForm({
    defaultValues: formData || defaultFormData,
    onSubmit: async () => {
      // Form submission is handled by the parent component if needed
    },
  });

  // Update form values when formData changes
  useEffect(() => {
    if (formData) {
      Object.keys(formData).forEach((key) => {
        const fieldKey = key as keyof DocumentFormData;
        form.setFieldValue(fieldKey, formData[fieldKey] || '');
      });
    }
  }, [formData, form]);

  // Notify parent of form changes
  const handleFieldChange = (fieldName: keyof DocumentFormData, value: string) => {
    form.setFieldValue(fieldName, value);
    
    // Create updated form data and notify parent
    const currentValues = form.getFieldValue('') as DocumentFormData;
    const updatedData = {
      ...currentValues,
      [fieldName]: value,
    };
    onFormChange?.(updatedData);
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle>
          Extracted Information
          {totalDocuments && totalDocuments > 0 && (
            <span className="text-sm font-normal text-gray-500 block mt-1">
              Aggregated from {totalDocuments} document{totalDocuments > 1 ? 's' : ''}
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            e.stopPropagation();
            form.handleSubmit();
          }}
          className="space-y-4"
        >
          <form.Field name="billOfLadingNumber">
            {(field) => (
              <div className="space-y-2">
                <Label htmlFor={field.name}>Bill of Lading Number</Label>
                <Input
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(e) => handleFieldChange('billOfLadingNumber', e.target.value)}
                />
              </div>
            )}
          </form.Field>

          <form.Field name="containerNumber">
            {(field) => (
              <div className="space-y-2">
                <Label htmlFor={field.name}>Container Number</Label>
                <Input
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(e) => handleFieldChange('containerNumber', e.target.value)}
                />
              </div>
            )}
          </form.Field>

          <form.Field name="consigneeName">
            {(field) => (
              <div className="space-y-2">
                <Label htmlFor={field.name}>Consignee Name</Label>
                <Input
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(e) => handleFieldChange('consigneeName', e.target.value)}
                />
              </div>
            )}
          </form.Field>

          <form.Field name="consigneeAddress">
            {(field) => (
              <div className="space-y-2">
                <Label htmlFor={field.name}>Consignee Address</Label>
                <Input
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(e) => handleFieldChange('consigneeAddress', e.target.value)}
                />
              </div>
            )}
          </form.Field>

          <form.Field name="date">
            {(field) => (
              <DatePicker
                id={field.name}
                label="Date"
                placeholder="Select date..."
                value={field.state.value}
                onChange={(value) => handleFieldChange('date', value)}
                onBlur={field.handleBlur}
              />
            )}
          </form.Field>

          <form.Field name="lineItemsCount">
            {(field) => (
              <div className="space-y-2">
                <Label htmlFor={field.name}>Line Items Count</Label>
                <Input
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(e) => handleFieldChange('lineItemsCount', e.target.value)}
                />
              </div>
            )}
          </form.Field>

          <form.Field name="averageGrossWeight">
            {(field) => (
              <div className="space-y-2">
                <Label htmlFor={field.name}>Average Gross Weight</Label>
                <Input
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(e) => handleFieldChange('averageGrossWeight', e.target.value)}
                />
              </div>
            )}
          </form.Field>

          <form.Field name="averagePrice">
            {(field) => (
              <div className="space-y-2">
                <Label htmlFor={field.name}>Average Price</Label>
                <Input
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(e) => handleFieldChange('averagePrice', e.target.value)}
                />
              </div>
            )}
          </form.Field>
        </form>
      </CardContent>
    </Card>
  );
}