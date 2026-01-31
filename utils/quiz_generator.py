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
        """Parse AI-generated questions."""
        questions = []
        lines = response.split('\n')
        
        current_question = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Q:'):
                if current_question and 'question' in current_question:
                    questions.append(current_question)
                current_question = {'question': line[2:].strip()}
            
            elif line.startswith('A)'):
                current_question['options'] = [line[2:].strip()]
            elif line.startswith('B)'):
                if 'options' in current_question:
                    current_question['options'].append(line[2:].strip())
            elif line.startswith('C)'):
                if 'options' in current_question:
                    current_question['options'].append(line[2:].strip())
            elif line.startswith('D)'):
                if 'options' in current_question:
                    current_question['options'].append(line[2:].strip())
            
            elif line.startswith('ANSWER:'):
                answer = line[7:].strip().upper()
                if answer in ['A', 'B', 'C', 'D']:
                    current_question['correct'] = answer
            
            elif line.startswith('EXPLANATION:'):
                current_question['explanation'] = line[12:].strip()
        
        # Add last question
        if current_question and 'question' in current_question:
            questions.append(current_question)
        
        # Validate questions
        valid_questions = []
        for q in questions:
            if (q.get('question') and 
                q.get('options') and len(q.get('options', [])) == 4 and
                q.get('correct') and
                q.get('explanation')):
                valid_questions.append(q)
        
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
