import { X, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { DocumentData } from '@/types';
import { formatFileSize, formatDate, getFileIconComponent, getFileIconColor } from '@/lib/fileAnalysis';

interface FileListProps {
  documents: DocumentData[];
  onRemoveFile: (id: string) => void;
  onAddMoreFiles: (files: File[]) => void;
  isProcessing: boolean;
}

export function FileList({ documents, onRemoveFile, onAddMoreFiles, isProcessing }: FileListProps) {
  const handleAddFiles = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '.pdf,.xlsx,.xls,application/pdf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel';
    input.onchange = (e) => {
      const target = e.target as HTMLInputElement;
      if (target.files) {
        onAddMoreFiles(Array.from(target.files));
      }
    };
    input.click();
  };

  const renderFileStats = (doc: DocumentData) => {
    const { file, stats } = doc;
    const IconComponent = getFileIconComponent(file);
    const iconColor = getFileIconColor(file);
    
    return (
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <IconComponent className={`h-5 w-5 ${iconColor}`} />
            <span className="font-medium text-gray-900 truncate">{file.name}</span>
          </div>
          
          <div className="flex flex-wrap gap-4 text-sm text-gray-600">
            <span>{formatFileSize(stats.size)}</span>
            <span>{formatDate(stats.lastModified)}</span>
            
            {stats.pages && (
              <span>{stats.pages} page{stats.pages > 1 ? 's' : ''}</span>
            )}
            
            {stats.sheets && (
              <span>{stats.sheets} sheet{stats.sheets > 1 ? 's' : ''}</span>
            )}
            
            {stats.rows && (
              <span>~{stats.rows} rows</span>
            )}
          </div>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onRemoveFile(doc.id)}
          disabled={isProcessing}
          className="h-8 w-8 p-0 text-gray-400 hover:text-red-500"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    );
  };

  if (documents.length === 0) {
    return null;
  }

  return (
    <Card className="border-green-200 bg-green-50">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-medium text-green-800">
            {documents.length} file{documents.length > 1 ? 's' : ''} selected
          </h3>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={handleAddFiles}
            disabled={isProcessing}
            className="text-green-700 hover:text-green-800 hover:bg-green-100"
          >
            <Plus className="h-4 w-4 mr-1" />
            Add more
          </Button>
        </div>
        
        <div className="space-y-3">
          {documents.map((doc) => (
            <div key={doc.id} className="bg-white rounded-lg p-3 border border-green-200">
              {renderFileStats(doc)}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}