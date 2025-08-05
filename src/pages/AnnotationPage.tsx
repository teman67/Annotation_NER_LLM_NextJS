import React, { useState } from "react";
import {
  DocumentTextIcon,
  PlayIcon,
  StopIcon,
} from "@heroicons/react/24/outline";

const AnnotationPage: React.FC = () => {
  const [text, setText] = useState("");
  const [isAnnotating, setIsAnnotating] = useState(false);
  const [selectedModel, setSelectedModel] = useState("gpt-4");
  const [selectedTagSet, setSelectedTagSet] = useState("");

  const handleAnnotate = async () => {
    if (!text.trim()) return;

    setIsAnnotating(true);
    // Simulate annotation process
    setTimeout(() => {
      setIsAnnotating(false);
    }, 3000);
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Text Annotation</h1>
        <p className="mt-1 text-sm text-gray-500">
          Annotate scientific text using AI models with custom tag definitions.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input Panel */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Input Text</h3>
            </div>
            <div className="p-6">
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                rows={12}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Enter or paste your scientific text here..."
              />
              <div className="mt-4 flex justify-between items-center">
                <div className="text-sm text-gray-500">
                  {text.length} characters
                </div>
                <button
                  onClick={handleAnnotate}
                  disabled={isAnnotating || !text.trim()}
                  className={`flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                    isAnnotating || !text.trim()
                      ? "bg-gray-400 cursor-not-allowed"
                      : "bg-primary-600 hover:bg-primary-700"
                  }`}
                >
                  {isAnnotating ? (
                    <>
                      <StopIcon className="h-4 w-4 mr-2" />
                      Annotating...
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-4 w-4 mr-2" />
                      Start Annotation
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Settings Panel */}
        <div>
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Settings</h3>
            </div>
            <div className="p-6 space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  AI Model
                </label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="claude-3">Claude 3</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tag Set
                </label>
                <select
                  value={selectedTagSet}
                  onChange={(e) => setSelectedTagSet(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">Select a tag set...</option>
                  <option value="biomedical">Biomedical NER</option>
                  <option value="sentiment">Sentiment Analysis</option>
                  <option value="custom">Custom Tags</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Temperature
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  defaultValue="0.1"
                  className="w-full"
                />
                <div className="text-xs text-gray-500 mt-1">
                  Lower = more consistent, Higher = more creative
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <h4 className="text-sm font-medium text-gray-900 mb-2">
                  Cost Estimate
                </h4>
                <div className="text-sm text-gray-600">
                  <div>Input tokens: ~{Math.ceil(text.length / 4)}</div>
                  <div>
                    Estimated cost: $
                    {(((text.length / 4) * 0.01) / 1000).toFixed(4)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Results Panel */}
      <div className="mt-8">
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Annotation Results
            </h3>
          </div>
          <div className="p-6">
            {isAnnotating ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                <p className="text-gray-500">
                  Analyzing text and generating annotations...
                </p>
              </div>
            ) : !text.trim() ? (
              <div className="text-center py-12">
                <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">
                  Enter text above to see annotation results
                </p>
              </div>
            ) : (
              <div className="text-center py-12">
                <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">
                  Click "Start Annotation" to begin
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnnotationPage;
