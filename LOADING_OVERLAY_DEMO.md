# Loading Overlay Visual Demo

## What Users Will See

### Step 1: Upload Starting (0-2 seconds)
```
┌─────────────────────────────────────────────────────┐
│                    🗄️ Database Icon                 │
│             Uploading Dataset                        │
│    Please wait while we securely upload your data   │
└─────────────────────────────────────────────────────┘

🟢 Uploading Dataset ✓ Complete
⚪ Profiling Data - Pending
⚪ Scanning for PII - Pending
⚪ Generating AI Insights - Pending
⚪ Finding Resources - Pending

Progress: 20% [████████░░░░░░░░░░░░░░░░░░░░░░░░]
```

### Step 2: Analysis in Progress (3-8 seconds)
```
┌─────────────────────────────────────────────────────┐
│                    🗄️ Database Icon                 │
│             Analyzing Your Dataset                   │
│  Running comprehensive quality checks and insights   │
└─────────────────────────────────────────────────────┘

🟢 Uploading Dataset ✓ Complete
🟡 Profiling Data ⏳ Analyzing quality metrics... (Spinner)
⚪ Scanning for PII - Pending
⚪ Generating AI Insights - Pending
⚪ Finding Resources - Pending

Progress: 40% [████████████████░░░░░░░░░░░░░░░░]
```

### Step 3: Mid-Analysis (9-14 seconds)
```
┌─────────────────────────────────────────────────────┐
│                    🗄️ Database Icon                 │
│             Analyzing Your Dataset                   │
│  Running comprehensive quality checks and insights   │
└─────────────────────────────────────────────────────┘

🟢 Uploading Dataset ✓ Complete
🟢 Profiling Data ✓ Complete
🟢 Scanning for PII ✓ Complete
🟡 Generating AI Insights ⏳ Creating recommendations... (Spinner)
⚪ Finding Resources - Pending

Progress: 80% [████████████████████████████░░░░]
```

### Step 4: Final Step (15-20 seconds)
```
┌─────────────────────────────────────────────────────┐
│                    🗄️ Database Icon                 │
│             Analyzing Your Dataset                   │
│  Running comprehensive quality checks and insights   │
└─────────────────────────────────────────────────────┘

🟢 Uploading Dataset ✓ Complete
🟢 Profiling Data ✓ Complete  
🟢 Scanning for PII ✓ Complete
🟢 Generating AI Insights ✓ Complete
🟡 Finding Resources ⏳ Searching for materials... (Spinner)

Progress: 100% [████████████████████████████████]
```

### Step 5: Completion & Transition
```
All steps complete → Fade out → Navigate to Results Page
```

## Color Legend
- 🟢 Green = Completed (Emerald background)
- 🟡 Yellow/Orange = Active (Amber background with animation)
- ⚪ Gray = Pending (Reduced opacity)
- ✓ = Checkmark icon
- ⏳ = Spinner animation

## Animations
1. Overlay fades in with backdrop blur
2. Modal zooms in from 95% to 100% scale
3. Steps animate in with staggered delay (50ms each)
4. Active step icon pulses
5. Progress bar smoothly fills
6. Completed steps scale down slightly (98%)
