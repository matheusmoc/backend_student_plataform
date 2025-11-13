# Exam Submission API Documentation

This document explains how to use the exam submission and results functionality.

## Overview

The system provides two main features:
1. **Submit Exam Answers**: Students can submit all their answers for an exam at once
2. **View Results**: Students can view their detailed results including correct/incorrect answers and score percentage

## Database Models

### ExamSubmission
- `student`: Foreign key to Student model
- `exam`: Foreign key to Exam model  
- `submitted_at`: Timestamp when submitted
- `score`: Property that calculates percentage score
- `correct_answers_count`: Property that counts correct answers
- Unique constraint on (student, exam) - one submission per student per exam

### SubmissionAnswer
- `submission`: Foreign key to ExamSubmission
- `question`: Foreign key to Question
- `selected_alternative_option`: Integer (1-5 representing A-E)
- `is_correct`: Property that checks if answer matches correct alternative
- Unique constraint on (submission, question) - one answer per question per submission

## API Endpoints

### 1. Submit Exam Answers
**POST** `/api/exam/submit/`

Submit all answers for an exam at once.

**Request Body:**
```json
{
    "student_id": 1,
    "exam_id": 1,
    "answers": [
        {"question_id": 1, "selected_option": 3},
        {"question_id": 2, "selected_option": 2},
        {"question_id": 3, "selected_option": 1},
        {"question_id": 4, "selected_option": 4},
        {"question_id": 5, "selected_option": 2}
    ]
}
```

**Response (Success - 201):**
```json
{
    "success": true,
    "message": "Exam submitted successfully",
    "submission_id": 1,
    "submitted_at": "2025-11-13T14:53:21.123456Z",
    "total_answers": 5
}
```

**Response (Error - 400):**
```json
{
    "success": false,
    "errors": {
        "student_id": ["Student does not exist"],
        "answers": ["Questions [6, 7] do not belong to exam 1"]
    }
}
```

### 2. Get Exam Results (by submission ID)
**GET** `/api/exam/results/{submission_id}/`

Get detailed results for a specific submission.

**Response (200):**
```json
{
    "success": true,
    "results": {
        "id": 1,
        "student_name": "John Doe",
        "exam_name": "Prova Falsa 1",
        "submitted_at": "2025-11-13T14:53:21.123456Z",
        "total_questions": 5,
        "correct_answers": 4,
        "score_percentage": 80.0,
        "questions": [
            {
                "id": 1,
                "content": "Qual parte do corpo usamos para ouvir?",
                "student_answer": 3,
                "student_answer_letter": "C",
                "correct_answer": 3,
                "correct_answer_letter": "C",
                "is_correct": true,
                "alternatives": [
                    {"option": 1, "option_letter": "A", "content": "Dentes", "is_correct": false},
                    {"option": 2, "option_letter": "B", "content": "Cabelos", "is_correct": false},
                    {"option": 3, "option_letter": "C", "content": "Ouvidos", "is_correct": true},
                    {"option": 4, "option_letter": "D", "content": "Braços", "is_correct": false}
                ]
            }
            // ... more questions
        ]
    }
}
```

### 3. Get Exam Results (by student and exam ID)
**GET** `/api/exam/student/{student_id}/exam/{exam_id}/results/`

Alternative endpoint to get results using student and exam IDs.

Same response format as above.

## Validation Rules

### Submission Validation
- Student must exist
- Exam must exist
- All questions must exist and belong to the specified exam
- No duplicate questions in the answer list
- Student cannot submit the same exam twice
- Selected option must be between 1-5 (A-E)

### Error Scenarios
- **404**: Submission not found (for results endpoints)
- **400**: Validation errors (invalid data, duplicate submission, etc.)

## Usage Examples

### Example 1: Complete workflow
1. Student submits answers for exam ID 1
2. System validates all data and creates submission
3. Student can view results using submission ID or student/exam IDs

### Example 2: Answer options
- Option 1 = A
- Option 2 = B  
- Option 3 = C
- Option 4 = D
- Option 5 = E

## Database Setup

To apply the migrations:
```bash
python manage.py makemigrations exam
python manage.py migrate
```

The system automatically creates the ExamSubmission and SubmissionAnswer tables with proper relationships and constraints.