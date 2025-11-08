import { Paperclip, ArrowUp, Upload, X, FileSpreadsheet } from "lucide-react";
import { useState, useRef, useEffect } from "react";

const datasetPrompts = [
  "Ready to validate your dataset?",
  "What dataset challenges can I help you solve?",
  "Let's audit your data quality",
  "Need help checking your dataset health?",
  "What ML problem are you working on?",
  "Is your data ready for modeling?",
  "Let's examine your dataset together",
  "What data quality concerns do you have?",
];

const placeholderExamples = [
  "I have a customer dataset with 50,000 rows and want to predict churn probability based on usage patterns, subscription tier, and support interactions",
  "I'm working with transaction data from the last 2 years and need to detect fraudulent credit card transactions using purchase history and behavioral signals",
  "I need to forecast monthly sales demand across 12 product categories using historical sales, seasonality, and marketing spend data",
  "I have 200,000 labeled medical images and want to build a multi-class classifier to detect early signs of diabetic retinopathy",
  "I'm analyzing sensor data from 500 manufacturing machines to predict equipment failures 48 hours in advance and reduce downtime",
  "I have user clickstream and purchase history from 100,000 customers and want to build a recommendation system for personalized product suggestions",
];

const popularDatasets = [
  {
    name: "MIMIC-III Clinical Database",
    description: "ICU patient records & vital signs",
    source: "PhysioNet",
    logo: "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtZWRpY2FsJTIwaGVhbHRoY2FyZXxlbnwxfHx8fDE3NjI1NjQzNzZ8MA&ixlib=rb-4.1.0&q=80&w=1080",
  },
  {
    name: "Credit Card Fraud Detection",
    description: "284k anonymized transactions",
    source: "Kaggle",
    logo: "https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjcmVkaXQlMjBjYXJkJTIwZmluYW5jZXxlbnwxfHx8fDE3NjI1NjQzNzZ8MA&ixlib=rb-4.1.0&q=80&w=1080",
  },
  {
    name: "NYC Taxi Trip Records",
    description: "1B+ trips with fare & location",
    source: "NYC Open Data",
    logo: "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxuZXclMjB5b3JrJTIwdGF4aXxlbnwxfHx8fDE3NjI1NjQzNzZ8MA&ixlib=rb-4.1.0&q=80&w=1080",
  },
  {
    name: "NIH Chest X-Ray Dataset",
    description: "112k labeled radiographic images",
    source: "NIH Clinical Center",
    logo: "https://images.unsplash.com/photo-1530026405186-ed1f139313f8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx4cmF5JTIwbWVkaWNhbHxlbnwxfHx8fDE3NjI1NjQzNzZ8MA&ixlib=rb-4.1.0&q=80&w=1080",
  },
  {
    name: "Lending Club Loan Data",
    description: "2.2M loans with default outcomes",
    source: "Lending Club",
    logo: "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsb2FuJTIwZmluYW5jZXxlbnwxfHx8fDE3NjI1NjQzNzZ8MA&ixlib=rb-4.1.0&q=80&w=1080",
  },
  {
    name: "Amazon Product Reviews",
    description: "130M+ reviews across categories",
    source: "Stanford SNAP",
    logo: "https://images.unsplash.com/photo-1523474253046-8cd2748b5fd2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhbWF6b24lMjBzaG9wcGluZ3xlbnwxfHx8fDE3NjI1NjQzNzZ8MA&ixlib=rb-4.1.0&q=80&w=1080",
  },
  {
    name: "US Flight Delays Dataset",
    description: "5.8M domestic flights with delays",
    source: "Bureau of Transportation",
    logo: "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhaXJwbGFuZSUyMGZsaWdodHxlbnwxfHx8fDE3NjI1NjQzNzZ8MA&ixlib=rb-4.1.0&q=80&w=1080",
  },
  {
    name: "UK Biobank Health Data",
    description: "500k participants with genomics",
    source: "UK Biobank",
    logo: "https://images.unsplash.com/photo-1582719471384-894fbb16e074?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxkbmElMjBnZW5vbWljc3xlbnwxfHx8fDE3NjI1NjQzNzZ8MA&ixlib=rb-4.1.0&q=80&w=1080",
  },
];

import { senalignAPI, AnalysisReport } from "../services/api";

interface ChatInputProps {
  onAnalyzeComplete?: (report: AnalysisReport) => void;
}

export function ChatInput({ onAnalyzeComplete }: ChatInputProps) {
  const [input, setInput] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isFileDraggedOnPage, setIsFileDraggedOnPage] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [, setDatasetId] = useState<string | null>(null);
  const [selectedPrompt] = useState(
    () => datasetPrompts[Math.floor(Math.random() * datasetPrompts.length)],
  );
  const [currentPlaceholder, setCurrentPlaceholder] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const maxFiles = 1; // Changed to 1 for simplicity

  useEffect(() => {
    const interval = setInterval(() => {
      setIsAnimating(true);

      setTimeout(() => {
        setCurrentPlaceholder(
          (prev) => (prev + 1) % placeholderExamples.length,
        );
        setIsAnimating(false);
      }, 500); // Half of the transition duration for crossfade effect
    }, 7000); // Change placeholder every 7 seconds

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    let dragCounter = 0;

    const handleWindowDragEnter = (e: DragEvent) => {
      e.preventDefault();
      dragCounter++;
      if (e.dataTransfer?.types.includes("Files")) {
        setIsFileDraggedOnPage(true);
      }
    };

    const handleWindowDragLeave = (e: DragEvent) => {
      e.preventDefault();
      dragCounter--;
      if (dragCounter === 0) {
        setIsFileDraggedOnPage(false);
      }
    };

    const handleWindowDrop = (e: DragEvent) => {
      e.preventDefault();
      dragCounter = 0;
      setIsFileDraggedOnPage(false);
    };

    const handleWindowDragOver = (e: DragEvent) => {
      e.preventDefault();
    };

    window.addEventListener("dragenter", handleWindowDragEnter);
    window.addEventListener("dragleave", handleWindowDragLeave);
    window.addEventListener("drop", handleWindowDrop);
    window.addEventListener("dragover", handleWindowDragOver);

    return () => {
      window.removeEventListener("dragenter", handleWindowDragEnter);
      window.removeEventListener("dragleave", handleWindowDragLeave);
      window.removeEventListener("drop", handleWindowDrop);
      window.removeEventListener("dragover", handleWindowDragOver);
    };
  }, []);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    setIsFileDraggedOnPage(false);

    const files = Array.from(e.dataTransfer.files).filter(
      (file) =>
        file.name.endsWith(".csv") ||
        file.name.endsWith(".xls") ||
        file.name.endsWith(".xlsx"),
    );

    const remainingSlots = maxFiles - uploadedFiles.length;
    const filesToAdd = files.slice(0, remainingSlots);

    if (filesToAdd.length > 0) {
      setUploadedFiles((prev) => [...prev, ...filesToAdd]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      const remainingSlots = maxFiles - uploadedFiles.length;
      const filesToAdd = files.slice(0, remainingSlots);

      if (filesToAdd.length > 0) {
        setUploadedFiles((prev) => [...prev, ...filesToAdd]);
      }
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
    setDatasetId(null);
    setError("");
  };

  const handleSubmit = async () => {
    if (uploadedFiles.length === 0) {
      setError("Please upload a dataset file first");
      return;
    }

    if (!input.trim()) {
      setError("Please describe your ML problem");
      return;
    }

    try {
      // Step 1: Upload dataset
      setIsUploading(true);
      setError("");

      const uploadResponse = await senalignAPI.uploadDataset(
        uploadedFiles[0],
        input,
      );

      setDatasetId(uploadResponse.dataset_id);
      setIsUploading(false);

      // Step 2: Analyze dataset
      setIsAnalyzing(true);

      const analysisReport = await senalignAPI.analyzeDataset(
        uploadResponse.dataset_id,
      );

      setIsAnalyzing(false);

      // Step 3: Navigate to results with report data
      if (onAnalyzeComplete) {
        onAnalyzeComplete(analysisReport);
      }
    } catch (err: any) {
      setIsUploading(false);
      setIsAnalyzing(false);
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to analyze dataset. Please try again.",
      );
    }
  };

  return (
    <>
      <div className="w-full max-w-2xl">
        <h1 className="text-center text-3xl mb-8 font-[Inter] text-[36px] font-normal">
          {selectedPrompt}
        </h1>

        <div className="bg-white rounded-3xl shadow-sm border border-gray-200 p-4 mb-6 relative">
          {/* Uploaded Files List - Above Input */}
          {uploadedFiles.length > 0 && (
            <div className="mb-3 flex flex-wrap gap-2">
              {uploadedFiles.map((file, index) => (
                <div
                  key={index}
                  className="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-gray-800 rounded-lg border border-gray-200 group hover:bg-gray-50 transition-colors"
                >
                  <FileSpreadsheet className="w-4 h-4 flex-shrink-0 text-gray-600" />
                  <span className="text-sm truncate max-w-[200px]">
                    {file.name}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFile(index);
                    }}
                    className="p-0.5 hover:bg-gray-200 rounded transition-colors flex-shrink-0"
                  >
                    <X className="w-3.5 h-3.5 text-gray-500 hover:text-gray-700" />
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="relative mb-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
              className="w-full outline-none text-sm"
            />
            {!input && !isFocused && (
              <div
                className={`absolute left-0 top-0 text-sm text-gray-400 pointer-events-none transition-opacity duration-500 ${
                  isAnimating ? "opacity-0" : "opacity-100"
                }`}
              >
                {placeholderExamples[currentPlaceholder]}
              </div>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Loading State */}
          {(isUploading || isAnalyzing) && (
            <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center gap-2 text-sm text-blue-700">
                <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                <span>
                  {isUploading && "Uploading dataset..."}
                  {isAnalyzing &&
                    "Analyzing dataset... (This may take 20-30 seconds)"}
                </span>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex items-center justify-between mt-6">
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading || isAnalyzing}
              className="text-gray-600 p-1.5 rounded-full hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Paperclip className="w-4 h-4" />
            </button>
            <button
              onClick={handleSubmit}
              disabled={
                isUploading ||
                isAnalyzing ||
                uploadedFiles.length === 0 ||
                !input.trim()
              }
              className="bg-black text-white p-1.5 rounded-full hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isUploading || isAnalyzing ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <ArrowUp className="w-4 h-4" />
              )}
            </button>
          </div>

          {/* Dataset Carousel */}
          <div className="mt-6 -mx-4 relative">
            <div className="absolute inset-y-0 left-0 w-12 bg-gradient-to-r from-white to-transparent z-10 pointer-events-none" />
            <div className="absolute inset-y-0 right-0 w-12 bg-gradient-to-l from-white to-transparent z-10 pointer-events-none" />

            <div className="overflow-hidden">
              <div className="flex gap-3 animate-scroll-carousel-infinite px-4">
                {[
                  ...popularDatasets,
                  ...popularDatasets,
                  ...popularDatasets,
                ].map((dataset, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-3 px-4 py-3 bg-gray-50 rounded-xl border border-gray-100 min-w-[300px] flex-shrink-0 hover:bg-gray-100 transition-colors cursor-pointer"
                  >
                    <img
                      src={dataset.logo}
                      alt={dataset.source}
                      className="w-8 h-8 rounded-full object-cover flex-shrink-0"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900 truncate">
                        {dataset.name}
                      </p>
                      <p className="text-xs text-gray-500 truncate">
                        {dataset.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Full-Page Drag and Drop Overlay */}
      {isFileDraggedOnPage && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            fixed inset-0 z-50 flex items-center justify-center
            transition-all duration-300 ease-out
            ${isFileDraggedOnPage ? "opacity-100" : "opacity-0 pointer-events-none"}
            ${
              isDragging
                ? "bg-blue-500/10 backdrop-blur-md"
                : "bg-white/30 backdrop-blur-md"
            }
          `}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".csv,.xls,.xlsx"
            onChange={handleFileSelect}
            className="hidden"
          />

          <div
            className={`
              border-2 border-dashed rounded-2xl p-16 text-center cursor-pointer bg-white/80 backdrop-blur-sm shadow-2xl
              transition-all duration-300 ease-out
              ${
                isDragging
                  ? "border-blue-500 scale-105 shadow-blue-500/20"
                  : "border-gray-400 scale-100"
              }
            `}
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="flex flex-col items-center gap-4">
              <div
                className={`relative transition-transform duration-300 ${isDragging ? "scale-110" : "scale-100"}`}
              >
                <FileSpreadsheet
                  className="w-20 h-20 text-gray-500"
                  strokeWidth={1.5}
                />
                <Upload
                  className={`w-8 h-8 absolute -bottom-1 -right-1 transition-colors duration-300 ${
                    isDragging ? "text-blue-600" : "text-gray-600"
                  }`}
                />
              </div>

              <div>
                <p
                  className={`mb-2 transition-colors duration-300 ${
                    isDragging ? "text-blue-700" : "text-gray-800"
                  }`}
                >
                  {isDragging
                    ? "Drop your files here"
                    : "Drag and drop your files here"}
                </p>
                <p className="text-xs text-gray-500">
                  Supported formats: .xlsx, .xls, .csv
                </p>
              </div>

              {/* Progress Indicator */}
              {uploadedFiles.length > 0 && (
                <div className="flex items-center gap-2 mt-2">
                  <div className="flex items-center gap-1 px-3 py-1.5 bg-white rounded-full border border-gray-300 shadow-sm">
                    <div className="flex gap-1">
                      {Array.from({ length: maxFiles }).map((_, i) => (
                        <div
                          key={i}
                          className={`w-1.5 h-1.5 rounded-full transition-all duration-300 ${
                            i < uploadedFiles.length
                              ? "bg-blue-600"
                              : "bg-gray-300"
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-xs text-gray-600 ml-1">
                      {uploadedFiles.length}/{maxFiles}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
