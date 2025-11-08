import { useState } from "react";
import {
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Download,
  AlertCircle,
  FileText,
  Shield,
  Book,
  ExternalLink,
  BarChart3,
  Database,
  AlertTriangle,
  Users,
  XCircle,
  Target,
  Share2,
} from "lucide-react";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { AnalysisReport } from "../services/api";

interface AnalysisResultsProps {
  onBack?: () => void;
  report?: AnalysisReport;
}

const getScoreColor = (score: number) => {
  const scorePercent = score * 100;
  if (scorePercent >= 80) return "text-emerald-600";
  if (scorePercent >= 60) return "text-amber-600";
  return "text-orange-600";
};

const getScoreBgColor = (score: number) => {
  const scorePercent = score * 100;
  if (scorePercent >= 80) return "bg-emerald-50 border-emerald-200";
  if (scorePercent >= 60) return "bg-amber-50 border-amber-200";
  return "bg-orange-50 border-orange-200";
};

const getProgressBarColor = (score: number) => {
  const scorePercent = score * 100;
  if (scorePercent >= 80) return "bg-emerald-500";
  if (scorePercent >= 60) return "bg-amber-500";
  return "bg-orange-500";
};

const getSeverityBadge = (severity: string) => {
  switch (severity?.toLowerCase()) {
    case "critical":
      return "destructive";
    case "high":
      return "destructive";
    case "medium":
      return "secondary";
    default:
      return "default";
  }
};

const getResourceIcon = (type: string) => {
  switch (type) {
    case "paper":
      return <Book className="w-4 h-4" />;
    case "kaggle":
      return <BarChart3 className="w-4 h-4" />;
    case "blog":
      return <FileText className="w-4 h-4" />;
    case "github":
      return <ExternalLink className="w-4 h-4" />;
    default:
      return <ExternalLink className="w-4 h-4" />;
  }
};

const ProgressBar = ({ value }: { value: number }) => {
  return (
    <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
      <div
        className={`h-full transition-all duration-300 ${getProgressBarColor(value)}`}
        style={{ width: `${value * 100}%` }}
      />
    </div>
  );
};

export function AnalysisResults({ onBack, report }: AnalysisResultsProps) {
  const [expandedSections, setExpandedSections] = useState<string[]>([
    "summary",
    "completeness",
  ]);

  const toggleSection = (section: string) => {
    setExpandedSections((prev) =>
      prev.includes(section)
        ? prev.filter((s) => s !== section)
        : [...prev, section],
    );
  };

  if (!report) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-amber-50 via-orange-50 to-amber-100">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No analysis report available</p>
          {onBack && (
            <button
              onClick={onBack}
              className="mt-4 px-4 py-2 bg-black text-white rounded-2xl hover:bg-gray-800"
            >
              Go Back
            </button>
          )}
        </div>
      </div>
    );
  }

  const hasPII = report.pii_report?.summary?.columns_with_pii > 0;
  const overallScore = Math.round((report.quality_scores?.overall || 0) * 100);
  const fileName = "Uploaded Dataset";

  // Count critical and warning issues
  const criticalIssues =
    report.recommendations?.filter((r) => r.severity === "critical").length ||
    0;
  const warningIssues =
    report.recommendations?.filter(
      (r) => r.severity === "high" || r.severity === "medium",
    ).length || 0;

  const downloadReport = () => {
    const dataStr = JSON.stringify(report, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `senalign_report_${report.dataset_id}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-orange-50 to-amber-100">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Database className="w-5 h-5 text-gray-600" />
              <div>
                <h1 className="text-gray-900">{fileName}</h1>
                <p className="text-xs text-gray-500">
                  {report.problem_description}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button className="px-4 py-2 text-sm text-gray-700 hover:bg-white/80 rounded-2xl transition-colors flex items-center gap-2 bg-white/60 border border-gray-200">
                <Share2 className="w-4 h-4" />
                Share
              </button>
              <button
                onClick={downloadReport}
                className="px-4 py-2 text-sm bg-black text-white hover:bg-gray-800 rounded-2xl transition-colors flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export Report
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Overall Score Card */}
        <Card
          className={`p-8 mb-6 border-2 rounded-3xl shadow-sm ${getScoreBgColor(overallScore / 100)}`}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-gray-900">Dataset Quality Score</h2>
                <Badge
                  variant={
                    overallScore >= 80
                      ? "default"
                      : overallScore >= 60
                        ? "secondary"
                        : "destructive"
                  }
                >
                  {overallScore >= 80
                    ? "Ready for Production"
                    : overallScore >= 60
                      ? "Needs Attention"
                      : "Critical Issues"}
                </Badge>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                Your dataset shows{" "}
                {overallScore >= 80
                  ? "excellent"
                  : overallScore >= 60
                    ? "moderate"
                    : "poor"}{" "}
                readiness for machine learning.
                {criticalIssues > 0 && (
                  <>
                    {" "}
                    There are <strong>
                      {criticalIssues} critical issues
                    </strong>{" "}
                    that must be addressed before training
                  </>
                )}
                {warningIssues > 0 && (
                  <>
                    {criticalIssues > 0 ? ", and " : " There are "}
                    <strong>{warningIssues} additional warnings</strong> that
                    could impact model performance
                  </>
                )}
                .
              </p>
              <div className="flex items-center gap-4">
                <div>
                  <p className="text-xs text-gray-500 mb-1">
                    {report.shape?.rows?.toLocaleString() || 0} rows ×{" "}
                    {report.shape?.columns || 0} columns
                  </p>
                  <p className="text-xs text-gray-500">
                    Target: {report.problem_type?.replace("_", " ")}
                  </p>
                </div>
              </div>
            </div>
            <div className="flex flex-col items-center">
              <div className={`text-6xl ${getScoreColor(overallScore / 100)}`}>
                {overallScore}
              </div>
              <p className="text-sm text-gray-500">/ 100</p>
            </div>
          </div>
        </Card>

        {/* Metrics Grid */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {Object.entries(report.quality_scores || {})
            .filter(([key]) => key !== "overall")
            .slice(0, 4)
            .map(([key, value]) => {
              const scorePercent = Math.round(value * 100);
              return (
                <Card
                  key={key}
                  className="p-5 rounded-2xl shadow-sm bg-white border-gray-200"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm text-gray-600 capitalize">
                      {key.replace("_", " ")}
                    </h3>
                    {scorePercent >= 80 ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    ) : scorePercent >= 60 ? (
                      <AlertTriangle className="w-4 h-4 text-amber-600" />
                    ) : (
                      <XCircle className="w-4 h-4 text-orange-600" />
                    )}
                  </div>
                  <div className={`text-2xl mb-1 ${getScoreColor(value)}`}>
                    {scorePercent}
                  </div>
                  <ProgressBar value={value} />
                  <p className="text-xs text-gray-500 mt-2">Analyzed</p>
                </Card>
              );
            })}
        </div>

        {/* Privacy Alert */}
        {hasPII && (
          <Card className="mb-4 rounded-2xl shadow-sm bg-red-50 border-red-200">
            <div className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="w-5 h-5 text-red-600" />
                <h3 className="text-lg font-semibold text-red-900">
                  Privacy Alert: PII Detected
                </h3>
              </div>
              <p className="text-sm text-red-700 mb-3">
                Found {report.pii_report.summary.columns_with_pii} columns with
                personally identifiable information.
                {report.pii_report.summary.total_pii_values &&
                  ` Total PII values: ${report.pii_report.summary.total_pii_values}`}
              </p>
              {report.pii_report.details && (
                <div className="bg-white rounded-2xl p-3">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Detected PII Types:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(report.pii_report.details)
                      .filter(([_, data]: [string, any]) => data.found)
                      .map(([piiType]) => (
                        <Badge
                          key={piiType}
                          className="bg-red-100 text-red-800"
                        >
                          {piiType.replace("_", " ").toUpperCase()}
                        </Badge>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Executive Summary */}
        {report.overall_assessment && (
          <Card className="mb-4 rounded-2xl shadow-sm bg-white border-gray-200">
            <button
              onClick={() => toggleSection("summary")}
              className="w-full px-6 py-4 flex items-center justify-between hover:bg-amber-50/50 transition-colors rounded-2xl"
            >
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-gray-600" />
                <h2 className="text-gray-900">Executive Summary</h2>
              </div>
              {expandedSections.includes("summary") ? (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronRight className="w-5 h-5 text-gray-400" />
              )}
            </button>
            {expandedSections.includes("summary") && (
              <div className="px-6 pb-6 space-y-4 border-t border-gray-100">
                <div className="pt-4">
                  <p className="text-sm text-gray-700 leading-relaxed mb-4">
                    {report.overall_assessment}
                  </p>
                  {report.priority_actions &&
                    report.priority_actions.length > 0 && (
                      <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4">
                        <h3 className="text-sm text-amber-900 mb-2">
                          ✅ Recommended Next Steps
                        </h3>
                        <ol className="text-sm text-amber-900/80 space-y-1 list-decimal list-inside">
                          {report.priority_actions.map((action, idx) => (
                            <li key={idx}>{action}</li>
                          ))}
                        </ol>
                      </div>
                    )}
                </div>
              </div>
            )}
          </Card>
        )}

        {/* Issues/Recommendations List */}
        {report.recommendations && report.recommendations.length > 0 && (
          <div className="space-y-4">
            {report.recommendations.map((rec, index) => (
              <Card
                key={index}
                className={`overflow-hidden rounded-2xl shadow-sm bg-white ${
                  rec.severity === "critical"
                    ? "border-l-4 border-l-orange-500"
                    : rec.severity === "high"
                      ? "border-l-4 border-l-amber-500"
                      : "border-l-4 border-l-gray-400"
                }`}
              >
                <button
                  onClick={() => toggleSection(`issue-${index}`)}
                  className="w-full px-6 py-4 flex items-center justify-between hover:bg-amber-50/30 transition-colors"
                >
                  <div className="flex items-center gap-3 flex-1">
                    {rec.severity === "critical" && (
                      <XCircle className="w-5 h-5 text-orange-600 flex-shrink-0" />
                    )}
                    {(rec.severity === "high" || rec.severity === "medium") && (
                      <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />
                    )}
                    {rec.severity === "low" && (
                      <AlertCircle className="w-5 h-5 text-gray-600 flex-shrink-0" />
                    )}
                    <div className="text-left flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-gray-900">{rec.category}</h3>
                        <Badge variant={getSeverityBadge(rec.severity)}>
                          {rec.severity.toUpperCase()}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">{rec.suggestion}</p>
                    </div>
                  </div>
                  {expandedSections.includes(`issue-${index}`) ? (
                    <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  )}
                </button>

                {expandedSections.includes(`issue-${index}`) && (
                  <div className="px-6 pb-6 space-y-4 border-t border-gray-100 bg-amber-50/20">
                    {rec.code_example && (
                      <div className="pt-4">
                        <h4 className="text-sm text-gray-900 mb-2 flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                          Code Example
                        </h4>
                        <div className="bg-gray-900 text-gray-100 rounded-2xl p-4 text-xs font-mono overflow-x-auto">
                          <pre className="whitespace-pre-wrap">
                            {rec.code_example}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}

        {/* Completeness Analysis */}
        {report.missing_values?.columns &&
          report.missing_values.columns.length > 0 && (
            <Card className="mt-4 rounded-2xl shadow-sm bg-white border-gray-200">
              <button
                onClick={() => toggleSection("completeness")}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-amber-50/30 transition-colors rounded-2xl"
              >
                <div className="flex items-center gap-3">
                  <Database className="w-5 h-5 text-gray-600" />
                  <h2 className="text-gray-900">Completeness Analysis</h2>
                </div>
                {expandedSections.includes("completeness") ? (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                )}
              </button>
              {expandedSections.includes("completeness") && (
                <div className="px-6 pb-6 border-t border-gray-100">
                  <div className="pt-4 space-y-3">
                    {report.missing_values.columns.map((col) => {
                      const missingCount =
                        report.missing_values?.counts?.[col] || 0;
                      const missingPercent =
                        report.missing_values?.percentages?.[col] || 0;
                      return (
                        <div
                          key={col}
                          className="flex items-center justify-between py-2 border-b border-gray-100"
                        >
                          <div>
                            <p className="text-sm text-gray-900">{col}</p>
                            <p className="text-xs text-gray-500">
                              {missingPercent.toFixed(1)}% missing (
                              {missingCount.toLocaleString()} rows)
                            </p>
                          </div>
                          <Badge
                            variant={
                              missingPercent > 20 ? "destructive" : "secondary"
                            }
                          >
                            {missingPercent > 20 ? "High" : "Acceptable"}
                          </Badge>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </Card>
          )}

        {/* Distribution & Balance */}
        {report.class_imbalance?.columns &&
          report.class_imbalance.columns.length > 0 && (
            <Card className="mt-4 rounded-2xl shadow-sm bg-white border-gray-200">
              <button
                onClick={() => toggleSection("distribution")}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-amber-50/30 transition-colors rounded-2xl"
              >
                <div className="flex items-center gap-3">
                  <BarChart3 className="w-5 h-5 text-gray-600" />
                  <h2 className="text-gray-900">Distribution & Balance</h2>
                </div>
                {expandedSections.includes("distribution") ? (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                )}
              </button>
              {expandedSections.includes("distribution") && (
                <div className="px-6 pb-6 border-t border-gray-100">
                  <div className="pt-4 space-y-4">
                    {report.class_imbalance.columns.map((col) => {
                      const ratio =
                        report.class_imbalance?.imbalance_ratios?.[col] || 0;
                      const distribution =
                        report.class_imbalance?.distributions?.[col] || {};
                      return (
                        <div key={col}>
                          <div className="flex items-center justify-between mb-2">
                            <p className="text-sm text-gray-900">
                              Column: {col}
                            </p>
                            <Badge
                              variant={ratio > 3 ? "destructive" : "secondary"}
                            >
                              {ratio > 3 ? "Severe Imbalance" : "Imbalanced"}
                            </Badge>
                          </div>
                          <div className="space-y-1">
                            {Object.entries(distribution)
                              .slice(0, 5)
                              .map(([value, count]) => {
                                const total = Object.values(
                                  distribution,
                                ).reduce((a: any, b: any) => a + b, 0);
                                const percent = ((count / total) * 100).toFixed(
                                  1,
                                );
                                return (
                                  <div
                                    key={value}
                                    className="flex items-center gap-2"
                                  >
                                    <div className="w-24 text-xs text-gray-600 truncate">
                                      {value}
                                    </div>
                                    <div className="flex-1 bg-gray-200 h-6 rounded-lg relative">
                                      <div
                                        className="bg-amber-500 h-6 rounded-lg"
                                        style={{ width: `${percent}%` }}
                                      ></div>
                                      <span className="absolute inset-0 flex items-center justify-center text-xs">
                                        {percent}%
                                      </span>
                                    </div>
                                  </div>
                                );
                              })}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </Card>
          )}

        {/* Domain Resources */}
        {report.domain_resources && report.domain_resources.length > 0 && (
          <Card className="mt-4 rounded-2xl shadow-sm bg-white border-gray-200">
            <button
              onClick={() => toggleSection("resources")}
              className="w-full px-6 py-4 flex items-center justify-between hover:bg-amber-50/30 transition-colors rounded-2xl"
            >
              <div className="flex items-center gap-3">
                <Book className="w-5 h-5 text-gray-600" />
                <h2 className="text-gray-900">
                  Helpful Resources ({report.domain_resources.length})
                </h2>
              </div>
              {expandedSections.includes("resources") ? (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronRight className="w-5 h-5 text-gray-400" />
              )}
            </button>
            {expandedSections.includes("resources") && (
              <div className="px-6 pb-6 border-t border-gray-100">
                <div className="pt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                  {report.domain_resources.map((resource, idx) => (
                    <div
                      key={idx}
                      className="border border-gray-200 rounded-2xl p-4 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getResourceIcon(resource.type)}
                          <span className="text-xs text-gray-500">
                            {resource.type.toUpperCase()}
                          </span>
                        </div>
                        {resource.relevance_score && (
                          <span className="text-xs text-gray-500">
                            {Math.round(resource.relevance_score * 100)}%
                            relevant
                          </span>
                        )}
                      </div>
                      <h4 className="font-medium text-sm mb-2">
                        <a
                          href={resource.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800"
                        >
                          {resource.title}
                        </a>
                      </h4>
                      <p className="text-xs text-gray-600">
                        {resource.summary}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        )}
      </div>
    </div>
  );
}
