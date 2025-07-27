import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";

const CourseFileUpload = () => {
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  const courses = ['B.Tech', 'M.Tech', 'MCA'];

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFileName(acceptedFiles[0].name);
      console.log("Uploaded file:", acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': [],
    },
    multiple: false,
  });

  const handleSubmit = () => {
    if (!selectedCourse || !fileName) return;
    console.log("Selected course:", selectedCourse);
    console.log("Selected file:", fileName);
    // Add submission logic 
  };

  return (
    <div className="flex flex-col items-center gap-6 w-full">
      {/* Course Selection */}
      <div className="flex flex-wrap justify-center gap-4">
        {courses.map((course) => (
          <button
            key={course}
            onClick={() => setSelectedCourse((prev) => (prev === course ? null : course))}
            className={`border-2 rounded-2xl px-5 py-1 transition cursor-pointer ${
              selectedCourse === course
                ? 'border-blue-600 bg-blue-600 text-white'
                : 'border-gray-300 bg-white text-gray-800'
            }`}
          >
            {course}
          </button>
        ))}
      </div>

      {/* File Upload */}
      <div
        {...getRootProps()}
        className="flex text-center w-full px-2 border-2 border-dashed rounded-2xl items-center justify-center cursor-pointer text-gray-500"
        style={{ height: '140px' }}
      >
        <input {...getInputProps()} />
        {fileName ? (
          <p className="text-gray-700 break-words">{fileName}</p>
        ) : isDragActive ? (
          <p>Drop files here ...</p>
        ) : (
          <p>Drag & drop the file here, or click to select</p>
        )}
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={!selectedCourse || !fileName}
        className={`px-10 py-3 rounded-2xl font-semibold shadow-md transition text-white ${
          selectedCourse && fileName
            ? 'bg-blue-600 hover:bg-blue-500 cursor-pointer'
            : 'bg-gray-400 cursor-not-allowed'
        }`}
      >
        Submit
      </button>
    </div>
  );
};

export default CourseFileUpload;
