import React, { useState, useMemo } from "react";
import {
  PencilIcon,
  TrashIcon,
  CheckIcon,
  XMarkIcon,
  TagIcon,
} from "@heroicons/react/24/outline";
import type { Entity } from "../types";

interface AnnotationTableProps {
  entities: Entity[];
  onUpdateEntity: (index: number, updatedEntity: Entity) => void;
  onDeleteEntity: (index: number) => void;
  availableTags: string[];
  text: string;
}

interface EditingState {
  index: number;
  entity: Entity;
}

const AnnotationTable: React.FC<AnnotationTableProps> = ({
  entities,
  onUpdateEntity,
  onDeleteEntity,
  availableTags,
  text,
}) => {
  const [editingState, setEditingState] = useState<EditingState | null>(null);
  const [selectedEntities, setSelectedEntities] = useState<number[]>([]);

  // Sort entities by start position
  const sortedEntities = useMemo(() => {
    return entities
      .map((entity, index) => ({ ...entity, originalIndex: index }))
      .sort((a, b) => a.start_char - b.start_char);
  }, [entities]);

  const handleEdit = (index: number, entity: Entity) => {
    setEditingState({ index, entity: { ...entity } });
  };

  const handleSaveEdit = () => {
    if (editingState) {
      // Validate the edited entity
      const { start_char, end_char, label } = editingState.entity;

      if (
        start_char >= 0 &&
        end_char > start_char &&
        end_char <= text.length &&
        label.trim()
      ) {
        const actualText = text.slice(start_char, end_char);
        const updatedEntity = {
          ...editingState.entity,
          text: actualText,
        };

        onUpdateEntity(editingState.index, updatedEntity);
        setEditingState(null);
      }
    }
  };

  const handleCancelEdit = () => {
    setEditingState(null);
  };

  const handleDelete = (index: number) => {
    onDeleteEntity(index);
    setSelectedEntities((prev) => prev.filter((i) => i !== index));
  };

  const handleSelectEntity = (index: number) => {
    setSelectedEntities((prev) => {
      if (prev.includes(index)) {
        return prev.filter((i) => i !== index);
      } else {
        return [...prev, index];
      }
    });
  };

  const handleDeleteSelected = () => {
    // Sort in descending order to delete from the end first
    const sortedIndices = [...selectedEntities].sort((a, b) => b - a);
    sortedIndices.forEach((index) => {
      onDeleteEntity(index);
    });
    setSelectedEntities([]);
  };

  const getSourceBadgeColor = (source: string) => {
    switch (source) {
      case "llm":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "manual":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <TagIcon className="h-5 w-5 text-gray-500" />
            <h3 className="text-lg font-medium text-gray-900">
              Annotations ({sortedEntities.length})
            </h3>
          </div>
          {selectedEntities.length > 0 && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">
                {selectedEntities.length} selected
              </span>
              <button
                onClick={handleDeleteSelected}
                className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
              >
                Delete Selected
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Table */}
      {sortedEntities.length === 0 ? (
        <div className="px-6 py-8 text-center text-gray-500">
          No annotations found. Run annotation first to see results.
        </div>
      ) : (
        <div className="overflow-hidden">
          <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
            <table className="min-w-full divide-y divide-gray-200 table-fixed">
              <thead className="bg-gray-50">
                <tr>
                  <th className="w-8 px-3 py-3 text-center">
                    <input
                      type="checkbox"
                      checked={
                        selectedEntities.length === sortedEntities.length &&
                        sortedEntities.length > 0
                      }
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedEntities(sortedEntities.map((_, i) => i));
                        } else {
                          setSelectedEntities([]);
                        }
                      }}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                  </th>
                  <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-1/5">
                    Text
                  </th>
                  <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-1/5">
                    Label
                  </th>
                  <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-1/5">
                    Position
                  </th>
                  <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-1/5">
                    Source
                  </th>
                  <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-1/5">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sortedEntities.map((entity) => {
                  const isEditing =
                    editingState?.index === entity.originalIndex;
                  const isSelected = selectedEntities.includes(
                    entity.originalIndex
                  );

                  return (
                    <tr
                      key={`${entity.originalIndex}-${entity.start_char}-${entity.end_char}`}
                      className={`hover:bg-gray-50 ${
                        isSelected ? "bg-blue-50" : ""
                      }`}
                    >
                      {/* Checkbox */}
                      <td className="px-3 py-4 text-center">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() =>
                            handleSelectEntity(entity.originalIndex)
                          }
                          className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                        />
                      </td>

                      {/* Text */}
                      <td className="px-3 py-4 text-center">
                        <div className="flex justify-center">
                          <div className="text-sm text-gray-900">
                            <span
                              className="inline-block bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 px-3 py-1.5 rounded-lg font-medium text-blue-900 shadow-sm cursor-help transition-all duration-200 hover:shadow-md hover:from-blue-100 hover:to-indigo-100"
                              title={
                                entity.text.length > 30
                                  ? entity.text
                                  : undefined
                              }
                            >
                              "
                              {entity.text.length > 30
                                ? `${entity.text.substring(0, 30)}...`
                                : entity.text}
                              "
                            </span>
                          </div>
                        </div>
                        {entity.text.length > 30 && (
                          <div className="mt-1 text-xs text-gray-400 italic text-center">
                            Hover to see full text
                          </div>
                        )}
                      </td>

                      {/* Label */}
                      <td className="px-3 py-4 text-center">
                        {isEditing ? (
                          <select
                            value={editingState.entity.label}
                            onChange={(e) =>
                              setEditingState((prev) =>
                                prev
                                  ? {
                                      ...prev,
                                      entity: {
                                        ...prev.entity,
                                        label: e.target.value,
                                      },
                                    }
                                  : null
                              )
                            }
                            className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm text-center"
                          >
                            {availableTags.length > 0 ? (
                              availableTags.map((tag) => (
                                <option key={tag} value={tag}>
                                  {tag}
                                </option>
                              ))
                            ) : (
                              <option value={entity.label}>
                                {entity.label}
                              </option>
                            )}
                          </select>
                        ) : (
                          <div className="flex justify-center">
                            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 border border-indigo-200">
                              {entity.label}
                            </span>
                          </div>
                        )}
                      </td>

                      {/* Position */}
                      <td className="px-3 py-4 text-center">
                        {isEditing ? (
                          <div className="flex space-x-1 justify-center">
                            <input
                              type="number"
                              value={editingState.entity.start_char}
                              onChange={(e) =>
                                setEditingState((prev) =>
                                  prev
                                    ? {
                                        ...prev,
                                        entity: {
                                          ...prev.entity,
                                          start_char:
                                            parseInt(e.target.value) || 0,
                                        },
                                      }
                                    : null
                                )
                              }
                              className="w-10 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-xs text-center"
                              placeholder="Start"
                            />
                            <span className="text-xs text-gray-400 self-center">
                              -
                            </span>
                            <input
                              type="number"
                              value={editingState.entity.end_char}
                              onChange={(e) =>
                                setEditingState((prev) =>
                                  prev
                                    ? {
                                        ...prev,
                                        entity: {
                                          ...prev.entity,
                                          end_char:
                                            parseInt(e.target.value) || 0,
                                        },
                                      }
                                    : null
                                )
                              }
                              className="w-10 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-xs text-center"
                              placeholder="End"
                            />
                          </div>
                        ) : (
                          <div className="text-xs text-gray-500 font-mono text-center">
                            {entity.start_char}-{entity.end_char}
                          </div>
                        )}
                      </td>

                      {/* Source */}
                      <td className="px-3 py-4 text-center">
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getSourceBadgeColor(
                            entity.source || "llm"
                          )}`}
                        >
                          {entity.source === "manual" ? "Manual" : "LLM"}
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="px-3 py-4 text-center">
                        {isEditing ? (
                          <div className="flex space-x-1 justify-center">
                            <button
                              onClick={handleSaveEdit}
                              className="text-green-600 hover:text-green-800 p-1 rounded hover:bg-green-50"
                              title="Save changes"
                            >
                              <CheckIcon className="h-4 w-4" />
                            </button>
                            <button
                              onClick={handleCancelEdit}
                              className="text-gray-600 hover:text-gray-800 p-1 rounded hover:bg-gray-50"
                              title="Cancel editing"
                            >
                              <XMarkIcon className="h-4 w-4" />
                            </button>
                          </div>
                        ) : (
                          <div className="flex space-x-1 justify-center">
                            <button
                              onClick={() =>
                                handleEdit(entity.originalIndex, entity)
                              }
                              className="text-indigo-600 hover:text-indigo-800 p-1 rounded hover:bg-indigo-50"
                              title="Edit annotation"
                            >
                              <PencilIcon className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(entity.originalIndex)}
                              className="text-red-600 hover:text-red-800 p-1 rounded hover:bg-red-50"
                              title="Delete annotation"
                            >
                              <TrashIcon className="h-4 w-4" />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnnotationTable;
