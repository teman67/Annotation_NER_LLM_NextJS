import React, { useState } from "react";
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  WrenchScrewdriverIcon,
} from "@heroicons/react/24/outline";
import { API_CONFIG } from "../constants/api";

interface AnnotationEntity {
  start_char: number;
  end_char: number;
  text: string;
  label: string;
  confidence?: number;
  source?: "llm" | "manual";
}

interface ValidationResult {
  is_valid: boolean;
  errors: Array<{
    entity_index: number;
    error_type: string;
    message: string;
    suggestion?: string;
  }>;
  fixed_entities?: AnnotationEntity[];
  statistics: {
    total_entities: number;
    valid_entities: number;
    fixed_entities: number;
    errors_found: number;
  };
}

interface ValidationProps {
  text: string;
  entities: AnnotationEntity[];
  onEntitiesUpdate: (entities: AnnotationEntity[]) => void;
}

const ValidationComponent: React.FC<ValidationProps> = ({
  text,
  entities,
  onEntitiesUpdate,
}) => {
  const [isValidating, setIsValidating] = useState(false);
  const [isFixing, setIsFixing] = useState(false);
  const [validationResult, setValidationResult] =
    useState<ValidationResult | null>(null);

  const handleValidate = async () => {
    if (!entities.length) return;

    setIsValidating(true);
    try {
      const response = await fetch(
        `${API_CONFIG.API_BASE_URL}/annotations/validate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: JSON.stringify({
            text,
            annotations: entities,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Validation failed");
      }

      const result: ValidationResult = await response.json();
      setValidationResult(result);
    } catch (error) {
      console.error("Validation error:", error);
      alert("Validation failed. Please try again.");
    } finally {
      setIsValidating(false);
    }
  };

  const handleFix = async () => {
    if (!entities.length) return;

    setIsFixing(true);
    try {
      const response = await fetch(
        `${API_CONFIG.API_BASE_URL}/annotations/fix`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: JSON.stringify({
            text,
            annotations: entities,
            strategy: "fuzzy_match",
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Fix failed");
      }

      const result: ValidationResult = await response.json();
      if (result.fixed_entities) {
        onEntitiesUpdate(result.fixed_entities);
        setValidationResult(result);
      }
    } catch (error) {
      console.error("Fix error:", error);
      alert("Fix failed. Please try again.");
    } finally {
      setIsFixing(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 flex items-center">
          <CheckCircleIcon className="h-5 w-5 mr-2" />
          Validation & Quality Control
        </h3>
      </div>
      <div className="p-6">
        <div className="space-y-4">
          {/* Action Buttons */}
          <div className="flex space-x-3">
            <button
              onClick={handleValidate}
              disabled={isValidating || !entities.length}
              className={`flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                isValidating || !entities.length
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {isValidating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Validating...
                </>
              ) : (
                <>
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Validate Annotations
                </>
              )}
            </button>

            <button
              onClick={handleFix}
              disabled={isFixing || !entities.length}
              className={`flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                isFixing || !entities.length
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-orange-600 hover:bg-orange-700"
              }`}
            >
              {isFixing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Fixing...
                </>
              ) : (
                <>
                  <WrenchScrewdriverIcon className="h-4 w-4 mr-2" />
                  Auto-Fix Issues
                </>
              )}
            </button>
          </div>

          {/* Validation Results */}
          {validationResult && (
            <div className="space-y-4">
              {/* Summary */}
              <div
                className={`rounded-lg p-4 ${
                  validationResult.is_valid
                    ? "bg-green-50 border border-green-200"
                    : "bg-red-50 border border-red-200"
                }`}
              >
                <div className="flex items-center">
                  {validationResult.is_valid ? (
                    <CheckCircleIcon className="h-5 w-5 text-green-600 mr-2" />
                  ) : (
                    <ExclamationTriangleIcon className="h-5 w-5 text-red-600 mr-2" />
                  )}
                  <div>
                    <h4
                      className={`font-medium ${
                        validationResult.is_valid
                          ? "text-green-800"
                          : "text-red-800"
                      }`}
                    >
                      {validationResult.is_valid
                        ? "All annotations are valid!"
                        : "Issues found in annotations"}
                    </h4>
                    <div
                      className={`text-sm mt-1 ${
                        validationResult.is_valid
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      {validationResult.statistics.valid_entities} valid out of{" "}
                      {validationResult.statistics.total_entities} entities
                      {validationResult.statistics.fixed_entities > 0 && (
                        <span>
                          {" "}
                          • {validationResult.statistics.fixed_entities}{" "}
                          entities were automatically fixed
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Error Details */}
              {validationResult.errors &&
                validationResult.errors.length > 0 && (
                  <div className="space-y-2">
                    <h5 className="font-medium text-gray-900">Issues Found:</h5>
                    {validationResult.errors.map((error, index) => (
                      <div
                        key={index}
                        className="bg-yellow-50 border border-yellow-200 rounded-lg p-3"
                      >
                        <div className="flex items-start">
                          <ExclamationTriangleIcon className="h-4 w-4 text-yellow-600 mr-2 mt-0.5 flex-shrink-0" />
                          <div className="flex-1">
                            <div className="text-sm font-medium text-yellow-800">
                              Entity #{error.entity_index + 1}:{" "}
                              {error.error_type}
                            </div>
                            <div className="text-sm text-yellow-700 mt-1">
                              {error.message}
                            </div>
                            {error.suggestion && (
                              <div className="text-sm text-yellow-600 mt-1 italic">
                                💡 {error.suggestion}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

              {/* Statistics */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h5 className="font-medium text-gray-900 mb-2">
                  Validation Statistics:
                </h5>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div className="text-center">
                    <div className="text-lg font-semibold text-blue-600">
                      {validationResult.statistics.total_entities}
                    </div>
                    <div className="text-gray-500">Total</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-green-600">
                      {validationResult.statistics.valid_entities}
                    </div>
                    <div className="text-gray-500">Valid</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-orange-600">
                      {validationResult.statistics.fixed_entities}
                    </div>
                    <div className="text-gray-500">Fixed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-red-600">
                      {validationResult.statistics.errors_found}
                    </div>
                    <div className="text-gray-500">Errors</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {!entities.length && (
            <div className="text-center py-8 text-gray-500">
              <CheckCircleIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <div className="text-lg font-medium">
                No annotations to validate
              </div>
              <div className="text-sm">
                Add some annotations first to use validation features
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ValidationComponent;
