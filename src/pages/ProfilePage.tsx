import React, { useState, useEffect } from "react";
import { useAuth } from "../hooks/useAuth";
import {
  EyeIcon,
  EyeSlashIcon,
  KeyIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import { API_ENDPOINTS } from "../constants/api";
import { get, put } from "../utils/api";

interface ApiKeySettings {
  openai_api_key?: string;
  anthropic_api_key?: string;
}

const ProfilePage: React.FC = () => {
  const { user, updateProfile } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [organization, setOrganization] = useState("");
  const [apiKeys, setApiKeys] = useState<ApiKeySettings>({});
  const [showOpenAIKey, setShowOpenAIKey] = useState(false);
  const [showClaudeKey, setShowClaudeKey] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [isSavingApiKeys, setIsSavingApiKeys] = useState(false);

  // Load existing API keys on component mount
  useEffect(() => {
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    try {
      const data = await get<ApiKeySettings>(API_ENDPOINTS.USERS.API_KEYS);
      setApiKeys(data);
    } catch (error) {
      console.error("Failed to load API keys:", error);
    }
  };

  const handleSaveProfile = async () => {
    setIsSavingProfile(true);
    try {
      await updateProfile({ full_name: fullName });
      toast.success("Profile updated successfully!");
    } catch (error) {
      toast.error("Failed to update profile");
    } finally {
      setIsSavingProfile(false);
    }
  };

  const handleSaveApiKeys = async () => {
    setIsSavingApiKeys(true);
    try {
      await put(API_ENDPOINTS.USERS.UPDATE_API_KEYS, apiKeys);
      toast.success("API keys saved successfully!");
    } catch (error) {
      toast.error("Failed to save API keys");
    } finally {
      setIsSavingApiKeys(false);
    }
  };

  const validateApiKey = (
    key: string,
    type: "openai" | "anthropic"
  ): boolean => {
    if (!key) return false;

    if (type === "openai") {
      return key.startsWith("sk-") && key.length > 20;
    } else if (type === "anthropic") {
      return key.startsWith("sk-ant-") && key.length > 20;
    }

    return false;
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your account settings and API configurations.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Profile Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Profile Information */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                Profile Information
              </h3>
            </div>
            <div className="p-6">
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={user?.email || ""}
                    disabled
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-gray-50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Organization
                  </label>
                  <input
                    type="text"
                    value={organization}
                    onChange={(e) => setOrganization(e.target.value)}
                    placeholder="Your organization or institution"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <button
                    onClick={handleSaveProfile}
                    disabled={isSavingProfile}
                    className="bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg flex items-center"
                  >
                    {isSavingProfile ? "Saving..." : "Save Changes"}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* API Keys Configuration */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <KeyIcon className="h-5 w-5 mr-2" />
                API Keys Configuration
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                Configure your AI model API keys to enable annotation features
              </p>
            </div>
            <div className="p-6 space-y-6">
              {/* OpenAI API Key */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  OpenAI API Key
                </label>
                <div className="relative">
                  <input
                    type={showOpenAIKey ? "text" : "password"}
                    value={apiKeys.openai_api_key || ""}
                    onChange={(e) =>
                      setApiKeys((prev) => ({
                        ...prev,
                        openai_api_key: e.target.value,
                      }))
                    }
                    placeholder="sk-..."
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 pr-12 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowOpenAIKey(!showOpenAIKey)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    {showOpenAIKey ? (
                      <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <EyeIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
                <div className="flex items-center mt-1">
                  {apiKeys.openai_api_key &&
                  validateApiKey(apiKeys.openai_api_key, "openai") ? (
                    <div className="flex items-center text-green-600 text-sm">
                      <CheckCircleIcon className="h-4 w-4 mr-1" />
                      Valid API key format
                    </div>
                  ) : apiKeys.openai_api_key ? (
                    <div className="flex items-center text-red-600 text-sm">
                      <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                      Invalid API key format
                    </div>
                  ) : null}
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Get your API key from{" "}
                  <a
                    href="https://platform.openai.com/api-keys"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700"
                  >
                    OpenAI Platform
                  </a>
                </p>
              </div>

              {/* Claude API Key */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Anthropic Claude API Key
                </label>
                <div className="relative">
                  <input
                    type={showClaudeKey ? "text" : "password"}
                    value={apiKeys.anthropic_api_key || ""}
                    onChange={(e) =>
                      setApiKeys((prev) => ({
                        ...prev,
                        anthropic_api_key: e.target.value,
                      }))
                    }
                    placeholder="sk-ant-..."
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 pr-12 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowClaudeKey(!showClaudeKey)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    {showClaudeKey ? (
                      <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <EyeIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
                <div className="flex items-center mt-1">
                  {apiKeys.anthropic_api_key &&
                  validateApiKey(apiKeys.anthropic_api_key, "anthropic") ? (
                    <div className="flex items-center text-green-600 text-sm">
                      <CheckCircleIcon className="h-4 w-4 mr-1" />
                      Valid API key format
                    </div>
                  ) : apiKeys.anthropic_api_key ? (
                    <div className="flex items-center text-red-600 text-sm">
                      <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                      Invalid API key format
                    </div>
                  ) : null}
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Get your API key from{" "}
                  <a
                    href="https://console.anthropic.com/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700"
                  >
                    Anthropic Console
                  </a>
                </p>
              </div>

              <div className="border-t pt-4">
                <button
                  onClick={handleSaveApiKeys}
                  disabled={isSavingApiKeys}
                  className="bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg flex items-center"
                >
                  {isSavingApiKeys ? "Saving..." : "Save API Keys"}
                </button>
                <p className="text-xs text-gray-500 mt-2">
                  Your API keys are encrypted and stored securely. They are only
                  used for your annotation requests.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Settings Sidebar */}
        <div>
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Settings</h3>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">
                  Email notifications
                </span>
                <input type="checkbox" defaultChecked className="rounded" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Cost alerts</span>
                <input type="checkbox" defaultChecked className="rounded" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Monthly reports</span>
                <input type="checkbox" className="rounded" />
              </div>
            </div>
          </div>

          <div className="mt-6 bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Usage Stats</h3>
            </div>
            <div className="p-6">
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Annotations</span>
                  <span className="text-sm font-medium">127</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Cost</span>
                  <span className="text-sm font-medium">$24.50</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Tokens Used</span>
                  <span className="text-sm font-medium">45,230</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
