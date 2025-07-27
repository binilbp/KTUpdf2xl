import { useState } from "react";

const UploadOpts = () => {
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);

  const courses = ['B.Tech', 'M.Tech', 'MCA'];

  const handleSubmit = () => {
    if (!selectedCourse) return;
    console.log("Selected course:", selectedCourse);
  };

  return (
    <div className="flex flex-col items-center gap-6 w-full">
      <div className="flex flex-wrap justify-center gap-4">
        {courses.map((course) => (
          <button
            key={course}
            onClick={() => setSelectedCourse(course)}
            className={`border-2 rounded-2xl px-5 py-1 transition cursor-pointer ${
              selectedCourse === course ? 'border-primary bg-primary text-white' : ''
            }`}
          >
            {course}
          </button>
        ))}
      </div>

      <button
        onClick={handleSubmit}
        disabled={!selectedCourse}
        className={`px-10 py-3 rounded-2xl font-semibold shadow-md transition text-white ${
          selectedCourse ? 'bg-accent hover:bg-blue-400 cursor-pointer' : 'bg-gray-400 cursor-not-allowed'
        }`}
      >
        Submit
      </button>
    </div>
  );
};

export default UploadOpts;
