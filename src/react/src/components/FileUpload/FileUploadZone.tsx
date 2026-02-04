// src/components/FileUpload/FileUploadZone.tsx
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, CheckCircle } from 'lucide-react';

interface FileUploadZoneProps {
  label: string;
  accept: string;
  multiple?: boolean;
  required?: boolean;
  files: File[];
  onFilesChange: (files: File[]) => void;
  description?: string;
}

export const FileUploadZone: React.FC<FileUploadZoneProps> = ({
  label,
  accept,
  multiple = false,
  required = false,
  files,
  onFilesChange,
  description,
}) => {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (multiple) {
        onFilesChange([...files, ...acceptedFiles]);
      } else {
        onFilesChange(acceptedFiles.slice(0, 1));
      }
    },
    [files, multiple, onFilesChange]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'image/*': ['.jpg', '.jpeg', '.png'] },
    multiple,
  });

  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index);
    onFilesChange(newFiles);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="mb-6">
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {description && (
        <p className="text-sm text-gray-500 mb-3">{description}</p>
      )}

      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all
          ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400'}
          ${files.length > 0 ? 'bg-green-50 border-green-300' : 'bg-white'}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center">
          {files.length > 0 ? (
            <CheckCircle className="w-12 h-12 text-green-500 mb-3" />
          ) : (
            <Upload className="w-12 h-12 text-gray-400 mb-3" />
          )}
          
          {isDragActive ? (
            <p className="text-primary-600 font-medium">Drop the files here...</p>
          ) : (
            <>
              <p className="text-gray-700 font-medium mb-1">
                {files.length > 0 ? `${files.length} file(s) selected` : 'Click to upload or drag and drop'}
              </p>
              <p className="text-sm text-gray-500">
                {accept === 'application/pdf' ? 'PDF files only' : 'PDF or Image files'}
              </p>
            </>
          )}
        </div>
      </div>

      {/* Display uploaded files */}
      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-shadow"
            >
              <div className="flex items-center space-x-3">
                <FileText className="w-5 h-5 text-primary-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{file.name}</p>
                  <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                </div>
              </div>
              
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile(index);
                }}
                className="p-1 hover:bg-red-50 rounded-full transition-colors"
                type="button"
              >
                <X className="w-4 h-4 text-red-500" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
