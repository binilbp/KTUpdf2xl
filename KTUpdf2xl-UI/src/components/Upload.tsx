import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";

const Upload = () => {
  const [fileName, setFileName] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles : File[]) => {
    if(acceptedFiles.length > 0){
      setFileName(acceptedFiles[0].name);
      console.log(acceptedFiles);
    }
  }, []);

  const {getRootProps, getInputProps, isDragActive} = useDropzone({ 
    onDrop,
    accept: {
      'application/pdf' : [],
    }, 
    multiple : false,
  });

  return (
    <div {...getRootProps()} className="flex text-center w-full h-35 px-2 border-2 border-dashed rounded-2xl items-center justify-center 
                                        text-(--secondary-text-color) cursor-pointer ">
        <input {...getInputProps()}/>
        {
          fileName ? <p className="text-gray-600 text-wrap">{fileName}</p> :
          isDragActive ? <p>Drop Files Here ...</p>:<p>Drag & drop the files here, or click to select files</p>
        }
    </div>
  );
}

export default Upload;