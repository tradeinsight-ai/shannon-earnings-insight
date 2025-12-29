# EarningsInsight - JIRA Workflow Reference

## Epic Structure

**Epic:** SHAN-727 - EarningsInsight: AI-Powered Earnings Call Analysis Platform
- **Epic Name:** EARNINGS-INSIGHT-V1
- **Labels:** earnings-insight, ai, platform, v1.0
- **Description:** Build a comprehensive web application that enables users to analyze earnings call transcripts using AI

## Completed Work (Retroactively Documented)

### Story: SHAN-720 - Implement live microphone transcription with local AI
- **Status:** Done
- **Story Points:** 8
- **Epic:** SHAN-727 (linked via comment)

#### Tasks:
1. **SHAN-721** - Implement LocalWhisperService backend with faster-whisper ✓
2. **SHAN-722** - Create WebSocket endpoint for real-time audio streaming ✓
3. **SHAN-723** - Implement frontend audio capture service with MediaRecorder ✓
4. **SHAN-724** - Create TranscriptionWebSocket service for bidirectional communication ✓
5. **SHAN-725** - Build MicrophoneControls UI component ✓
6. **SHAN-726** - Integrate microphone transcription into main dashboard ✓

## Workflow for Future Work

### 1. Creating New Stories

```bash
# Always link stories to the Epic!
jira-cli create-story \
  --summary "Your story title" \
  --description "User story description" \
  --project SHAN \
  --epic SHAN-727 \
  --story-points 5 \
  --labels "earnings-insight,feature-area"
```

### 2. Creating New Tasks

```bash
# Link tasks to the Epic
jira-cli create-task \
  --summary "Your task title" \
  --description "Task description" \
  --project SHAN \
  --epic SHAN-727 \
  --labels "earnings-insight,component"
```

### 3. Git Workflow

```bash
# Always branch from develop
git checkout develop
git pull origin develop

# Create story branch
git checkout -b story/SHAN-XXX-brief-description

# Create task branch from story
git checkout -b task/SHAN-YYY-brief-description

# Make commits with JIRA references
git commit -m "feat(component): [SHAN-YYY] description"

# Merge task → story → develop
```

### 4. Transition Issues

```bash
# Set to In Progress when starting
jira-cli transition SHAN-XXX --status "In Progress"

# Set to Done when complete
jira-cli transition SHAN-XXX --status "Done" --comment "Implementation details"
```

## Key Rules

1. **Always use --epic SHAN-727** when creating stories/tasks for earningsInsight
2. **Branch from develop**, not main
3. **Reference JIRA tickets** in all commit messages: `[SHAN-XXX]`
4. **Update ticket status** as you work (To Do → In Progress → Done)
5. **Add comments** with file paths and implementation details

## Future Story Ideas

- Sentiment analysis visualization
- Key insights extraction with LLMs
- Earnings call comparison across quarters
- Custom analysis prompts
- Export analysis reports
- Audio playback synchronization with transcript
- Multi-company comparison views
