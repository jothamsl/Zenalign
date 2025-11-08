import { useState, useEffect } from "react";
import {
  Database,
  BarChart3,
  Shield,
  Brain,
  Book,
  CheckCircle2,
} from "lucide-react";

interface LoadingOverlayProps {
  isUploading?: boolean;
  isAnalyzing?: boolean;
}

const analysisSteps = [
  {
    id: "upload",
    icon: Database,
    title: "Uploading Dataset",
    description: "Securely transferring your data...",
  },
  {
    id: "profiling",
    icon: BarChart3,
    title: "Profiling Data",
    description: "Analyzing quality metrics and patterns...",
  },
  {
    id: "pii",
    icon: Shield,
    title: "Scanning for PII",
    description: "Detecting sensitive information...",
  },
  {
    id: "ai",
    icon: Brain,
    title: "Generating AI Insights",
    description: "Creating personalized recommendations...",
  },
  {
    id: "resources",
    icon: Book,
    title: "Finding Resources",
    description: "Searching for helpful materials...",
  },
];

export function LoadingOverlay({
  isUploading,
  isAnalyzing,
}: LoadingOverlayProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [showOverlay, setShowOverlay] = useState(false);

  useEffect(() => {
    if (!isUploading && !isAnalyzing) {
      // Delay hiding to prevent flash
      const timeout = setTimeout(() => {
        setShowOverlay(false);
        setCurrentStep(0);
        setCompletedSteps([]);
      }, 300);
      return () => clearTimeout(timeout);
    }

    // Show overlay after small delay to prevent flash for quick operations
    const showTimeout = setTimeout(() => {
      setShowOverlay(true);
    }, 200);

    if (isUploading) {
      setCurrentStep(0);
      setCompletedSteps([]);
    }

    if (isAnalyzing) {
      // Start from profiling step
      setCurrentStep(1);
      setCompletedSteps([0]); // Upload is complete

      // Simulate progress through steps
      const interval = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev < analysisSteps.length - 1) {
            setCompletedSteps((completed) => [...completed, prev]);
            return prev + 1;
          }
          return prev;
        });
      }, 6000); // 6 seconds per step

      return () => {
        clearInterval(interval);
        clearTimeout(showTimeout);
      };
    }

    return () => clearTimeout(showTimeout);
  }, [isUploading, isAnalyzing]);

  if (!showOverlay) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-300">
      <div className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full p-8 animate-in zoom-in-95 fade-in duration-500">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl mb-4">
            <Database className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            {isUploading ? "Uploading Dataset" : "Analyzing Your Dataset"}
          </h2>
          <p className="text-sm text-gray-600">
            {isUploading
              ? "Please wait while we securely upload your data..."
              : "Running comprehensive quality checks and generating insights..."}
          </p>
        </div>

        {/* Progress Steps */}
        <div className="space-y-4 mb-8">
          {analysisSteps.map((step, index) => {
            const StepIcon = step.icon;
            const isCompleted = completedSteps.includes(index);
            const isCurrent = currentStep === index;
            const isPending = index > currentStep;

            return (
              <div
                key={step.id}
                className={`flex items-start gap-4 p-4 rounded-2xl transition-all duration-500 transform ${
                  isCompleted
                    ? "bg-emerald-50 border-2 border-emerald-200 scale-[0.98]"
                    : isCurrent
                      ? "bg-amber-50 border-2 border-amber-300 scale-100"
                      : "bg-gray-50 border-2 border-gray-200 opacity-60"
                }`}
                style={{
                  transitionDelay: `${index * 50}ms`,
                }}
              >
                <div
                  className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-500 ${
                    isCompleted
                      ? "bg-emerald-500"
                      : isCurrent
                        ? "bg-amber-500"
                        : "bg-gray-300"
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="w-5 h-5 text-white" />
                  ) : (
                    <StepIcon
                      className={`w-5 h-5 ${isCurrent ? "text-white animate-pulse" : "text-white"}`}
                    />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <h3
                    className={`font-semibold text-sm mb-1 ${
                      isCompleted
                        ? "text-emerald-900"
                        : isCurrent
                          ? "text-amber-900"
                          : "text-gray-500"
                    }`}
                  >
                    {step.title}
                  </h3>
                  <p
                    className={`text-xs ${
                      isCompleted
                        ? "text-emerald-700"
                        : isCurrent
                          ? "text-amber-700"
                          : "text-gray-400"
                    }`}
                  >
                    {isCompleted
                      ? "Complete"
                      : isCurrent
                        ? step.description
                        : "Pending"}
                  </p>
                </div>

                {isCurrent && (
                  <div className="flex-shrink-0">
                    <div className="w-5 h-5 border-2 border-amber-600 border-t-transparent rounded-full animate-spin"></div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <span>
              {isUploading
                ? "Uploading..."
                : `Step ${currentStep + 1} of ${analysisSteps.length}`}
            </span>
            <span>
              {Math.round((completedSteps.length / analysisSteps.length) * 100)}
              %
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-amber-500 to-orange-500 transition-all duration-500 ease-out"
              style={{
                width: `${(completedSteps.length / analysisSteps.length) * 100}%`,
              }}
            />
          </div>
        </div>

        {/* Estimated Time */}
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            {isUploading
              ? "Upload usually completes in a few seconds..."
              : "Analysis usually takes 20-30 seconds"}
          </p>
        </div>
      </div>
    </div>
  );
}
