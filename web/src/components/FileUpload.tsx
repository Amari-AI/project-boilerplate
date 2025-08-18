import { Upload, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { DocumentData } from '@/types';
import { FileList } from './FileList';

interface FileUploadProps {
  documents: DocumentData[];
  isProcessing: boolean;
  onFilesChange: (files: File[]) => void;
  onAddMoreFiles: (files: File[]) => void;
  onRemoveFile: (id: string) => void;
  onProcess: () => void;
}

export function FileUpload({
  documents,
  isProcessing,
  onFilesChange,
  onAddMoreFiles,
  onRemoveFile,
  onProcess,
}: FileUploadProps) {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    onFilesChange(files);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold mb-2">
            AI Document Extraction
          </CardTitle>
          <p className="text-gray-600">
            Upload PDF or Excel documents to extract shipment information
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="document">Select Documents</Label>
            <Input
              id="document"
              type="file"
              multiple
              accept=".pdf,.xlsx,.xls,application/pdf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel"
              onChange={handleFileChange}
              disabled={isProcessing}
            />
            <p className="text-sm text-gray-500">
              Supported formats: PDF, Excel (.xlsx, .xls). You can select multiple files.
            </p>
          </div>

          {documents.length > 0 && (
            <FileList
              documents={documents}
              onRemoveFile={onRemoveFile}
              onAddMoreFiles={onAddMoreFiles}
              isProcessing={isProcessing}
            />
          )}

          <Button
            onClick={onProcess}
            disabled={documents.length === 0 || isProcessing}
            className="w-full"
            size="lg"
          >
            {isProcessing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing Documents...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Process {documents.length > 0 ? `${documents.length} Document${documents.length > 1 ? 's' : ''}` : 'Documents'}
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}