import React from 'react';

type TextButtonProps = {
  text: string;
  callback: () => void;
};

export default function TextButton({ text, callback }: Readonly<TextButtonProps>) {
  return (
    <button
      onClick={callback}
      className="text-blue-600 hover:underline p-0 m-0 bg-transparent border-none cursor-pointer"
      type="button"
    >
      {text}
    </button>
  );
}
