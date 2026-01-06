"""Quiz API endpoints with content negotiation (HTML/JSON)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Request, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from api.config import settings
from api.dependencies import get_storage, get_ai, get_sessions
from src.storage import QuizStorage
from src.quiz_ai import QuizAI
from src.parser import QuizParser
from src.models import Question, Choice, Quiz

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

# ============================================
# Helper Functions
# ============================================

def accepts_json(request: Request) -> bool:
    """Check if client accepts JSON response."""
    accept = request.headers.get("accept", "")
    return "application/json" in accept

def serialize_quizzes(quizzes: List[Quiz]) -> List[Dict]:
    """Serialize quizzes for JSON/HTML."""
    return [
        {
            "slug": q.slug,
            "topic": q.topic,
            "questions": q.total_questions,
            "time_limit": q.time_limit
        }
        for q in quizzes
    ]

def serialize_questions(
    questions: List[Question],
    evaluations: Optional[Dict] = None
) -> List[Dict]:
    """Serialize questions. If evaluations provided, include grading results."""
    result = []
    for i, q in enumerate(questions):
        data = {
            "text": q.text,
            "choices": [c.text for c in q.choices],
            "multiple": len(q.correct_choices) > 1
        }
        if evaluations and i in evaluations:
            eval_data = evaluations[i]
            data["your_answer"] = eval_data.get("your_answer", [])
            data["correct_answers"] = eval_data.get("correct_answers", [])
            data["correct"] = eval_data.get("correct", False)
            # Add structured feedback and suggestions
            if eval_data.get("feedback"):
                data["feedback"] = eval_data["feedback"]
            if eval_data.get("suggestions"):
                data["suggestions"] = eval_data["suggestions"]
        result.append(data)
    return result

def serialize_evaluation(
    ai: QuizAI,
    question: Question,
    selected: List[Choice],
    topic: str = "general",
    learning_profile: Optional[Dict] = None,
    quiz_context: Optional[Any] = None
) -> Dict:
    """Serialize evaluation with AI-generated feedback using EvaluatorAgent."""
    is_correct = set(selected) == set(question.correct_choices)
    correct_choices = [c.text for c in question.correct_choices]

    try:
        from src.agents.schemas import LearningProfile
        
        # Convert dict to LearningProfile if provided
        profile = None
        if learning_profile:
            profile = LearningProfile.from_dict(learning_profile)
        
        evaluation = ai.evaluate_answer(
            question=question,
            selected=selected,
            topic=topic,
            learning_profile=profile,
            quiz_context=quiz_context
        )
        
        # Extract structured feedback
        feedback = evaluation.get("feedback", {})
        
        result = {
            "correct": is_correct,
            "feedback": feedback,
            "error_evaluation": evaluation.get("error_evaluation", {}),
            "suggestions": evaluation.get("suggestions"),
            "your_answer": [c.text for c in selected],
            "correct_answers": correct_choices
        }
        
        # Include learning_profile in result for session updates
        if evaluation.get("learning_profile"):
            result["learning_profile"] = evaluation["learning_profile"]
        
        return result
    except Exception as e:
        import logging
        logging.error(f"AI evaluation failed: {type(e).__name__}: {str(e)}")
        # Fallback response
        return {
            "correct": is_correct,
            "feedback": None,
            "error_evaluation": None,
            "suggestions": None,
            "your_answer": [c.text for c in selected],
            "correct_answers": correct_choices
        }

# ============================================
# API Endpoints
# ============================================

@router.post("")
async def upload_quiz(
    file: UploadFile = File(...), 
    storage: QuizStorage = Depends(get_storage)
):
    """Upload quiz markdown file."""
    try:
        content = await file.read()
        quizzes = QuizParser.from_string(content.decode('utf-8'), source=file.filename)
        if not quizzes:
            raise HTTPException(status_code=400, detail="No quizzes found in file")
        for quiz in quizzes:
            storage.save_quiz(quiz)
        return RedirectResponse(url=f"{settings.API_BASE_URL}/quizzes", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse quiz: {str(e)}")


@router.post("/create")
async def create_quiz(
    request: Request,
    storage: QuizStorage = Depends(get_storage)
):
    """Create quiz from pasted content."""
    try:
        body = await request.json()
        content = body.get("content", "")
        if not content:
            raise HTTPException(status_code=400, detail="No content provided")
        
        quizzes = QuizParser.from_string(content, source="pasted")
        if not quizzes:
            raise HTTPException(status_code=400, detail="No quizzes found in content")
        
        for quiz in quizzes:
            storage.save_quiz(quiz)
        
        return JSONResponse({"message": f"Created {len(quizzes)} quiz(es)"}, status_code=201)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse quiz: {str(e)}")


@router.delete("")
async def reset_quizzes(storage: QuizStorage = Depends(get_storage)):
    """Delete all quizzes except those in examples directory."""
    try:
        storage.delete_quizzes()
        return JSONResponse({"message": "All quizzes deleted successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete quizzes: {str(e)}")

@router.get("")
async def list_quizzes(
    request: Request, 
    storage: QuizStorage = Depends(get_storage)
):
    """List all quizzes."""
    quizzes = serialize_quizzes(storage.get_quizzes())
    if accepts_json(request):
        return JSONResponse({"quizzes": quizzes})
    return templates.TemplateResponse("quizzes.html", {
        "request": request,
        "quizzes": quizzes,
        "api_base_url": settings.API_BASE_URL
    })


@router.get("/{slug}")
async def get_quiz(
    request: Request,
    slug: str,
    session_id: Optional[str] = Query(None),
    storage: QuizStorage = Depends(get_storage),
    sessions: Dict[str, Any] = Depends(get_sessions)
):
    """Get quiz preview or session."""
    quiz = storage.get_quiz(slug)
    if not quiz:
        if accepts_json(request):
            raise HTTPException(status_code=404, detail="Quiz not found")
        return RedirectResponse(url=f"{settings.API_BASE_URL}/quizzes")
    
    # JSON: return preview
    if accepts_json(request):
        quiz.shuffle_questions()
        return JSONResponse({
            "slug": quiz.slug,
            "topic": quiz.topic,
            "time_limit": quiz.time_limit,
            "questions": serialize_questions(quiz.questions)
        })
    
    # HTML: show preview or session
    if not session_id or session_id not in sessions:
        # Preview
        return templates.TemplateResponse("quiz.html", {
            "request": request,
            "quiz": {
                "slug": quiz.slug,
                "topic": quiz.topic,
                "time_limit": quiz.time_limit,
                "questions": serialize_questions(quiz.questions)
            },
            "status": "preview",
            "api_base_url": settings.API_BASE_URL
        })
    
    # Active session
    session = sessions[session_id]
    session_quiz = session["quiz"]
    return templates.TemplateResponse("quiz.html", {
        "request": request,
        "quiz": {
            "slug": session_quiz.slug,
            "topic": session_quiz.topic,
            "time_limit": session_quiz.time_limit,
            "questions": serialize_questions(
                session_quiz.questions,
                evaluations=session.get("evaluations") if session["status"] == "completed" else None
            )
        },
        "session_id": session_id,
        "status": session["status"],
        "started_at": session["started_at"].isoformat(),
        "submitted_at": session["submitted_at"].isoformat() if session.get("submitted_at") else None,
        "score": session.get("score"),
        "total": session.get("total"),
        "api_base_url": settings.API_BASE_URL
    })


@router.post("/{slug}/sessions")
async def start_session(
    request: Request,
    slug: str,
    storage: QuizStorage = Depends(get_storage),
    sessions: Dict[str, Any] = Depends(get_sessions)
):
    """Start new quiz session."""
    quiz = storage.get_quiz(slug)
    if not quiz:
        if accepts_json(request):
            raise HTTPException(status_code=404, detail="Quiz not found")
        return RedirectResponse(url=f"{settings.API_BASE_URL}/quizzes", status_code=303)
    
    session_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)
    quiz.shuffle_questions()

    # Record latest session
    sessions[session_id] = {
        "session_id": session_id,
        "slug": slug,
        "quiz": quiz,
        "status": "in_progress",
        "started_at": started_at,
        "submitted_at": None,
        "answers": {},
        "evaluations": {},
        "score": None,
        "total": quiz.total_questions,
        "learning_profile": {}
    }
    
    if accepts_json(request):
        return JSONResponse({
            "session_id": session_id,
            "slug": slug,
            "status": "in_progress",
            "started_at": started_at.isoformat() + "Z"
        }, status_code=201)
    return RedirectResponse(url=f"{settings.API_BASE_URL}/quizzes/{slug}", status_code=303)


@router.get("/{slug}/sessions/latest")
async def get_latest_session(
    slug: str,
    session_id: str = Query(...),
    sessions: Dict[str, Any] = Depends(get_sessions)
):
    """Get latest session (JSON only)."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Retrieve latest session
    session = sessions[session_id]
    quiz = session["quiz"]
    
    response = {
        "session_id": session_id,
        "slug": slug,
        "status": session["status"],
        "started_at": session["started_at"].isoformat() + "Z",
        "quiz": {
            "slug": quiz.slug,
            "topic": quiz.topic,
            "time_limit": quiz.time_limit,
            "questions": serialize_questions(
                quiz.questions,
                evaluations=session.get("evaluations") if session["status"] == "completed" else None
            )
        }
    }
    
    if session["status"] == "completed":
        response["submitted_at"] = session["submitted_at"].isoformat() + "Z"
        response["score"] = session["score"]
        response["total"] = session["total"]
    
    return JSONResponse(response)


@router.post("/{slug}/sessions/latest/submit")
async def submit_session(
    request: Request,
    slug: str,
    session_id: str = Query(...),
    ai: QuizAI = Depends(get_ai),
    sessions: Dict[str, Any] = Depends(get_sessions)
):
    """Submit quiz answers for JSON."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session["status"] == "completed":
        raise HTTPException(status_code=400, detail="Already submitted")
    
    quiz = session["quiz"]
    body = await request.json()
    
    # Extract quiz context once for all evaluations
    from src.agents.tools.quiz_context_extractor import extract_quiz_context
    quiz_context = extract_quiz_context(quiz, agent=ai.evaluator)
    
    # Parse and evaluate answers
    answers = {}
    evaluations = {}
    learning_profile = session.get("learning_profile", {})
    
    for idx_str, texts in body.get("answers", {}).items():
        idx = int(idx_str)
        if idx >= len(quiz.questions):
            continue
        question = quiz.questions[idx]
        selected = [c for c in question.choices if c.text in texts]
        if selected:
            answers[idx] = selected
            evaluation_result = serialize_evaluation(
                ai, 
                question, 
                selected,
                topic=quiz.topic,
                learning_profile=learning_profile,
                quiz_context=quiz_context
            )
            evaluations[idx] = evaluation_result
            # Update learning profile from evaluation result if available
            if evaluation_result.get("learning_profile"):
                learning_profile = evaluation_result["learning_profile"]
    
    # Update session
    session["status"] = "completed"
    session["submitted_at"] = datetime.now(timezone.utc)
    session["answers"] = answers
    session["evaluations"] = evaluations
    session["score"] = sum(1 for e in evaluations.values() if e.get("correct"))
    session["learning_profile"] = learning_profile
    
    return JSONResponse({"score": session["score"], "total": quiz.total_questions})


@router.post("/{slug}/generate")
async def generate_questions(
    slug: str,
    storage: QuizStorage = Depends(get_storage),
    ai: QuizAI = Depends(get_ai)
):
    """Generate 15 more questions for the quiz."""
    quiz = storage.get_quiz(slug)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    try:
        # Generate 15 new questions based on existing ones
        new_questions = ai.generate_questions(
            topic=quiz.topic,
            samples=quiz.questions,
            count=15
        )

        if not new_questions:
            raise HTTPException(status_code=500, detail="Failed to generate questions")

        # Add new questions to the quiz
        quiz.questions.extend(new_questions)

        # Save updated quiz
        storage.save_quiz(quiz)

        return JSONResponse({
            "message": f"Generated {len(new_questions)} new questions",
            "total_questions": len(quiz.questions),
            "new_count": len(new_questions)
        })
    except Exception as e:
        import logging
        logging.error(f"Failed to generate questions: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")