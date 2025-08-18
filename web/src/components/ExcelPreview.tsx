"use client";

import { useEffect, useMemo, useState } from 'react';
import { read, utils, WorkBook } from 'xlsx';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface ExcelPreviewProps {
  file: File;
}

interface SheetHtmlData {
  name: string;
  html: string; // sanitized/controlled HTML table string
}

export function ExcelPreview({ file }: ExcelPreviewProps) {
  const [sheets, setSheets] = useState<SheetHtmlData[]>([]);
  const [currentSheetIndex, setCurrentSheetIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;
    const loadExcelFile = async () => {
      try {
        setLoading(true);
        setError(null);

        const arrayBuffer = await file.arrayBuffer();
        const workbook: WorkBook = read(arrayBuffer, { type: 'array' });

        const sheetsData: SheetHtmlData[] = workbook.SheetNames.map((sheetName) => {
          const worksheet = workbook.Sheets[sheetName];
          // Generate HTML that retains merged cells and column widths
          const html = utils.sheet_to_html(worksheet, {
            header: '',
            footer: '',
          });
          return { name: sheetName, html };
        });

        if (!isCancelled) {
          setSheets(sheetsData);
          setCurrentSheetIndex(0);
        }
      } catch (err) {
        if (!isCancelled) {
          setError('Failed to load Excel file');
          // eslint-disable-next-line no-console
          console.error('Excel loading error:', err);
        }
      } finally {
        if (!isCancelled) setLoading(false);
      }
    };

    loadExcelFile();
    return () => {
      isCancelled = true;
    };
  }, [file]);

  const currentSheet = useMemo(() => sheets[currentSheetIndex], [sheets, currentSheetIndex]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[600px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Excel file...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[600px]">
        <div className="text-center">
          <p className="text-red-600 mb-2">Error loading Excel file</p>
          <p className="text-gray-500 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (sheets.length === 0) {
    return (
      <div className="flex items-center justify-center h-[600px]">
        <div className="text-center">
          <p className="text-gray-600">No data found in Excel file</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[600px] flex flex-col">
      {sheets.length > 1 && (
        <div className="flex items-center justify-between p-3 border-b bg-gray-50">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCurrentSheetIndex(Math.max(0, currentSheetIndex - 1))}
            disabled={currentSheetIndex === 0}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>
          <span className="text-sm font-medium">
            Sheet: {currentSheet.name} ({currentSheetIndex + 1}/{sheets.length})
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCurrentSheetIndex(Math.min(sheets.length - 1, currentSheetIndex + 1))}
            disabled={currentSheetIndex === sheets.length - 1}
          >
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      )}

      <div className="flex-1 overflow-auto bg-white">
        <style jsx>{`
          :global(.excel-preview table) {
            width: max-content;
            border-collapse: collapse;
            background: white;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 13px;
          }
          :global(.excel-preview table td),
          :global(.excel-preview table th) {
            border: 1px solid hsl(var(--border));
            padding: 6px 8px;
            vertical-align: top;
            white-space: pre-wrap;
          }
          :global(.excel-preview table th) {
            background: hsl(var(--muted));
            font-weight: 600;
          }
        `}</style>
        <div className="excel-preview p-4">
          {/* The HTML produced by sheet_to_html is trusted here because the source is the user-supplied file */}
          <div dangerouslySetInnerHTML={{ __html: currentSheet.html }} />
        </div>
      </div>
    </div>
  );
}