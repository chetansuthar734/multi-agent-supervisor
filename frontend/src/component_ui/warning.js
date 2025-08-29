import React from "react";
import { AlertTriangle } from "lucide-react"; // nice warning icon

const WarningUI = ({ message }) => {
  return (
    <div style={{color:'yellow'}} className="flex items-start gap-3 p-4 my-3 rounded-2xl shadow-md bg-yellow-100 border-l-4 border-yellow-500">
      <AlertTriangle className="text-yellow-600 w-6 h-6 mt-1" />
      <p className="text-yellow-800 font-medium">{message}</p>
    </div>
  );
};

export default WarningUI;
