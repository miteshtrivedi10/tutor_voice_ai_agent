import { useState } from 'react';

interface UploadedFile {
  id: string;
  subject: string;
  fileName: string;
  uploadDate: string;
}

interface UseFileUploadReturn {
  uploadedFiles: UploadedFile[];
  isUploading: boolean;
  uploadMessage: { type: 'success' | 'error'; text: string } | null;
  fetchUploadedFiles: () => Promise<void>;
  handleFileUpload: (files: FileList) => Promise<void>;
  handleDeleteFile: (fileId: string) => Promise<void>;
}

const useFileUpload = (): UseFileUploadReturn => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Fetch uploaded files from API
  const fetchUploadedFiles = async () => {
    try {
      // In a real implementation, this would fetch from an API endpoint
      // For now, we'll use dummy data to simulate the response
      const dummyFiles: UploadedFile[] = [
        { id: '1', subject: 'Science', fileName: 'Biology Chapter 1.pdf', uploadDate: '2023-05-15' },
        { id: '2', subject: 'Mathematics', fileName: 'Algebra_Formulas.docx', uploadDate: '2023-05-16' },
        { id: '3', subject: 'History', fileName: 'World_War_II_Summary.pdf', uploadDate: '2023-05-17' },
      ];
      setUploadedFiles(dummyFiles);
    } catch (error) {
      console.error('Error fetching files:', error);
      setUploadMessage({ type: 'error', text: 'Failed to load uploaded files.' });
    }
  };

  const handleFileUpload = async (files: FileList) => {
    if (files.length === 0) return;

    setIsUploading(true);
    setUploadMessage(null);

    try {
      // Create FormData for file upload
      const formData = new FormData();
      
      // Append files to formData
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
      }
      
      // In a real implementation, you would use the API_CONFIG.BASE_URL
      const apiUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
      
      // API endpoint from documentation
      const response = await fetch(`${apiUrl}/upload-files`, {
        method: 'POST',
        body: formData,
        // Note: Don't set Content-Type header when using FormData, 
        // browser will set it correctly with boundary
      });

      if (response.ok) {
        await response.json(); // Parse but don't use result
        setUploadMessage({ type: 'success', text: 'Files uploaded successfully!' });
        
        // Refresh the file list
        await fetchUploadedFiles();
      } else {
        const errorText = await response.text();
        setUploadMessage({ type: 'error', text: `Upload failed: ${errorText}` });
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadMessage({ type: 'error', text: 'An error occurred during upload. Please try again.' });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteFile = async (fileId: string) => {
    try {
      // In a real implementation, this would call a delete API endpoint
      // For now, we'll just simulate the deletion
      setUploadedFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
      setUploadMessage({ type: 'success', text: 'File deleted successfully!' });
    } catch (error) {
      console.error('Error deleting file:', error);
      setUploadMessage({ type: 'error', text: 'Failed to delete file.' });
    }
  };

  return {
    uploadedFiles,
    isUploading,
    uploadMessage,
    fetchUploadedFiles,
    handleFileUpload,
    handleDeleteFile
  };
};

export default useFileUpload;