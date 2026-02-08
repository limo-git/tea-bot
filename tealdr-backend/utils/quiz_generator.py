import re
import random
from datetime import datetime, timedelta
from utils.logger import get_logger
from ai.gemini_client import gemini_client

logger = get_logger(__name__)

class QuizGenerator:
    """Generate Kahoot-style quizzes from server message history."""
    
    @staticmethod
    async def generate_quiz(messages, num_questions=5):
        """Generate quiz questions from messages."""
        try:
            if len(messages) < 10:
                return None, "Not enough messages to generate a quiz. Need at least 10 messages."
            
            # Sample interesting messages for quiz generation
            sampled_messages = random.sample(messages, min(50, len(messages)))
            
            # Build prompt for AI to generate quiz questions
            message_context = "\n".join([
                f"{msg.get('author_name')}: {msg.get('content')[:200]}"
                for msg in sampled_messages[:20]
            ])
            
            prompt = f"""Based on these Discord server messages, create {num_questions} multiple-choice trivia questions.

Messages:
{message_context}

For each question, provide:
1. The question text
2. Four answer options (A, B, C, D)
3. The correct answer (A, B, C, or D)
4. A brief explanation

Format each question exactly like this:
Q: [question text]
A) [option A]
B) [option B]
C) [option C]
D) [option D]
ANSWER: [correct letter]
EXPLANATION: [brief explanation]

Make questions fun and engaging! Focus on:
- Who said what
- When things happened
- Popular topics discussed
- Funny or memorable moments

Generate {num_questions} questions now:"""

            response = await gemini_client.generate_response(prompt)
            
            # Parse questions from response
            questions = QuizGenerator._parse_questions(response)
            
            if not questions:
                # Fallback to template-based questions
                questions = QuizGenerator._generate_template_questions(sampled_messages, num_questions)
            
            return questions[:num_questions], None
            
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            return None, f"Failed to generate quiz: {str(e)}"
    
    @staticmethod
    def _parse_questions(response):
        """Parse AI-generated questions with robust pattern matching."""
        questions = []
        lines = response.split('\n')
        
        current_question = {}
        
        # Patterns to match various AI formatting styles
        q_pattern = re.compile(r'^\*{0,2}Q\d*[:\.]?\*{0,2}\s*(.*)', re.IGNORECASE)
        opt_pattern = re.compile(r'^\*{0,2}([A-D])[)\.]\*{0,2}\s*(.*)', re.IGNORECASE)
        answer_pattern = re.compile(r'^\*{0,2}ANSWER\s*[:\.]?\*{0,2}\s*([A-D])', re.IGNORECASE)
        explanation_pattern = re.compile(r'^\*{0,2}EXPLANATION\s*[:\.]?\*{0,2}\s*(.*)', re.IGNORECASE)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            q_match = q_pattern.match(line)
            if q_match:
                if current_question and 'question' in current_question:
                    questions.append(current_question)
                current_question = {'question': q_match.group(1).strip()}
                continue
            
            opt_match = opt_pattern.match(line)
            if opt_match:
                letter = opt_match.group(1).upper()
                text = opt_match.group(2).strip()
                if letter == 'A':
                    current_question['options'] = [text]
                elif 'options' in current_question:
                    current_question['options'].append(text)
                continue
            
            ans_match = answer_pattern.match(line)
            if ans_match:
                current_question['correct'] = ans_match.group(1).upper()
                continue
            
            exp_match = explanation_pattern.match(line)
            if exp_match:
                current_question['explanation'] = exp_match.group(1).strip()
                continue
        
        # Add last question
        if current_question and 'question' in current_question:
            questions.append(current_question)
        
        logger.info(f"Parsed {len(questions)} raw questions from AI response")
        
        # Validate questions — fill in missing explanation with default
        valid_questions = []
        for q in questions:
            if not q.get('explanation'):
                q['explanation'] = 'No explanation provided.'
            if (q.get('question') and 
                q.get('options') and len(q.get('options', [])) == 4 and
                q.get('correct')):
                valid_questions.append(q)
            else:
                logger.warning(f"Dropped invalid question: {q.get('question', 'N/A')[:50]} — "
                              f"options={len(q.get('options', []))}, correct={q.get('correct')}")
        
        logger.info(f"{len(valid_questions)} valid questions after validation")
        return valid_questions
    
    @staticmethod
    def _generate_template_questions(messages, num_questions):
        """Generate template-based questions as fallback."""
        questions = []
        
        # Get unique authors
        authors = list(set(msg.get('author_name') for msg in messages if msg.get('author_name')))
        
        if len(authors) < 4:
            return []
        
        # Question type 1: Who said this?
        for _ in range(min(num_questions, len(messages))):
            msg = random.choice(messages)
            content = msg.get('content', '')[:100]
            correct_author = msg.get('author_name')
            
            if not content or not correct_author or correct_author not in authors:
                continue
            
            # Get 3 wrong answers
            wrong_authors = [a for a in authors if a != correct_author]
            if len(wrong_authors) < 3:
                continue
            
            options_list = [correct_author] + random.sample(wrong_authors, 3)
            random.shuffle(options_list)
            
            correct_letter = ['A', 'B', 'C', 'D'][options_list.index(correct_author)]
            
            questions.append({
                'question': f'Who said: "{content}"?',
                'options': options_list,
                'correct': correct_letter,
                'explanation': f'This was said by {correct_author}!'
            })
            
            if len(questions) >= num_questions:
                break
        
        return questions

quiz_generator = QuizGenerator()
