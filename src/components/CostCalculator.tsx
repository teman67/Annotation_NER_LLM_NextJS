import React, { useState, useEffect, useCallback } from "react";
import {
  CurrencyDollarIcon,
  CalculatorIcon,
} from "@heroicons/react/24/outline";
import { API_CONFIG } from "../constants/api";

interface AnnotationTag {
  tag_name: string;
  definition: string;
  examples: string;
}

interface CostEstimate {
  model: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  input_cost: number;
  output_cost: number;
  total_cost: number;
}

interface CostCalculatorProps {
  text: string;
  model: string;
  chunkSize: number;
  maxTokens: number;
  tags: AnnotationTag[];
}

const CostCalculator: React.FC<CostCalculatorProps> = ({
  text,
  model,
  chunkSize,
  maxTokens,
  tags,
}) => {
  const [costEstimate, setCostEstimate] = useState<CostEstimate | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  const calculateCost = useCallback(async () => {
    if (!text.trim() || tags.length === 0) {
      setCostEstimate(null);
      return;
    }

    setIsCalculating(true);
    try {
      const response = await fetch(
        `${API_CONFIG.API_BASE_URL}/annotations/estimate-cost`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: JSON.stringify({
            text,
            model,
            chunk_size: chunkSize,
            max_tokens: maxTokens,
            tag_definitions: tags,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Cost estimation failed");
      }

      const result: CostEstimate = await response.json();
      setCostEstimate(result);
    } catch (error) {
      console.error("Cost estimation error:", error);
      setCostEstimate(null);
    } finally {
      setIsCalculating(false);
    }
  }, [text, model, chunkSize, maxTokens, tags]);

  useEffect(() => {
    if (text && tags.length > 0) {
      calculateCost();
    }
  }, [text, model, chunkSize, maxTokens, tags, calculateCost]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 4,
      maximumFractionDigits: 6,
    }).format(amount);
  };

  if (!text || tags.length === 0) {
    return (
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <CurrencyDollarIcon className="h-5 w-5 mr-2" />
            Cost Estimation
          </h3>
        </div>
        <div className="p-4 text-center text-gray-500">
          <CalculatorIcon className="h-12 w-12 mx-auto mb-2 text-gray-400" />
          <div>Add text and tags to see cost estimation</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 flex items-center">
          <CurrencyDollarIcon className="h-5 w-5 mr-2" />
          Cost Estimation
        </h3>
      </div>
      <div className="p-4">
        {isCalculating ? (
          <div className="flex items-center justify-center py-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mr-2"></div>
            <span className="text-gray-600">Calculating...</span>
          </div>
        ) : costEstimate ? (
          <div className="space-y-4">
            {/* Model Info */}
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-gray-700">Model:</span>
              <span className="text-gray-900">{costEstimate.model}</span>
            </div>

            {/* Token Breakdown */}
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-lg font-semibold text-blue-600">
                  {costEstimate.input_tokens.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500">Input Tokens</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-green-600">
                  {costEstimate.output_tokens.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500">Output Tokens</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-purple-600">
                  {costEstimate.total_tokens.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500">Total Tokens</div>
              </div>
            </div>

            {/* Cost Breakdown */}
            <div className="bg-gray-50 rounded-lg p-3 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Input Cost:</span>
                <span className="text-gray-900">
                  {formatCurrency(costEstimate.input_cost)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Output Cost:</span>
                <span className="text-gray-900">
                  {formatCurrency(costEstimate.output_cost)}
                </span>
              </div>
              <div className="border-t border-gray-200 pt-2">
                <div className="flex justify-between font-medium">
                  <span className="text-gray-900">Total Estimated Cost:</span>
                  <span className="text-primary-600 text-lg">
                    {formatCurrency(costEstimate.total_cost)}
                  </span>
                </div>
              </div>
            </div>

            {/* Additional Info */}
            <div className="text-xs text-gray-500 space-y-1">
              <div>• Estimation based on current text length and settings</div>
              <div>
                • Actual costs may vary slightly due to processing variations
              </div>
              <div>• Includes chunking overhead and tag definition tokens</div>
              {costEstimate.total_cost > 0.01 && (
                <div className="text-amber-600 font-medium">
                  ⚠️ High cost estimated - consider using a smaller model or
                  reducing text length
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center text-red-500 py-4">
            <div>Failed to calculate cost estimation</div>
            <button
              onClick={calculateCost}
              className="mt-2 text-sm text-primary-600 hover:text-primary-700"
            >
              Try again
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CostCalculator;
