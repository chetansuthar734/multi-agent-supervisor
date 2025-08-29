// message.name ==code , ui show code and output , copy code 


import React from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

const CodeUI = ({ code, language = "javascript" }) => {
  return (
    <div style={{width:"700px" }} className="rounded-2xl shadow-md bg-gray-900 text-white p-3 my-2 overflow-x-auto">
      <SyntaxHighlighter
        language={language}
        style={oneDark}
        customStyle={{
          borderRadius: "1rem",
          padding: "1rem",
          fontSize: "0.9rem",
        }}
        wrapLongLines
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
};

export default CodeUI;
