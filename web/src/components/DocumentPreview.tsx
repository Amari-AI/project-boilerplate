import { FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DocumentData } from '@/types';
import { ExcelPreview } from './ExcelPreview';
import { formatFileSize, formatDate, getFileIconComponent, getFileIconColor } from '@/lib/fileAnalysis';

interface DocumentPreviewProps {
  document: DocumentData | null;
}

export function DocumentPreview({ document }: DocumentPreviewProps) {
  if (!document) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Document Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[600px] border rounded bg-gray-50">
            <div className="text-center">
              <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-gray-500">No document selected</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const { file, stats } = document;
  const IconComponent = getFileIconComponent(file);
  const iconColor = getFileIconColor(file);
  const isPdf = file.type === "application/pdf";
  const isExcel = file.type.includes('spreadsheet') || file.type.includes('excel') || 
                  file.name.toLowerCase().endsWith('.xlsx') || file.name.toLowerCase().endsWith('.xls');

  return (
    <Card>
      <CardHeader>
        <CardTitle>Document Preview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Document Information */}
        <div className="p-4 bg-gray-50 rounded-lg border">
          <div className="flex items-start gap-3">
            <IconComponent className={`h-6 w-6 ${iconColor} mt-1`} />
            <div className="flex-1 min-w-0">
              <h4 className="font-medium text-gray-900 truncate mb-2">{file.name}</h4>
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
          </div>
        </div>

        {/* Document Preview */}
        <div className="border rounded-lg overflow-hidden">
          {isPdf ? (
            <iframe
              src={`${document.documentUrl}#toolbar=0&navpanes=0&scrollbar=0`}
              className="w-full h-[600px]"
              title="Document Preview"
              style={{
                border: 'none',
                background: 'white'
              }}
            />
          ) : isExcel ? (
            <ExcelPreview file={file} />
          ) : (
            <div className="flex items-center justify-center h-[600px] bg-gray-50">
              <div className="text-center">
                <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p className="text-gray-500 mb-2">{file.name}</p>
                <p className="text-sm text-gray-400">
                  Preview not available for this file type
                </p>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}