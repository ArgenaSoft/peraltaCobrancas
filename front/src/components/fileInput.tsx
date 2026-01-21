'use client';

import { useRef, useState } from 'react';


type FileInputProps = {
  label: string;
  accept?: string;
  name: string;
  callback?: (file: File) => void;
};

export function FileInput({ label = "Selecionar arquivo", accept, name, callback }: Readonly<FileInputProps>) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string>(label);

  return (
    <div className="flex flex-col gap-2">

      <input
        ref={inputRef}
        type="file"
        name={name}
        accept={accept}
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (!file) return;
          setFileName(file.name || label);
          if (callback) {
            callback(file);
          }
        }}
      />

      <button
        type="button"
        className="rounded-md bg-gray p-1 border-black border-1"
        onClick={() => inputRef.current?.click()}
      >
        {fileName}
      </button>
    </div>
  );
}
