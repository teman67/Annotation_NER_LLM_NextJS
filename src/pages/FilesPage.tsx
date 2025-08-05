import React from "react";
import { DocumentIcon, CloudArrowUpIcon } from "@heroicons/react/24/outline";

const FilesPage: React.FC = () => {
  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Files</h1>
          <p className="mt-1 text-sm text-gray-500">
            Upload and manage your text files for annotation.
          </p>
        </div>
        <button className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg flex items-center">
          <CloudArrowUpIcon className="h-5 w-5 mr-2" />
          Upload File
        </button>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Files</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className="px-6 py-4 flex items-center justify-between"
            >
              <div className="flex items-center">
                <DocumentIcon className="h-8 w-8 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    research_paper_{i}.txt
                  </p>
                  <p className="text-sm text-gray-500">
                    {Math.floor(Math.random() * 100) + 50} KB • Uploaded {i}{" "}
                    days ago
                  </p>
                </div>
              </div>
              <div className="flex space-x-2">
                <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                  Annotate
                </button>
                <button className="text-gray-600 hover:text-gray-700 text-sm font-medium">
                  Download
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FilesPage;
