import React, { useState, useRef, useEffect } from 'react';
// import { useAuth } from '../context/AuthContext'; // Removed unused import
import VoiceChat from './VoiceChat';
import useFileUpload from '../hooks/useFileUpload';
import { Card, Alert, Table, TableHead, TableHeadCell, TableBody, TableRow, TableCell, Spinner as FlowbiteSpinner } from 'flowbite-react';
import { ShimmerButton } from './ui/shimmer-button';

const QuizModeSelector: React.FC = () => {
  // const { user } = useAuth(); // Removed unused variable
  const [selectedMode, setSelectedMode] = useState<'descriptive' | 'quick' | 'multiple' | null>(null);
  const [connectionInfo, setConnectionInfo] = useState<{ url: string; token: string } | null>(null);
  const { uploadedFiles, isUploading, uploadMessage, fetchUploadedFiles, handleFileUpload, handleDeleteFile } = useFileUpload();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleConnect = (url: string, token: string) => {
    setConnectionInfo({ url, token });
  };

  const handleDisconnect = () => {
    setConnectionInfo(null);
  };

  useEffect(() => {
    fetchUploadedFiles();
  }, [fetchUploadedFiles]);

  const handleFileInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    await handleFileUpload(files);
    
    // Clear the file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const renderModeDescription = () => {
    switch (selectedMode) {
      case 'descriptive':
        return {
          title: 'Descriptive Voice Quiz',
          description: 'Practice speaking with our AI tutor. Answer questions descriptively and get feedback on grammar, pronunciation, and content accuracy.',
          icon: (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-accent-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
          ),
          bgColor: 'bg-accent-100 dark:bg-accent-900/30',
          buttonColor: 'bg-accent-500 hover:bg-accent-600'
        };
      case 'quick':
        return {
          title: 'Quick Quiz Mode',
          description: 'Rapid-fire questions with a 2-minute timer. Practice quick thinking and concise responses.',
          icon: (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-success-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ),
          bgColor: 'bg-success-100 dark:bg-success-900/30',
          buttonColor: 'bg-success-500 hover:bg-success-600'
        };
      case 'multiple':
        return {
          title: 'Multiple Choice Quiz',
          description: 'Interactive multiple choice questions that require visual attention. Perfect for testing comprehension.',
          icon: (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-secondary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          ),
          bgColor: 'bg-secondary-100 dark:bg-secondary-900/30',
          buttonColor: 'bg-secondary-500 hover:bg-secondary-600'
        };
      default:
        return null;
    }
  };

  const modeInfo = renderModeDescription();

  if (selectedMode) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <ShimmerButton
            onClick={() => setSelectedMode(null)}
            className="px-6 py-3 text-base rounded-xl shadow-lg"
            shimmerColor="#000000"
            background="rgba(243, 244, 246, 1)" // gray-100
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            Back to Mode Selection
          </ShimmerButton>
        </div>

        <Card className="mb-8">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
            <div className="flex-shrink-0">
              {modeInfo?.icon}
            </div>
            <div className="flex-1 text-center md:text-left">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{modeInfo?.title}</h2>
              <p className="text-gray-600 dark:text-gray-300">{modeInfo?.description}</p>
            </div>
          </div>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Voice Control Panel */}
          <div className="lg:col-span-2">
            <Card 
              className={`transition-all duration-500 ${
                connectionInfo 
                  ? 'bg-gradient-to-r from-accent-50 to-success-50 dark:from-accent-900/20 dark:to-success-900/20 shadow-lg' 
                  : ''
              } hover:shadow-2xl`}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Voice Session</h2>
                <div className="flex items-center">
                  <div className={`h-3 w-3 rounded-full mr-2 ${
                    connectionInfo ? 'bg-success-500 animate-pulse' : 'bg-gray-400'
                  }`}></div>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {connectionInfo ? 'Live' : 'Disconnected'}
                  </span>
                </div>
              </div>

              <div className="flex flex-col items-center justify-center py-12">
                <VoiceChat onConnect={handleConnect} onDisconnect={handleDisconnect} />
              </div>
            </Card>
          </div>

          {/* Info Panel */}
          <div>
            <Card className="mb-8 transition-all duration-300 hover:shadow-2xl">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Connection History</h2>
              <div className="overflow-x-auto max-h-96 overflow-y-auto">
                <table className="table-modern">
                  <thead>
                    <tr>
                      <th scope="col">
                        Duration (secs)
                      </th>
                      <th scope="col">
                        Session Date
                      </th>
                      <th scope="col">
                        Start Time
                      </th>
                      <th scope="col">
                        End Time
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {/* Dummy data for connection history */}
                    <tr>
                      <td>180</td>
                      <td>2025-08-15</td>
                      <td>14:30</td>
                      <td>14:33</td>
                    </tr>
                    <tr>
                      <td>245</td>
                      <td>2025-08-12</td>
                      <td>10:15</td>
                      <td>10:19</td>
                    </tr>
                    <tr>
                      <td>156</td>
                      <td>2025-08-10</td>
                      <td>16:45</td>
                      <td>16:48</td>
                    </tr>
                    <tr>
                      <td>312</td>
                      <td>2025-08-08</td>
                      <td>09:00</td>
                      <td>09:05</td>
                    </tr>
                    <tr>
                      <td>98</td>
                      <td>2025-08-05</td>
                      <td>13:20</td>
                      <td>13:22</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Move the Upload Study Materials section to the top */}
      <Card className="mb-12">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Upload Study Materials</h2>
          <p className="text-gray-600 dark:text-gray-300">
            Upload your school chapters to generate personalized quizzes
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 transition-all duration-300 hover:border-accent-500">
            <div className="text-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">Upload your study materials</h3>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                PDF, DOC, or TXT files containing school chapters will be used to generate your personalized quizzes.
              </p>
              
              <div className="mt-6">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileInputChange}
                  multiple
                  accept=".pdf,.doc,.docx,.txt"
                  className="hidden"
                />
                <button
                  onClick={triggerFileInput}
                  disabled={isUploading}
                  className="btn-primary"
                >
                  {isUploading ? (
                    <span className="flex items-center">
                      <FlowbiteSpinner className="mr-2" size="sm" />
                      Uploading...
                    </span>
                  ) : 'Select Files'}
                </button>
              </div>
              
              {uploadMessage && (
                <Alert color={uploadMessage.type === 'success' ? 'success' : 'failure'} className="mt-4">
                  {uploadMessage.text}
                </Alert>
              )}
              
              <p className="mt-4 text-xs text-gray-500 dark:text-gray-400">
                All files are processed securely and only used for generating your quizzes.
              </p>
            </div>
          </div>
          
          {/* Uploaded Files List */}
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Uploaded Files</h3>
            
            {uploadedFiles.length === 0 ? (
              <div className="text-center py-8">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No files uploaded</h3>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  Get started by uploading your study materials.
                </p>
              </div>
            ) : (
              <div className="overflow-hidden rounded-2xl border border-gray-200 dark:border-gray-700">
                <Table className="table-modern">
                  <TableHead>
                    <TableHeadCell>
                      Subject
                    </TableHeadCell>
                    <TableHeadCell>
                      File Name
                    </TableHeadCell>
                    <TableHeadCell className="text-right">
                      Actions
                    </TableHeadCell>
                  </TableHead>
                  <TableBody>
                    {uploadedFiles.map((file) => (
                      <TableRow key={file.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                        <TableCell className="font-medium">
                          {file.subject}
                        </TableCell>
                        <TableCell className="max-w-xs truncate">
                          {file.fileName}
                        </TableCell>
                        <TableCell className="text-right">
                          <button
                            onClick={() => handleDeleteFile(file.id)}
                            className="btn-danger p-1 rounded-full"
                            title="Delete file"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                            </svg>
                          </button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </div>
        </div>
      </Card>
      
      <div className="text-center mb-12">
        <h1 className="text-3xl md:text-4xl font-extrabold text-gray-900 dark:text-white mb-4">
          Select Quiz Mode
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Choose from different quiz modes based on your learning objectives. All questions are generated from your uploaded study materials.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Descriptive Voice Quiz */}
        <Card 
          className="card-modern cursor-pointer transition-all duration-300 hover:-translate-y-1"
          onClick={() => setSelectedMode('descriptive')}
        >
          <div className="flex justify-center mb-4">
            <div className="h-16 w-16 rounded-full bg-gradient-to-r from-accent-100 to-accent-200 dark:from-accent-900 dark:to-accent-800 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-accent-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              </svg>
            </div>
          </div>
          <h2 className="text-xl font-bold text-center text-gray-900 dark:text-white mb-2">Descriptive Quiz</h2>
          <p className="text-gray-600 dark:text-gray-300 text-center mb-4">
            Answer questions with detailed verbal responses. Get comprehensive feedback on grammar, pronunciation, and content.
          </p>
          <div className="bg-gradient-to-r from-accent-50 to-accent-100 dark:from-accent-900/30 dark:to-accent-900/20 rounded-xl p-4 mb-4">
            <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-2">
              <li className="flex items-start">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-accent-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Grammar and pronunciation analysis</span>
              </li>
              <li className="flex items-start">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-accent-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Content accuracy verification</span>
              </li>
              <li className="flex items-start">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-accent-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Detailed improvement suggestions</span>
              </li>
            </ul>
          </div>
          <ShimmerButton 
            className="w-full px-6 py-3 text-base rounded-xl shadow-lg"
            shimmerColor="#ffffff"
            background="rgba(56, 189, 248, 1)" // primary-500
          >
            Select Mode
          </ShimmerButton>
        </Card>

        {/* Quick Quiz Mode */}
        <Card 
          className="card-modern cursor-pointer transition-all duration-300 hover:-translate-y-1"
          onClick={() => setSelectedMode('quick')}
        >
          <div className="flex justify-center mb-4">
            <div className="h-16 w-16 rounded-full bg-gradient-to-r from-success-100 to-success-200 dark:from-success-900 dark:to-success-800 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-success-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <h2 className="text-xl font-bold text-center text-gray-900 dark:text-white mb-2">Quick Quiz</h2>
          <p className="text-gray-600 dark:text-gray-300 text-center mb-4">
            Fast-paced questions with a 2-minute timer. Practice quick thinking and concise verbal responses.
          </p>
          <div className="bg-gradient-to-r from-success-50 to-success-100 dark:from-success-900/30 dark:to-success-900/20 rounded-xl p-4 mb-4">
            <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-2">
              <li className="flex items-start">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-success-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>2-minute time limit</span>
              </li>
              <li className="flex items-start">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-success-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Less than 10-word answers</span>
              </li>
              <li className="flex items-start">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-success-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Rapid skill building</span>
              </li>
            </ul>
          </div>
          <ShimmerButton 
            className="w-full px-6 py-3 text-base rounded-xl shadow-lg"
            shimmerColor="#ffffff"
            background="rgba(34, 197, 94, 1)" // success-500
          >
            Select Mode
          </ShimmerButton>
        </Card>

        {/* Multiple Choice Quiz */}
        <Card 
          className="card-modern cursor-pointer transition-all duration-300 hover:-translate-y-1"
          onClick={() => setSelectedMode('multiple')}
        >
          <div className="flex justify-center mb-4">
            <div className="h-16 w-16 rounded-full bg-gradient-to-r from-secondary-100 to-secondary-200 dark:from-secondary-900 dark:to-secondary-800 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-secondary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>
          <h2 className="text-xl font-bold text-center text-gray-900 dark:text-white mb-2">Multiple Choice</h2>
          <p className="text-gray-600 dark:text-gray-300 text-center mb-4">
            Interactive multiple choice questions. Requires visual attention and quick decision making.
          </p>
          <div className="bg-gradient-to-r from-secondary-50 to-secondary-100 dark:from-secondary-900/30 dark:to-secondary-900/20 rounded-xl p-4 mb-4">
            <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-2">
              <li className="flex items-start">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-secondary-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Visual question format</span>
              </li>
              <li className="flex items-start">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-secondary-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Screen-based interaction</span>
              </li>
              <li className="flex items-start">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-secondary-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Immediate scoring</span>
              </li>
            </ul>
          </div>
          <ShimmerButton 
            className="w-full px-6 py-3 text-base rounded-xl shadow-lg"
            shimmerColor="#ffffff"
            background="rgba(139, 92, 246, 1)" // secondary-500
          >
            Select Mode
          </ShimmerButton>
        </Card>
      </div>
    </div>
  );
};

export default QuizModeSelector;