import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [health, setHealth] = useState(null);
  const [file, setFile] = useState(null);
  const [uploadedDataset, setUploadedDataset] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Analysis state
  const [analysisConfig, setAnalysisConfig] = useState({
    problemDescription: "",
    targetColumn: "",
    protectedColumns: "",
  });
  const [jobId, setJobId] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [polling, setPolling] = useState(false);

  // Check health on mount
  useEffect(() => {
    checkHealth();
  }, []);

  // Poll for analysis results
  useEffect(() => {
    if (!jobId || !polling) return;

    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`/analysis/result/${jobId}`);
        const result = response.data;

        if (result.status === "completed") {
          setAnalysisResult(result);
          setPolling(false);
          setSuccess("Analysis completed successfully!");
        } else if (result.status === "failed") {
          setError(`Analysis failed: ${result.error}`);
          setPolling(false);
        }
      } catch (err) {
        setError(`Failed to fetch results: ${err.message}`);
        setPolling(false);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId, polling]);

  const checkHealth = async () => {
    try {
      const response = await axios.get("/health");
      setHealth(response.data);
    } catch (err) {
      setHealth({ status: "unhealthy", error: err.message });
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setSuccess(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("/datasets/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setUploadedDataset(response.data);
      setSuccess(
        `Dataset uploaded successfully! ID: ${response.data.dataset_id}`,
      );

      // Auto-fill target column if score exists
      if (response.data.columns && response.data.columns > 0) {
        // This is just a guess; user can change it
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const handleStartAnalysis = async () => {
    if (!uploadedDataset) {
      setError("Please upload a dataset first");
      return;
    }

    if (
      !analysisConfig.problemDescription ||
      analysisConfig.problemDescription.trim().length < 10
    ) {
      setError("Please describe your ML problem (at least 10 characters)");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    setAnalysisResult(null);

    const protectedCols = analysisConfig.protectedColumns
      ? analysisConfig.protectedColumns
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean)
      : [];

    try {
      const response = await axios.post("/analysis/start", {
        dataset_id: uploadedDataset.dataset_id,
        problem_description: analysisConfig.problemDescription,
        target_column: analysisConfig.targetColumn || null,
        protected_columns: protectedCols,
      });

      setJobId(response.data.job_id);
      setPolling(true);
      setSuccess("Analysis started! GPT-5 is analyzing your data...");
    } catch (err) {
      setError(
        err.response?.data?.detail || err.message || "Failed to start analysis",
      );
    } finally {
      setLoading(false);
    }
  };

  const resetAll = () => {
    setFile(null);
    setUploadedDataset(null);
    setAnalysisConfig({
      problemDescription: "",
      targetColumn: "",
      protectedColumns: "",
    });
    setJobId(null);
    setAnalysisResult(null);
    setPolling(false);
    setError(null);
    setSuccess(null);
  };

  const getQualityClass = (score) => {
    if (score >= 80) return "excellent";
    if (score >= 60) return "good";
    if (score >= 40) return "fair";
    return "poor";
  };

  const getQualityLabel = (score) => {
    if (score >= 80) return "Excellent";
    if (score >= 60) return "Good";
    if (score >= 40) return "Fair";
    return "Poor";
  };

  return (
    <div className="app">
      <div className="header">
        <h1>
          📊 Senalign Dataset Quality Validator
          {health && (
            <span
              className={`status-badge ${health.status === "healthy" ? "healthy" : "unhealthy"}`}
            >
              {health.status === "healthy" ? "✓ Healthy" : "✗ Unhealthy"}
            </span>
          )}
        </h1>
        <p>
          Upload datasets and get AI-powered quality analysis with PII detection
        </p>
        {health && !health.openai_configured && (
          <div className="alert warning" style={{ marginTop: "15px" }}>
            ⚠️ OPENAI_API_KEY not configured. Analysis features will not work.
          </div>
        )}
      </div>

      {error && (
        <div className="alert error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {success && (
        <div className="alert success">
          <strong>Success:</strong> {success}
        </div>
      )}

      {/* Upload Section */}
      <div className="card">
        <h2>1️⃣ Upload Dataset</h2>

        <div className="upload-section">
          <input
            type="file"
            id="file-upload"
            accept=".csv,.tsv,.txt,.json,.jsonl,.xlsx,.xls,.xlsb,.parquet,.feather,.pkl,.pickle,.hdf,.h5,.dta,.sav,.xml,.html"
            onChange={handleFileChange}
          />
          <label htmlFor="file-upload" className="upload-label">
            📁 Choose File
          </label>
          <p style={{ marginTop: "10px", fontSize: "13px", color: "#64748b" }}>
            Supported: CSV, TSV, JSON, Excel, Parquet, Feather, Pickle, HDF5,
            Stata, SPSS, XML, HTML
          </p>

          {file && (
            <div className="file-info">
              <strong>Selected:</strong> {file.name} (
              {(file.size / 1024).toFixed(2)} KB)
            </div>
          )}
        </div>

        <button
          className="button"
          onClick={handleUpload}
          disabled={!file || loading}
        >
          {loading ? "Uploading..." : "⬆️ Upload Dataset"}
        </button>

        {uploadedDataset && (
          <div className="dataset-info">
            <div className="info-item">
              <label>Dataset ID</label>
              <value>{uploadedDataset.dataset_id}</value>
            </div>
            <div className="info-item">
              <label>Rows</label>
              <value>{uploadedDataset.rows}</value>
            </div>
            <div className="info-item">
              <label>Columns</label>
              <value>{uploadedDataset.columns}</value>
            </div>
            <div className="info-item">
              <label>Size</label>
              <value>{(uploadedDataset.size_bytes / 1024).toFixed(2)} KB</value>
            </div>
          </div>
        )}
      </div>

      {/* Analysis Configuration */}
      {uploadedDataset && !analysisResult && (
        <div className="card">
          <h2>2️⃣ Describe Your ML Problem</h2>

          <div className="form-group">
            <label>What are you trying to solve? *</label>
            <textarea
              rows="4"
              placeholder="Example: I want to predict customer churn based on usage patterns and demographics. I need to identify which customers are likely to leave in the next 30 days so we can take preventive action."
              value={analysisConfig.problemDescription}
              onChange={(e) =>
                setAnalysisConfig({
                  ...analysisConfig,
                  problemDescription: e.target.value,
                })
              }
              style={{
                width: "100%",
                padding: "10px",
                border: "1px solid #cbd5e1",
                borderRadius: "6px",
                fontSize: "14px",
                fontFamily: "inherit",
                resize: "vertical",
              }}
            />
            <small style={{ color: "#64748b", fontSize: "12px" }}>
              Describe your machine learning problem in plain English. Be
              specific about your goals and use case.
            </small>
          </div>

          <div className="form-group">
            <label>Target Column (optional)</label>
            <input
              type="text"
              placeholder="e.g., churn, score, label, price"
              value={analysisConfig.targetColumn}
              onChange={(e) =>
                setAnalysisConfig({
                  ...analysisConfig,
                  targetColumn: e.target.value,
                })
              }
            />
            <small style={{ color: "#64748b", fontSize: "12px" }}>
              The column you want to predict (leave blank if unsure)
            </small>
          </div>

          <div className="form-group">
            <label>Protected Columns (comma-separated, optional)</label>
            <input
              type="text"
              placeholder="e.g., email, phone, ssn, customer_id"
              value={analysisConfig.protectedColumns}
              onChange={(e) =>
                setAnalysisConfig({
                  ...analysisConfig,
                  protectedColumns: e.target.value,
                })
              }
            />
            <small style={{ color: "#64748b", fontSize: "12px" }}>
              Columns containing sensitive information that should be protected
            </small>
          </div>

          <button
            className="button"
            onClick={handleStartAnalysis}
            disabled={
              loading || polling || !analysisConfig.problemDescription.trim()
            }
          >
            {polling ? "⏳ Analyzing with GPT-5..." : "🔍 Analyze with GPT-5"}
          </button>
        </div>
      )}

      {/* Analysis Results */}
      {analysisResult && (
        <>
          <div className="card">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <h2>3️⃣ Analysis Results</h2>
              <button className="button secondary" onClick={resetAll}>
                🔄 Start Over
              </button>
            </div>

            {/* Quality Score */}
            <div className="quality-score">
              <div
                className={`score-circle ${getQualityClass(analysisResult.profile.quality_score)}`}
              >
                {analysisResult.profile.quality_score}
                <span className="score-label">
                  {getQualityLabel(analysisResult.profile.quality_score)}
                </span>
              </div>
            </div>

            {/* Dataset Overview */}
            <div className="dataset-info">
              <div className="info-item">
                <label>Total Rows</label>
                <value>{analysisResult.profile.total_rows}</value>
              </div>
              <div className="info-item">
                <label>Total Columns</label>
                <value>{analysisResult.profile.total_columns}</value>
              </div>
              <div className="info-item">
                <label>PII Detected</label>
                <value
                  style={{
                    color: analysisResult.profile.pii_summary.pii_detected
                      ? "#dc2626"
                      : "#16a34a",
                  }}
                >
                  {analysisResult.profile.pii_summary.pii_detected
                    ? "Yes"
                    : "No"}
                </value>
              </div>
              <div className="info-item">
                <label>PII Columns</label>
                <value>
                  {analysisResult.profile.pii_summary.pii_column_count}
                </value>
              </div>
            </div>

            {/* LLM Recommendations */}
            {analysisResult.llm_recommendations && (
              <div className="recommendations">
                <div className="section-title">🤖 GPT-5 Analysis</div>

                {analysisResult.llm_recommendations.problem_understanding && (
                  <div
                    className="info-item"
                    style={{ marginBottom: "15px", background: "#eff6ff" }}
                  >
                    <label>Problem Understanding</label>
                    <p
                      style={{
                        marginTop: "8px",
                        fontSize: "14px",
                        lineHeight: "1.6",
                      }}
                    >
                      {analysisResult.llm_recommendations.problem_understanding}
                    </p>
                  </div>
                )}

                {analysisResult.llm_recommendations.recommended_approach && (
                  <div
                    className="info-item"
                    style={{ marginBottom: "15px", background: "#f0fdf4" }}
                  >
                    <label>Recommended Approach</label>
                    <p
                      style={{
                        marginTop: "8px",
                        fontSize: "14px",
                        lineHeight: "1.6",
                        fontWeight: "600",
                      }}
                    >
                      {analysisResult.llm_recommendations.recommended_approach}
                    </p>
                  </div>
                )}

                <div className="info-item" style={{ marginBottom: "15px" }}>
                  <label>Overall Quality</label>
                  <value style={{ textTransform: "capitalize" }}>
                    {analysisResult.llm_recommendations.overall_quality}
                  </value>
                </div>

                {analysisResult.llm_recommendations.suitability_assessment && (
                  <>
                    <div className="section-title">
                      🎯 Suitability for Your Problem
                    </div>
                    <div
                      style={{
                        padding: "12px",
                        background: "#f8fafc",
                        borderRadius: "6px",
                        marginBottom: "15px",
                        fontSize: "14px",
                        lineHeight: "1.6",
                      }}
                    >
                      {
                        analysisResult.llm_recommendations
                          .suitability_assessment
                      }
                    </div>
                  </>
                )}

                {analysisResult.llm_recommendations.quality_issues?.length >
                  0 && (
                  <>
                    <div className="section-title">⚠️ Quality Issues</div>
                    <ul className="recommendation-list">
                      {analysisResult.llm_recommendations.quality_issues.map(
                        (issue, idx) => (
                          <li key={idx}>{issue}</li>
                        ),
                      )}
                    </ul>
                  </>
                )}

                {analysisResult.llm_recommendations
                  .feature_engineering_suggestions?.length > 0 && (
                  <>
                    <div className="section-title">
                      🔧 Feature Engineering Ideas
                    </div>
                    <ul className="recommendation-list">
                      {analysisResult.llm_recommendations.feature_engineering_suggestions.map(
                        (suggestion, idx) => (
                          <li key={idx}>{suggestion}</li>
                        ),
                      )}
                    </ul>
                  </>
                )}

                {analysisResult.llm_recommendations.recommendations?.length >
                  0 && (
                  <>
                    <div className="section-title">💡 Recommendations</div>
                    <ul className="recommendation-list">
                      {analysisResult.llm_recommendations.recommendations.map(
                        (rec, idx) => (
                          <li key={idx}>{rec}</li>
                        ),
                      )}
                    </ul>
                  </>
                )}

                {analysisResult.llm_recommendations.bias_risks?.length > 0 && (
                  <>
                    <div className="section-title">⚖️ Bias Risks</div>
                    <ul className="recommendation-list">
                      {analysisResult.llm_recommendations.bias_risks.map(
                        (risk, idx) => (
                          <li key={idx}>{risk}</li>
                        ),
                      )}
                    </ul>
                  </>
                )}

                {analysisResult.llm_recommendations.suggested_preprocessing
                  ?.length > 0 && (
                  <>
                    <div className="section-title">
                      🔧 Suggested Preprocessing
                    </div>
                    <ul className="recommendation-list">
                      {analysisResult.llm_recommendations.suggested_preprocessing.map(
                        (step, idx) => (
                          <li key={idx}>{step}</li>
                        ),
                      )}
                    </ul>
                  </>
                )}

                {analysisResult.llm_recommendations.potential_challenges
                  ?.length > 0 && (
                  <>
                    <div className="section-title">🚧 Potential Challenges</div>
                    <ul className="recommendation-list">
                      {analysisResult.llm_recommendations.potential_challenges.map(
                        (challenge, idx) => (
                          <li key={idx}>{challenge}</li>
                        ),
                      )}
                    </ul>
                  </>
                )}

                {analysisResult.llm_recommendations.success_metrics?.length >
                  0 && (
                  <>
                    <div className="section-title">
                      📊 Suggested Success Metrics
                    </div>
                    <ul className="recommendation-list">
                      {analysisResult.llm_recommendations.success_metrics.map(
                        (metric, idx) => (
                          <li key={idx}>{metric}</li>
                        ),
                      )}
                    </ul>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Column Details */}
          <div className="card">
            <h2>📋 Column Details</h2>
            <div className="columns-grid">
              {analysisResult.profile.columns.map((col, idx) => (
                <div
                  key={idx}
                  className={`column-card ${col.pii_detected ? "has-pii" : ""}`}
                >
                  <div className="column-header">
                    <span className="column-name">{col.name}</span>
                    <span className="column-type">{col.dtype}</span>
                  </div>

                  {col.pii_detected && (
                    <div style={{ marginBottom: "10px" }}>
                      <span className="pii-badge">
                        🔒 PII: {col.pii_types.join(", ")}
                      </span>
                    </div>
                  )}

                  <div className="column-stats">
                    <div className="stat">
                      <span className="stat-label">Missing:</span>
                      <span className="stat-value">
                        {col.missing_percent.toFixed(1)}%
                      </span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Unique:</span>
                      <span className="stat-value">{col.unique_count}</span>
                    </div>
                  </div>

                  {col.numeric_stats && (
                    <div className="column-stats" style={{ marginTop: "10px" }}>
                      <div className="stat">
                        <span className="stat-label">Mean:</span>
                        <span className="stat-value">
                          {col.numeric_stats.mean?.toFixed(2) || "N/A"}
                        </span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Std:</span>
                        <span className="stat-value">
                          {col.numeric_stats.std?.toFixed(2) || "N/A"}
                        </span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Min:</span>
                        <span className="stat-value">
                          {col.numeric_stats.min?.toFixed(2) || "N/A"}
                        </span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Max:</span>
                        <span className="stat-value">
                          {col.numeric_stats.max?.toFixed(2) || "N/A"}
                        </span>
                      </div>
                    </div>
                  )}

                  {col.top_categories && col.top_categories.length > 0 && (
                    <div style={{ marginTop: "10px" }}>
                      <div
                        className="stat-label"
                        style={{ marginBottom: "5px" }}
                      >
                        Top Values:
                      </div>
                      {col.top_categories.slice(0, 3).map((cat, i) => (
                        <div
                          key={i}
                          className="stat"
                          style={{ fontSize: "12px" }}
                        >
                          <span>{cat.value}</span>
                          <span>({cat.count})</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Raw JSON */}
          <div className="card">
            <h2>📄 Raw JSON Response</h2>
            <div className="json-display">
              <pre>{JSON.stringify(analysisResult, null, 2)}</pre>
            </div>
          </div>
        </>
      )}

      {polling && (
        <div className="card">
          <div className="loading">
            <div className="spinner"></div>
            <p style={{ marginTop: "20px" }}>
              GPT-5 is analyzing your dataset and understanding your problem...
            </p>
            <p
              style={{ marginTop: "10px", fontSize: "14px", color: "#64748b" }}
            >
              This may take 10-30 seconds
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
