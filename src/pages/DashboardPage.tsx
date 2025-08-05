import React from "react";
import {
  ChartBarIcon,
  DocumentTextIcon,
  TagIcon,
  FolderIcon,
  ClockIcon,
  CurrencyDollarIcon,
} from "@heroicons/react/24/outline";

const DashboardPage: React.FC = () => {
  const stats = [
    {
      name: "Total Annotations",
      value: "127",
      icon: DocumentTextIcon,
      change: "+12%",
      changeType: "increase",
    },
    {
      name: "Active Projects",
      value: "8",
      icon: FolderIcon,
      change: "+2",
      changeType: "increase",
    },
    {
      name: "Tag Sets",
      value: "15",
      icon: TagIcon,
      change: "+3",
      changeType: "increase",
    },
    {
      name: "Cost This Month",
      value: "$24.50",
      icon: CurrencyDollarIcon,
      change: "+5.4%",
      changeType: "increase",
    },
  ];

  const recentActivity = [
    {
      id: 1,
      type: "annotation",
      description: 'Annotated "Protein Expression Analysis"',
      time: "2 hours ago",
    },
    {
      id: 2,
      type: "project",
      description: 'Created new project "Gene Discovery"',
      time: "5 hours ago",
    },
    {
      id: 3,
      type: "tagset",
      description: 'Updated "Biomedical NER" tag set',
      time: "1 day ago",
    },
    {
      id: 4,
      type: "file",
      description: 'Uploaded "research_paper.txt"',
      time: "2 days ago",
    },
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome back! Here's what's happening with your annotations.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {stats.map((item) => (
          <div
            key={item.name}
            className="bg-white overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <item.icon
                    className="h-6 w-6 text-gray-400"
                    aria-hidden="true"
                  />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {item.name}
                    </dt>
                    <dd>
                      <div className="text-lg font-medium text-gray-900">
                        {item.value}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 px-5 py-3">
              <div className="text-sm">
                <span
                  className={`font-medium ${
                    item.changeType === "increase"
                      ? "text-green-600"
                      : "text-red-600"
                  }`}
                >
                  {item.change}
                </span>
                <span className="text-gray-500"> from last month</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Activity */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Recent Activity
            </h3>
          </div>
          <div className="divide-y divide-gray-200">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="px-6 py-4">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <ClockIcon className="h-5 w-5 text-gray-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">
                      {activity.description}
                    </p>
                    <p className="text-sm text-gray-500">{activity.time}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="px-6 py-3 bg-gray-50">
            <a
              href="/app/activity"
              className="text-sm font-medium text-primary-600 hover:text-primary-500"
            >
              View all activity →
            </a>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <a
                href="/app/annotate"
                className="w-full bg-primary-600 hover:bg-primary-700 text-white flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium"
              >
                <DocumentTextIcon className="h-5 w-5 mr-2" />
                Start New Annotation
              </a>
              <a
                href="/app/files"
                className="w-full bg-white hover:bg-gray-50 text-gray-900 flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium"
              >
                <ChartBarIcon className="h-5 w-5 mr-2" />
                Upload File
              </a>
              <a
                href="/app/tags"
                className="w-full bg-white hover:bg-gray-50 text-gray-900 flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium"
              >
                <TagIcon className="h-5 w-5 mr-2" />
                Manage Tags
              </a>
              <a
                href="/app/projects"
                className="w-full bg-white hover:bg-gray-50 text-gray-900 flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium"
              >
                <FolderIcon className="h-5 w-5 mr-2" />
                Create Project
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Usage Chart Placeholder */}
      <div className="mt-8">
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Usage Overview
            </h3>
          </div>
          <div className="p-6">
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">
                  Chart visualization will be implemented here
                </p>
                <p className="text-sm text-gray-400">
                  Showing annotation trends and costs over time
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
