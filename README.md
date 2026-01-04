# AI-Powered Quiz Platform

A lightweight quiz platform built with FastAPI and Google Gemini AI for intelligent answer evaluation.

## Features

- Session tracking with localStorage
- AI-powered answer evaluation
- Markdown file upload
- RESTful API with JSON/HTML responses
- Randomized questions and answers

## Quick Start

```bash
# Install
pip install -e .

# Configure
echo "GOOGLE_API_KEY=your_key_here" > .env

# Run
uvicorn main:app --reload --port 8000
```

Visit [http://localhost:8000](http://localhost:8000)

Get API key at [ai.google.dev](https://ai.google.dev)

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

**Multiple topics per file:**
```markdown
<Topic 1>
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
│   └── quiz.html           # Quiz/results
├── src/
│   ├── models.py           # Data models
│   ├── parser.py           # Markdown parser
│   ├── storage.py          # Persistence
│   └── quiz_ai.py          # Gemini AI
├── quizzes/                # Quiz files
│   └── examples/           # Samples (excluded)
└── pyproject.toml
```

## API Endpoints

```
POST   /api/v1/quizzes                               # Upload
GET    /api/v1/quizzes                               # List
GET    /api/v1/quizzes/{slug}                        # Preview
POST   /api/v1/quizzes/{slug}/sessions               # Start
GET    /api/v1/quizzes/{slug}/sessions/latest        # View session
POST   /api/v1/quizzes/{slug}/sessions/latest/submit # Submit
```

All endpoints support JSON/HTML via `Accept` header.

## Usage

**Take quiz:** Browse → Start → Answer → Submit → View results  
**Upload:** Scroll down → Select `.md` file → Upload  
**Retake:** Click "Retake Quiz" (clears session)

## Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `jinja2` - Templating
- `google-generativeai` - AI integration
- `python-multipart` - File uploads
- `python-dotenv` - Environment variables

## License

MIT

---

**Built with FastAPI, Gemini AI, and Tailwind CSS**