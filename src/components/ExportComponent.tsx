import React, { useState } from "react";
import {
  ArrowDownTrayIcon,
  DocumentTextIcon,
} from "@heroicons/react/24/outline";
import { API_CONFIG } from "../constants/api";

interface AnnotationEntity {
  start_char: number;
  end_char: number;
  text: string;
  label: string;
  source?: "llm" | "manual";
}

interface ExportProps {
  text: string;
  entities: AnnotationEntity[];
}

const ExportComponent: React.FC<ExportProps> = ({ text, entities }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState<
    "json" | "csv" | "conll" | "comprehensive"
  >("json");

  const handleExport = async () => {
    if (!entities.length) return;

    setIsExporting(true);
    try {
      const response = await fetch(
        `${API_CONFIG.API_BASE_URL}/annotations/export`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: JSON.stringify({
            text,
            annotations: entities,
            format_type: exportFormat,
            include_metadata: true,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Export failed");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      const fileExtensions = {
        json: "json",
        csv: "csv",
        conll: "conll",
        comprehensive: "json",
      };

      a.download = `annotations_${new Date().toISOString().split("T")[0]}.${
        fileExtensions[exportFormat]
      }`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Export error:", error);
      alert("Export failed. Please try again.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 flex items-center">
          <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
          Export Annotations
        </h3>
      </div>
      <div className="p-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Export Format
            </label>
            <select
              value={exportFormat}
              onChange={(e) =>
                setExportFormat(
                  e.target.value as "json" | "csv" | "conll" | "comprehensive"
                )
              }
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="json">JSON Format</option>
              <option value="csv">CSV Format</option>
              <option value="conll">CoNLL Format</option>
              <option value="comprehensive">Comprehensive JSON</option>
            </select>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Format Details:</h4>
            <div className="text-sm text-gray-600">
              {exportFormat === "json" && (
                <div>
                  <div className="flex items-center mb-1">
                    <DocumentTextIcon className="h-4 w-4 mr-1" />
                    Basic JSON with entities and positions
                  </div>
                  <div>• Lightweight format for integration</div>
                </div>
              )}
              {exportFormat === "csv" && (
                <div>
                  <div className="flex items-center mb-1">
                    <DocumentTextIcon className="h-4 w-4 mr-1" />
                    Tabular format for spreadsheet analysis
                  </div>
                  <div>
                    • Columns: text, label, start_char, end_char, source
                  </div>
                </div>
              )}
              {exportFormat === "conll" && (
                <div>
                  <div className="flex items-center mb-1">
                    <DocumentTextIcon className="h-4 w-4 mr-1" />
                    Standard NLP format for training/evaluation
                  </div>
                  <div>• Token-based format with BIO tagging</div>
                </div>
              )}
              {exportFormat === "comprehensive" && (
                <div>
                  <div className="flex items-center mb-1">
                    <DocumentTextIcon className="h-4 w-4 mr-1" />
                    Complete export with metadata and statistics
                  </div>
                  <div>
                    • Includes processing details, token counts, and evaluation
                    results
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              {entities.length} entities ready for export
            </div>
            <button
              onClick={handleExport}
              disabled={isExporting || !entities.length}
              className={`flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                isExporting || !entities.length
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-green-600 hover:bg-green-700"
              }`}
            >
              {isExporting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Exporting...
                </>
              ) : (
                <>
                  <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                  Download {exportFormat.toUpperCase()}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExportComponent;
