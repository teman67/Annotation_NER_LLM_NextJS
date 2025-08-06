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
  total_entities: number;
  correct_entities: number;
  errors: Array<{
    entity_index: number;
    error: string;
    start_char: number;
    end_char: number;
    expected_text: string;
    actual_text?: string;
    label: string;
  }>;
  warnings: Array<unknown>;
  timestamp: string;
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

  console.log("ValidationComponent rendered with:", {
    textLength: text.length,
    entitiesCount: entities.length,
    hasValidationResult: !!validationResult,
  });

  console.log("Rendering ValidationComponent - return statement reached");

  const handleValidate = async () => {
    if (!entities.length) return;

    setIsValidating(true);
    console.log("Starting validation with:", {
      text: text.substring(0, 100),
      entities: entities.length,
    });

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

      console.log("Validation response status:", response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Validation error response:", errorData);
        throw new Error(errorData.detail || "Validation failed");
      }

      const result: ValidationResult = await response.json();
      console.log("Validation result:", result);
      setValidationResult(result);
    } catch (error) {
      console.error("Validation error:", error);
      alert(
        `Validation failed: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
    } finally {
      setIsValidating(false);
    }
  };

  const handleFix = async () => {
    if (!entities.length) return;

    console.log("Starting fix with entities:", entities.length);
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

      console.log("Fix response status:", response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Fix error response:", errorData);
        throw new Error(errorData.detail || "Fix failed");
      }

      const result = await response.json();
      console.log("Fix result:", result);

      // Update validation result if we got new validation data
      if (result.fixed_annotations) {
        console.log(
          "Updating entities with fixed annotations:",
          result.fixed_annotations.length
        );
        onEntitiesUpdate(result.fixed_annotations);
      }

      // Show detailed fix results
      const stats = result.fix_statistics;
      if (stats) {
        const message =
          `Fix completed!\n\n` +
          `📊 Results:\n` +
          `• Total annotations: ${stats.total}\n` +
          `• Already correct: ${stats.already_correct}\n` +
          `• Fixed: ${stats.fixed}\n` +
          `• Unfixable: ${stats.unfixable}\n` +
          `• Multiple matches: ${stats.multiple_matches || 0}\n` +
          `• Strategy used: ${stats.strategy_used}`;

        alert(message);
      } else {
        alert(
          `Fix completed! Updated ${
            result.fixed_annotations?.length || 0
          } annotations.`
        );
      }
    } catch (error) {
      console.error("Fix error:", error);
      alert(
        `Fix failed: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
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
                  validationResult.errors.length === 0
                    ? "bg-green-50 border border-green-200"
                    : "bg-red-50 border border-red-200"
                }`}
              >
                <div className="flex items-center">
                  {validationResult.errors.length === 0 ? (
                    <CheckCircleIcon className="h-5 w-5 text-green-600 mr-2" />
                  ) : (
                    <ExclamationTriangleIcon className="h-5 w-5 text-red-600 mr-2" />
                  )}
                  <div>
                    <h4
                      className={`font-medium ${
                        validationResult.errors.length === 0
                          ? "text-green-800"
                          : "text-red-800"
                      }`}
                    >
                      {validationResult.errors.length === 0
                        ? "All annotations are valid!"
                        : "Issues found in annotations"}
                    </h4>
                    <div
                      className={`text-sm mt-1 ${
                        validationResult.errors.length === 0
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      {validationResult.correct_entities} valid out of{" "}
                      {validationResult.total_entities} entities
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
                              Entity #{error.entity_index + 1}: {error.label}
                            </div>
                            <div className="text-sm text-yellow-700 mt-1">
                              {error.error}
                            </div>
                            <div className="text-sm text-gray-500 mt-1">
                              Expected: "{error.expected_text}"
                              {error.actual_text &&
                                ` | Got: "${error.actual_text}"`}{" "}
                              (chars {error.start_char}-{error.end_char})
                            </div>
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
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  <div className="text-center">
                    <div className="text-lg font-semibold text-blue-600">
                      {validationResult.total_entities}
                    </div>
                    <div className="text-gray-500">Total</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-green-600">
                      {validationResult.correct_entities}
                    </div>
                    <div className="text-gray-500">Valid</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-red-600">
                      {validationResult.errors.length}
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
