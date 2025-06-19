import { useState } from "react";

const UploadOpts = () => {
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);

  const courses = ['B.Tech', 'M.Tech', 'MCA'];

  return (
    <div className="flex flex-col items-center gap-6 w-full">
      <div className="flex flex-wrap justify-center gap-4">
        {courses.map((course) => ( //dynamically add button for each course using map
          <button
            key={course}
            onClick={() => setSelectedCourse(course)}
            className={`border-2 rounded-2xl px-5 py-1 cursor-pointer transition ${
              selectedCourse === course ? 'border-(--primary-color) text-white bg-(--primary-color)' : ''
            }`}
          >
            {course}
          </button>
        ))}
      </div>

      <button className="bg-(--primary-accent-color) px-10 py-3 text-white rounded-2xl font-semibold shadow-md hover:bg-blue-400 transition cursor-pointer">
        Submit
      </button>
    </div>
  );
};

export default UploadOpts;
