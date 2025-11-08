import { useEffect, useState } from "react";
import { Book, ExternalLink, Loader2, AlertCircle, RefreshCw } from "lucide-react";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { senalignAPI } from "../services/api";

interface Resource {
  title: string;
  url: string;
  summary: string;
  type: string;
  relevance_score?: number;
  category?: string;
}

interface ResourcesSidebarProps {
  datasetId: string;
  initialResources?: Resource[];
  resourcesStatus?: "pending" | "loading" | "complete" | "error";
}

const getResourceIcon = (type: string) => {
  switch (type) {
    case "paper":
      return <Book className="w-4 h-4" />;
    case "kaggle":
      return <ExternalLink className="w-4 h-4" />;
    case "blog":
      return <Book className="w-4 h-4" />;
    case "github":
      return <ExternalLink className="w-4 h-4" />;
    default:
      return <ExternalLink className="w-4 h-4" />;
  }
};

export function ResourcesSidebar({
  datasetId,
  initialResources = [],
  resourcesStatus = "pending",
}: ResourcesSidebarProps) {
  const [resources, setResources] = useState<Resource[]>(initialResources);
  const [status, setStatus] = useState<string>(resourcesStatus);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // If resources are pending or empty, fetch them
    if ((status === "pending" || resources.length === 0) && !isLoading) {
      fetchResources();
    }
  }, [datasetId]);

  const fetchResources = async () => {
    setIsLoading(true);
    setStatus("loading");
    setError(null);

    try {
      const response = await senalignAPI.fetchResources(datasetId);
      setResources(response.resources || []);
      setStatus(response.status || "complete");
      setIsLoading(false);
    } catch (err: any) {
      console.error("Failed to fetch resources:", err);
      setError(err.message || "Failed to load resources");
      setStatus("error");
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    fetchResources();
  };

  return (
    <div className="w-full lg:w-80 flex-shrink-0">
      <div className="sticky top-24">
        <Card className="rounded-2xl shadow-sm bg-white border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-amber-50 to-orange-50">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <Book className="w-5 h-5 text-amber-600" />
                <h3 className="font-semibold text-gray-900">Helpful Resources</h3>
              </div>
              {resources.length > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {resources.length}
                </Badge>
              )}
            </div>
            <p className="text-xs text-gray-600">
              Curated articles, papers, and tools
            </p>
          </div>

          {/* Content */}
          <div className="max-h-[calc(100vh-12rem)] overflow-y-auto">
            {/* Loading State */}
            {isLoading && (
              <div className="p-6 text-center">
                <Loader2 className="w-8 h-8 text-amber-500 animate-spin mx-auto mb-3" />
                <p className="text-sm text-gray-600 mb-1">
                  Finding relevant resources...
                </p>
                <p className="text-xs text-gray-500">
                  This may take a few moments
                </p>
              </div>
            )}

            {/* Error State */}
            {status === "error" && !isLoading && (
              <div className="p-6 text-center">
                <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-3" />
                <p className="text-sm text-gray-700 mb-2">
                  Unable to load resources
                </p>
                {error && (
                  <p className="text-xs text-gray-500 mb-3">{error}</p>
                )}
                <button
                  onClick={handleRetry}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-900 text-white text-xs rounded-2xl hover:bg-gray-800 transition-colors mx-auto"
                >
                  <RefreshCw className="w-3 h-3" />
                  Try Again
                </button>
              </div>
            )}

            {/* Empty State */}
            {status === "complete" && resources.length === 0 && !isLoading && (
              <div className="p-6 text-center">
                <Book className="w-8 h-8 text-gray-400 mx-auto mb-3" />
                <p className="text-sm text-gray-600 mb-1">No resources found</p>
                <p className="text-xs text-gray-500">
                  Try adjusting your problem description
                </p>
              </div>
            )}

            {/* Resources List */}
            {resources.length > 0 && (
              <div className="divide-y divide-gray-100">
                {resources.map((resource, idx) => (
                  <a
                    key={idx}
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block p-4 hover:bg-amber-50/50 transition-colors group"
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center group-hover:bg-amber-100 transition-colors">
                        {getResourceIcon(resource.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <h4 className="text-sm font-medium text-gray-900 group-hover:text-amber-900 line-clamp-2">
                            {resource.title}
                          </h4>
                          <ExternalLink className="w-3 h-3 text-gray-400 flex-shrink-0 mt-1" />
                        </div>
                        <p className="text-xs text-gray-600 line-clamp-2 mb-2">
                          {resource.summary}
                        </p>
                        <div className="flex items-center gap-2 flex-wrap">
                          <Badge
                            variant="outline"
                            className="text-xs bg-white"
                          >
                            {resource.type}
                          </Badge>
                          {resource.relevance_score && (
                            <span className="text-xs text-gray-500">
                              {Math.round(resource.relevance_score * 100)}% match
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </a>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          {resources.length > 0 && (
            <div className="p-3 border-t border-gray-200 bg-gray-50">
              <p className="text-xs text-center text-gray-500">
                Resources curated by AI • Click to open
              </p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
