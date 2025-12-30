# AI Video Editor

An advanced AI-powered video editing application aimed at automating and enhancing the video creation process. This project leverages Large Language Models (LLMs) to act as an AI Director, intelligently making editing decisions based on user intent, style references, and content analysis.

## Features

- **AI Director**: Utilizes LLMs to interpret user prompts and generate detailed Edit Decision Lists (EDL).
- **Asset Analysis**: Automatically tags and analyzes video scenes and audio beats to understand content context.
- **Style Extraction**: Extracts pacing, color grading, and transition styles from reference videos to match a specific "vibe".
- **Music Integration**: Seamlessly searches and integrates background music that aligns with the video's rhythm and mood.
- **Automated Editing**: Executes complex edits including cuts, speed ramping, filters, and transitions using FFmpeg/MoviePy.

## Tech Stack

- **Frontend**: Next.js, TailwindCSS (Chat-based Interface)
- **Backend**: Python (FastAPI/Flask)
- **Video Processing**: FFmpeg, MoviePy
- **AI/ML**: OpenAI API (Cost-effective models), TensorFlow Lite (for local optimization if needed)

## Getting Started

### Prerequisites

- Node.js (v18+)
- Python (v3.10+)
- FFmpeg installed and in system PATH

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/ai_video_editor.git
    cd ai_video_editor
    ```

2.  **Backend Setup:**
    ```bash
    cd backend
    pip install -r requirements.txt
    python main.py
    ```

3.  **Frontend Setup:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
