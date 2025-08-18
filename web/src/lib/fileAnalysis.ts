import { FileStats } from '@/types';
import { FileText, Sheet, File } from 'lucide-react';

export function generateFileFingerprint(file: File): string {
  // Create a unique fingerprint based on file name, size, and last modified date
  return `${file.name}-${file.size}-${file.lastModified}`;
}

export async function analyzeFile(file: File): Promise<FileStats> {
  const baseStats: FileStats = {
    size: file.size,
    lastModified: new Date(file.lastModified),
    type: file.type,
    fingerprint: generateFileFingerprint(file),
  };

  // For PDFs, we can't easily get page count without a PDF parsing library
  // For now, we'll estimate based on file size (rough approximation)
  if (file.type === 'application/pdf') {
    // Very rough estimation: average PDF page is ~50-100KB
    const estimatedPages = Math.max(1, Math.round(file.size / 75000));
    baseStats.pages = estimatedPages;
  }

  // For Excel files, we can't analyze without a parsing library
  // For now, we'll provide default estimates
  if (file.type.includes('spreadsheet') || file.type.includes('excel') || 
      file.name.toLowerCase().endsWith('.xlsx') || file.name.toLowerCase().endsWith('.xls')) {
    // Default estimates for Excel files
    baseStats.sheets = 1; // Most files have at least 1 sheet
    baseStats.rows = Math.max(10, Math.round(file.size / 1000)); // Very rough estimation
  }

  return baseStats;
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

export function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

export function getFileIconComponent(file: File) {
  if (file.type === 'application/pdf') {
    return FileText;
  }
  if (file.type.includes('spreadsheet') || file.type.includes('excel') || 
      file.name.toLowerCase().endsWith('.xlsx') || file.name.toLowerCase().endsWith('.xls')) {
    return Sheet;
  }
  return File;
}

export function getFileIconColor(file: File): string {
  if (file.type === 'application/pdf') {
    return 'text-red-500';
  }
  if (file.type.includes('spreadsheet') || file.type.includes('excel') || 
      file.name.toLowerCase().endsWith('.xlsx') || file.name.toLowerCase().endsWith('.xls')) {
    return 'text-green-500';
  }
  return 'text-gray-500';
}