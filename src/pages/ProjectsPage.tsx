import React from "react";
import { FolderIcon, PlusIcon } from "@heroicons/react/24/outline";

const ProjectsPage: React.FC = () => {
  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="mt-1 text-sm text-gray-500">
            Organize your annotation work into projects.
          </p>
        </div>
        <button className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg flex items-center">
          <PlusIcon className="h-5 w-5 mr-2" />
          New Project
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Sample projects */}
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <FolderIcon className="h-8 w-8 text-primary-600" />
              <span className="text-xs text-gray-500">
                {Math.floor(Math.random() * 50)} annotations
              </span>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {i === 1
                ? "Gene Expression Study"
                : i === 2
                ? "Protein Analysis"
                : `Research Project ${i}`}
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              Annotation project for analyzing scientific literature and
              extracting relevant entities.
            </p>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">Updated 1 day ago</span>
              <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                Open
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProjectsPage;
