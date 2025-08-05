import React from "react";
import { TagIcon, PlusIcon } from "@heroicons/react/24/outline";

const TagsPage: React.FC = () => {
  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tag Sets</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your custom tag definitions for annotation tasks.
          </p>
        </div>
        <button className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg flex items-center">
          <PlusIcon className="h-5 w-5 mr-2" />
          Create Tag Set
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Sample tag sets */}
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <TagIcon className="h-8 w-8 text-primary-600" />
              <span className="text-xs text-gray-500">5 tags</span>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {i === 1
                ? "Biomedical NER"
                : i === 2
                ? "Sentiment Analysis"
                : `Tag Set ${i}`}
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              {i === 1
                ? "Named entity recognition for biomedical texts including genes, proteins, and diseases."
                : i === 2
                ? "Sentiment classification for positive, negative, and neutral expressions."
                : "Custom tag definitions for specific annotation requirements."}
            </p>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">Updated 2 days ago</span>
              <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                Edit
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TagsPage;
