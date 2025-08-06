import React, { useState, useEffect } from "react";
import {
  FolderIcon,
  PlusIcon,
  EllipsisHorizontalIcon,
} from "@heroicons/react/24/outline";
import { API_CONFIG } from "../constants/api";
import toast from "react-hot-toast";

interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at?: string;
  annotation_count?: number;
}

const ProjectsPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProject, setNewProject] = useState({
    name: "",
    description: "",
  });
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await fetch(`${API_CONFIG.API_BASE_URL}/projects`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProjects(data);
      } else if (response.status === 401) {
        toast.error("Please log in to view your projects");
      }
    } catch (error) {
      console.error("Failed to load projects:", error);
      toast.error("Failed to load projects");
    } finally {
      setIsLoading(false);
    }
  };

  const createProject = async () => {
    if (!newProject.name.trim()) {
      toast.error("Project name is required");
      return;
    }

    setIsCreating(true);
    try {
      const response = await fetch(`${API_CONFIG.API_BASE_URL}/projects`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(newProject),
      });

      if (response.ok) {
        const createdProject = await response.json();
        setProjects([createdProject, ...projects]);
        setNewProject({ name: "", description: "" });
        setShowCreateModal(false);
        toast.success("Project created successfully!");
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to create project");
      }
    } catch (error) {
      console.error("Failed to create project:", error);
      toast.error("Failed to create project");
    } finally {
      setIsCreating(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="mt-1 text-sm text-gray-500">
            Organize your annotation work into projects.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg flex items-center"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          New Project
        </button>
      </div>

      {projects.length === 0 ? (
        <div className="text-center py-12">
          <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No projects
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating a new project.
          </p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
              New Project
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div
              key={project.id}
              className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <FolderIcon className="h-8 w-8 text-primary-600" />
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">
                    {project.annotation_count || 0} annotations
                  </span>
                  <button className="text-gray-400 hover:text-gray-600">
                    <EllipsisHorizontalIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {project.name}
              </h3>
              {project.description && (
                <p className="text-sm text-gray-500 mb-4 line-clamp-2">
                  {project.description}
                </p>
              )}
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">
                  Updated {formatDate(project.updated_at || project.created_at)}
                </span>
                <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                  Open
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Create New Project
              </h3>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Project Name *
                </label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={(e) =>
                    setNewProject({ ...newProject, name: e.target.value })
                  }
                  placeholder="Enter project name"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  value={newProject.description}
                  onChange={(e) =>
                    setNewProject({
                      ...newProject,
                      description: e.target.value,
                    })
                  }
                  placeholder="Describe your project..."
                  rows={3}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setNewProject({ name: "", description: "" });
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={createProject}
                  disabled={isCreating || !newProject.name.trim()}
                  className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50 rounded-lg"
                >
                  {isCreating ? "Creating..." : "Create Project"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectsPage;
