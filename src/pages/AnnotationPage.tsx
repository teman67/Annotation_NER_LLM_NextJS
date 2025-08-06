import React, { useState, useMemo } from "react";
import {
  PlayIcon,
  EyeIcon,
  TrashIcon,
  AdjustmentsHorizontalIcon,
  CheckCircleIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";
import LoadingSpinner from "../components/LoadingSpinner";
import ExportComponent from "../components/ExportComponent";
import ValidationComponent from "../components/ValidationComponent";
import CostCalculator from "../components/CostCalculator";
import { API_CONFIG } from "../constants/api";

// Local types for annotation
interface AnnotationTag {
  tag_name: string;
  definition: string;
  examples: string;
}

interface AnnotationEntity {
  start_char: number;
  end_char: number;
  text: string;
  label: string;
  confidence?: number;
  source?: "llm" | "manual";
}

interface AnnotationResult {
  entities: AnnotationEntity[];
  statistics: {
    total_entities: number;
    chunks_processed: number;
    total_input_tokens: number;
    total_output_tokens: number;
    total_tokens: number;
  };
}

const AnnotationPage: React.FC = () => {
  // Main state
  const [text, setText] = useState("");
  const [tags, setTags] = useState<AnnotationTag[]>([]);
  const [entities, setEntities] = useState<AnnotationEntity[]>([]);
  const [manualEntities, setManualEntities] = useState<AnnotationEntity[]>([]);
  const [selectedEntity, setSelectedEntity] = useState<AnnotationEntity | null>(
    null
  );

  // Processing state
  const [isAnnotating, setIsAnnotating] = useState(false);

  // Results state
  const [annotationResult, setAnnotationResult] =
    useState<AnnotationResult | null>(null);

  // Settings state
  const [selectedModel, setSelectedModel] = useState("gpt-4o-mini");
  const [temperature, setTemperature] = useState(0.1);
  const [maxTokens, setMaxTokens] = useState(1000);
  const [chunkSize, setChunkSize] = useState(1000);
  const [overlap, setOverlap] = useState(50);

  // UI state
  const [activeTab, setActiveTab] = useState<
    "annotation" | "validation" | "export"
  >("annotation");
  const [showSettings, setShowSettings] = useState(false);
  const [selectedText, setSelectedText] = useState("");
  const [selectedRange, setSelectedRange] = useState<{
    start: number;
    end: number;
  } | null>(null);

  // Calculate combined entities
  const combinedEntities = useMemo(() => {
    const combined = [
      ...entities.map((e) => ({ ...e, source: "llm" as const })),
      ...manualEntities.map((e) => ({ ...e, source: "manual" as const })),
    ];
    return combined.sort((a, b) => a.start_char - b.start_char);
  }, [entities, manualEntities]);

  // Token recommendations
  const tokenRecommendations = useMemo(() => {
    const inputTokens = Math.ceil(chunkSize / 4);
    const minTokens = Math.max(100, Math.floor(inputTokens / 2));
    const maxTokensLimit = Math.min(4000, inputTokens * 3);
    const defaultTokens = Math.min(2000, inputTokens * 2);

    return {
      min_tokens: minTokens,
      max_tokens_limit: maxTokensLimit,
      default_tokens: defaultTokens,
      input_tokens_estimate: inputTokens,
    };
  }, [chunkSize]);

  // Load tags from CSV file
  const handleTagsFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const csv = e.target?.result as string;
        const lines = csv.split("\n");

        const parsedTags: AnnotationTag[] = [];
        for (let i = 1; i < lines.length; i++) {
          const values = lines[i].split(",");
          if (values.length >= 3) {
            parsedTags.push({
              tag_name: values[0]?.trim() || "",
              definition: values[1]?.trim() || "",
              examples: values[2]?.trim() || "",
            });
          }
        }
        setTags(parsedTags);
      };
      reader.readAsText(file);
    }
  };

  // Load text from file
  const handleTextFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setText(content);
      };
      reader.readAsText(file);
    }
  };

  // Main annotation function
  const handleAnnotate = async () => {
    if (!text.trim() || tags.length === 0) return;

    setIsAnnotating(true);
    try {
      const response = await fetch(
        `${API_CONFIG.API_BASE_URL}/annotations/annotate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: JSON.stringify({
            text,
            tag_definitions: tags,
            model: selectedModel,
            temperature,
            max_tokens: maxTokens,
            chunk_size: chunkSize,
            overlap,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Annotation failed");
      }

      const result: AnnotationResult = await response.json();
      setAnnotationResult(result);
      setEntities(result.entities);
    } catch (error) {
      console.error("Annotation error:", error);
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Annotation failed. Please check your API keys in your profile settings.";
      alert(errorMessage);
    } finally {
      setIsAnnotating(false);
    }
  };

  // Add manual annotation
  const handleAddManualAnnotation = (label: string) => {
    if (!selectedRange || !selectedText.trim()) return;

    const newEntity: AnnotationEntity = {
      start_char: selectedRange.start,
      end_char: selectedRange.end,
      text: selectedText,
      label,
      confidence: 1.0,
      source: "manual",
    };

    setManualEntities((prev) => [...prev, newEntity]);
    setSelectedText("");
    setSelectedRange(null);
  };

  // Remove entity
  const handleRemoveEntity = (entity: AnnotationEntity) => {
    if (entity.source === "manual") {
      setManualEntities((prev) => prev.filter((e) => e !== entity));
    } else {
      setEntities((prev) => prev.filter((e) => e !== entity));
    }
  };

  // Render highlighted text
  const renderHighlightedText = () => {
    if (!text || combinedEntities.length === 0) {
      return (
        <div className="whitespace-pre-wrap p-4 bg-gray-50 rounded border min-h-64">
          {text}
        </div>
      );
    }

    const sortedEntities = [...combinedEntities].sort(
      (a, b) => a.start_char - b.start_char
    );
    const elements: React.ReactNode[] = [];
    let lastEnd = 0;

    sortedEntities.forEach((entity, index) => {
      // Add text before entity
      if (entity.start_char > lastEnd) {
        elements.push(text.slice(lastEnd, entity.start_char));
      }

      // Add highlighted entity
      const isSelected = selectedEntity === entity;
      const colorClass =
        entity.source === "manual"
          ? "bg-yellow-200 border-yellow-400"
          : "bg-blue-200 border-blue-400";

      elements.push(
        <span
          key={index}
          className={`${colorClass} border-2 rounded px-1 cursor-pointer hover:opacity-80 ${
            isSelected ? "ring-2 ring-indigo-500" : ""
          }`}
          onClick={() => setSelectedEntity(isSelected ? null : entity)}
          title={`${entity.label} (${entity.source}) - Confidence: ${
            entity.confidence || "N/A"
          }`}
        >
          {entity.text}
        </span>
      );

      lastEnd = entity.end_char;
    });

    // Add remaining text
    if (lastEnd < text.length) {
      elements.push(text.slice(lastEnd));
    }

    return (
      <div
        className="whitespace-pre-wrap p-4 bg-gray-50 rounded border min-h-64 cursor-text"
        onMouseUp={() => {
          const selection = window.getSelection();
          if (selection && selection.toString().trim()) {
            const range = selection.getRangeAt(0);
            const textNode = range.commonAncestorContainer;
            const fullText = textNode.textContent || "";
            const start = range.startOffset + text.indexOf(fullText);
            const end = range.endOffset + text.indexOf(fullText);

            setSelectedText(selection.toString());
            setSelectedRange({ start, end });
          }
        }}
      >
        {elements}
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          🔬 Scientific Text Annotator
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          Use AI models to annotate scientific text with custom tag definitions
        </p>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left Panel - Files and Settings */}
        <div className="lg:col-span-1">
          {/* File Upload */}
          <div className="bg-white shadow rounded-lg mb-6">
            <div className="px-4 py-3 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                📄 Upload Files
              </h3>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tags CSV File
                </label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleTagsFileUpload}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                />
                {tags.length > 0 && (
                  <p className="mt-1 text-sm text-green-600">
                    ✅ {tags.length} tags loaded
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Text File (.txt)
                </label>
                <input
                  type="file"
                  accept=".txt"
                  onChange={handleTextFileUpload}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                />
              </div>
            </div>
          </div>

          {/* Settings Panel */}
          <div className="bg-white shadow rounded-lg mb-6">
            <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">🔧 Settings</h3>
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-1 text-gray-400 hover:text-gray-600"
              >
                <AdjustmentsHorizontalIcon className="h-5 w-5" />
              </button>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  AI Model
                </label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="gpt-4o-mini">GPT-4O Mini</option>
                  <option value="gpt-4o">GPT-4O</option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="claude-3-5-haiku-20241022">
                    Claude 3.5 Haiku
                  </option>
                  <option value="claude-3-5-sonnet-20241022">
                    Claude 3.5 Sonnet
                  </option>
                </select>
              </div>

              {showSettings && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Temperature: {temperature}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.05"
                      value={temperature}
                      onChange={(e) =>
                        setTemperature(parseFloat(e.target.value))
                      }
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Consistent</span>
                      <span>Creative</span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Chunk Size: {chunkSize} chars
                    </label>
                    <input
                      type="range"
                      min="200"
                      max="4000"
                      step="100"
                      value={chunkSize}
                      onChange={(e) => setChunkSize(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Max Tokens: {maxTokens}
                    </label>
                    <input
                      type="range"
                      min={tokenRecommendations.min_tokens}
                      max={tokenRecommendations.max_tokens_limit}
                      step="50"
                      value={maxTokens}
                      onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                      className="w-full"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Recommended: {tokenRecommendations.default_tokens}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Overlap: {overlap} chars
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="200"
                      step="10"
                      value={overlap}
                      onChange={(e) => setOverlap(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Cost Calculator */}
          <CostCalculator
            text={text}
            model={selectedModel}
            chunkSize={chunkSize}
            maxTokens={maxTokens}
            tags={tags}
          />
        </div>

        {/* Main Panel */}
        <div className="lg:col-span-3">
          {/* Text Input */}
          <div className="bg-white shadow rounded-lg mb-6">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Text Input</h3>
            </div>
            <div className="p-6">
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                rows={8}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Enter or paste your scientific text here..."
              />
              <div className="mt-4 flex justify-between items-center">
                <div className="text-sm text-gray-500">
                  {text.length} characters • Estimated{" "}
                  {Math.ceil(text.length / 4)} tokens
                </div>
                <button
                  onClick={handleAnnotate}
                  disabled={isAnnotating || !text.trim() || tags.length === 0}
                  className={`flex items-center px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                    isAnnotating || !text.trim() || tags.length === 0
                      ? "bg-gray-400 cursor-not-allowed"
                      : "bg-primary-600 hover:bg-primary-700"
                  }`}
                >
                  {isAnnotating ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Annotating...
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-4 w-4 mr-2" />
                      🔍 Run Annotation
                    </>
                  )}
                </button>
              </div>

              {!text.trim() && (
                <div className="mt-2 text-sm text-red-600">❌ Text missing</div>
              )}
              {tags.length === 0 && (
                <div className="mt-2 text-sm text-red-600">
                  ❌ Tag CSV missing
                </div>
              )}
            </div>
          </div>

          {/* Processing Summary */}
          {annotationResult && (
            <div className="bg-white shadow rounded-lg mb-6">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">
                  📊 Processing Summary
                </h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary-600">
                      {annotationResult.statistics.total_entities}
                    </div>
                    <div className="text-sm text-gray-500">Entities Found</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {annotationResult.statistics.chunks_processed}
                    </div>
                    <div className="text-sm text-gray-500">
                      Chunks Processed
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {annotationResult.statistics.total_tokens.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-500">Total Tokens</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {entities.filter((e) => e.source === "llm").length} +{" "}
                      {manualEntities.length}
                    </div>
                    <div className="text-sm text-gray-500">LLM + Manual</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Annotated Text Preview */}
          <div className="bg-white shadow rounded-lg mb-6">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">
                🔍 Annotated Text Preview
              </h3>
              {combinedEntities.length > 0 && (
                <div className="text-sm text-gray-500">
                  {combinedEntities.length} annotations ({entities.length} LLM +{" "}
                  {manualEntities.length} Manual)
                </div>
              )}
            </div>
            <div className="p-6">
              {renderHighlightedText()}

              {/* Legend */}
              {combinedEntities.length > 0 && (
                <div className="mt-4 flex items-center space-x-6 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-blue-200 border-2 border-blue-400 rounded"></div>
                    <span>LLM Annotations</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-yellow-200 border-2 border-yellow-400 rounded"></div>
                    <span>Manual Annotations</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Manual Annotation Interface */}
          {selectedText && selectedRange && (
            <div className="bg-white shadow rounded-lg mb-6">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">
                  ✏️ Add Manual Annotation
                </h3>
              </div>
              <div className="p-6">
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Selected Text
                  </label>
                  <div className="p-3 bg-gray-50 border rounded-lg">
                    "{selectedText}"
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  {tags.map((tag) => (
                    <button
                      key={tag.tag_name}
                      onClick={() => handleAddManualAnnotation(tag.tag_name)}
                      className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm hover:bg-primary-200"
                    >
                      {tag.tag_name}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Entity List */}
          {combinedEntities.length > 0 && (
            <div className="bg-white shadow rounded-lg mb-6">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">
                  📝 Annotations List
                </h3>
              </div>
              <div className="p-6">
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {combinedEntities.map((entity, index) => (
                    <div
                      key={index}
                      className={`flex items-center justify-between p-3 border rounded-lg ${
                        entity.source === "manual"
                          ? "bg-yellow-50 border-yellow-200"
                          : "bg-blue-50 border-blue-200"
                      } ${
                        selectedEntity === entity
                          ? "ring-2 ring-indigo-500"
                          : ""
                      }`}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-gray-900">
                            "{entity.text}"
                          </span>
                          <span
                            className={`px-2 py-1 rounded text-xs font-medium ${
                              entity.source === "manual"
                                ? "bg-yellow-100 text-yellow-800"
                                : "bg-blue-100 text-blue-800"
                            }`}
                          >
                            {entity.label}
                          </span>
                          <span className="text-xs text-gray-500">
                            {entity.source} • [{entity.start_char}:
                            {entity.end_char}]
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() =>
                            setSelectedEntity(
                              selectedEntity === entity ? null : entity
                            )
                          }
                          className="p-1 text-gray-400 hover:text-gray-600"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleRemoveEntity(entity)}
                          className="p-1 text-red-400 hover:text-red-600"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Advanced Features Tabs */}
          {combinedEntities.length > 0 && (
            <div className="bg-white shadow rounded-lg">
              {/* Tab Navigation */}
              <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
                  <button
                    onClick={() => setActiveTab("validation")}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === "validation"
                        ? "border-primary-500 text-primary-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    <CheckCircleIcon className="h-5 w-5 inline mr-2" />
                    Validation
                  </button>
                  <button
                    onClick={() => setActiveTab("export")}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === "export"
                        ? "border-primary-500 text-primary-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    <ArrowDownTrayIcon className="h-5 w-5 inline mr-2" />
                    Export
                  </button>
                </nav>
              </div>

              {/* Tab Content */}
              <div className="p-6">
                {activeTab === "validation" && (
                  <ValidationComponent
                    text={text}
                    entities={combinedEntities}
                    onEntitiesUpdate={(updatedEntities) => {
                      // Split updated entities back into LLM and manual
                      const llmEntities = updatedEntities.filter(
                        (e) => e.source === "llm"
                      );
                      const manualEntitiesUpdated = updatedEntities.filter(
                        (e) => e.source === "manual"
                      );
                      setEntities(llmEntities);
                      setManualEntities(manualEntitiesUpdated);
                    }}
                  />
                )}

                {activeTab === "export" && (
                  <ExportComponent
                    text={text}
                    entities={combinedEntities}
                    annotationResult={annotationResult}
                  />
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnnotationPage;
