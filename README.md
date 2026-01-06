# AI-Powered Quiz Platform

A modern quiz platform built with FastAPI and OpenRouter AI for intelligent answer evaluation and autonomous quiz generation using agentic AI architecture.

## Features

- **Autonomous Quiz Generation** - Generate complete quizzes from topic descriptions using AI agents
- **AI-Powered Evaluation** - Expert feedback with detailed explanations using OpenRouter API (Google Gemini 2.5 Flash)
- **Question Augmentation** - Generate additional questions matching existing quiz style
- **Session Tracking** - Persistent sessions with localStorage
- **Quiz Management** - Upload markdown files, paste content, or generate from descriptions
- **Custom Modals** - Professional Tailwind-styled dialogs
- **Quiz Link Sharing** - Copy quiz links with visual feedback
- **Timer Support** - Optional time limits with countdown (auto-calculated for generated quizzes)
- **Responsive Design** - Mobile-first UI with Tailwind CSS

## Quick Start

```bash
# Install
pip install -e .

# Configure
echo "OPENROUTER_API_KEY=your_key_here" > .env

# Run
uvicorn main:app --reload --port 8000
```

Visit [http://localhost:8000](http://localhost:8000)

Get API key at [openrouter.ai](https://openrouter.ai/)

## Quiz Format

```markdown
<Topic Name>

What is Python?
- A snake
> A programming language
- A movie

Which are valid types in Python?
> int
> str
- double

</Topic Name>
```

**Rules:**
- `<Topic>...</Topic>` tags wrap questions
- `-` prefix = incorrect answer
- `>` prefix = correct answer
- Multiple correct answers supported
- Empty line between questions
- **Timed quizzes:** `<Topic:5>` (5 minutes) - colon required, closing tag is `</Topic>`
- **Non-timed quizzes:** `<Topic>` or `<Topic 5>` (number without colon is ignored)

**Multiple topics per file:**
```markdown
<Topic 1:15>
...
</Topic 1>

<Topic 2>
...
</Topic 2>
```

## Project Structure

```
.
├── main.py                 # FastAPI entry point
├── api/
│   ├── config.py           # Configuration
│   ├── dependencies.py     # DI (storage, AI, sessions)
│   └── v1/quizzes.py       # API endpoints
├── templates/
│   ├── quizzes.html        # Quiz list
│   ├── quiz.html           # Quiz/results
│   └── modal.html          # Shared modal
├── static/
│   └── modal.js            # Modal functions
├── src/
│   ├── models.py           # Data models (Quiz, Question, Choice)
│   ├── parser.py           # Markdown parser
│   ├── storage.py          # Persistence
│   ├── quiz_ai.py          # Main AI orchestrator
│   └── agents/             # Agentic AI architecture
│       ├── agent.py        # Base Agent class
│       ├── generator.py    # GeneratorAgent
│       ├── augmenter.py    # AugmenterAgent
│       ├── evaluator.py    # EvaluatorAgent
│       ├── schemas.py      # Data schemas
│       └── tools/          # Agent tools
│           ├── quiz_profile_extractor.py
│           ├── topic_coverage_planner.py
│           ├── question_generator.py
│           ├── question_validator.py
│           ├── quiz_context_extractor.py
│           ├── topic_coverage_analyzer.py
│           ├── error_evaluator.py
│           ├── pedagogy_extractor.py
│           ├── feedback_generator.py
│           └── suggestions_generator.py
├── quizzes/                # Quiz files
│   └── examples/           # Samples (git-ignored)
└── pyproject.toml
```

## API Endpoints

```
POST   /api/v1/quizzes/generate                      # Generate quiz from description
POST   /api/v1/quizzes                               # Upload file
POST   /api/v1/quizzes/create                        # Create from content
DELETE /api/v1/quizzes                               # Delete all
GET    /api/v1/quizzes                               # List quizzes
GET    /api/v1/quizzes/{slug}                        # Get quiz
POST   /api/v1/quizzes/{slug}/sessions               # Start session
GET    /api/v1/quizzes/{slug}/sessions/latest        # Get session
POST   /api/v1/quizzes/{slug}/sessions/latest/submit # Submit answers
POST   /api/v1/quizzes/{slug}/generate               # Generate +15 questions 
```

All endpoints support JSON/HTML via `Accept` header.

## AI Integration

**Autonomous Quiz Generation (Workflow 1):**
- Generate complete quizzes from topic descriptions
- Automatically infers complexity, style, target audience, and domain
- Calculates appropriate time limits based on complexity
- Extracts question count from description or calculates from time limit
- Uses agentic architecture with specialized tools

**Answer Evaluation (Workflow 3):**
- Structured feedback with key concepts, explanations, and hints
- Detailed analysis of misconceptions
- Learning profile tracking with topic proficiencies
- Personalized suggestions based on quiz context

**Question Augmentation (Workflow 2):**
- Generates additional questions matching existing quiz style
- Analyzes coverage gaps and suggests concepts
- Maintains consistency with original quiz characteristics

## Dependencies

- `fastapi>=0.108.0` - Web framework
- `uvicorn>=0.25.0` - ASGI server
- `jinja2>=3.1.2` - Templates
- `openai>=1.0.0` - OpenRouter client
- `python-multipart>=0.0.6` - File uploads
- `python-dotenv>=1.0.0` - Environment variables

## Configuration

Create `.env` file:

```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Change AI model in `src/quiz_ai.py` or agent initialization:

```python
QuizAI(model="google/gemini-2.5-flash")  # Default
GeneratorAgent(model="google/gemini-2.5-flash")  # For quiz generation
EvaluatorAgent(model="google/gemini-2.5-flash")  # For evaluation
AugmenterAgent(model="google/gemini-2.5-flash")  # For augmentation
```

## License

MIT

---

**Built with FastAPI, OpenRouter AI, and Tailwind CSS**

[GitHub Repository](https://github.com/alfaarizi/agentic-mcq-generator)
