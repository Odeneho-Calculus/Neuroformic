"""
NLP module for understanding form questions and predicting appropriate answers.
"""
import re
from typing import Dict, List, Any, Tuple, Optional
import spacy
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

from utils.logger import get_logger
from config import NLP_MODEL, TRANSFORMERS_MODEL

logger = get_logger()

class QuestionAnalyzer:
    """Analyze form questions and determine appropriate answers."""
    
    def __init__(self, use_transformers: bool = True):
        """
        Initialize the question analyzer with NLP models.
        
        Args:
            use_transformers: Whether to use transformer models for analysis
        """
        logger.info("Initializing NLP components")
        
        # Load spaCy model
        try:
            self.nlp = spacy.load(NLP_MODEL)
            logger.info(f"Loaded spaCy model: {NLP_MODEL}")
        except Exception as e:
            logger.error(f"Error loading spaCy model: {str(e)}")
            logger.info("Downloading spaCy model...")
            spacy.cli.download(NLP_MODEL)
            self.nlp = spacy.load(NLP_MODEL)
        
        # Initialize transformers if enabled
        self.use_transformers = use_transformers
        if use_transformers:
            try:
                self.sentiment_analyzer = pipeline("sentiment-analysis")
                logger.info("Loaded transformer sentiment analysis pipeline")
                
                # Load question classification model (for demonstration purposes)
                # In a real implementation, you might want to fine-tune a model for this specific task
                self.question_classifier = pipeline(
                    "text-classification", 
                    model=TRANSFORMERS_MODEL
                )
                logger.info(f"Loaded transformer model: {TRANSFORMERS_MODEL}")
            except Exception as e:
                logger.error(f"Error loading transformer models: {str(e)}")
                self.use_transformers = False
    
    def analyze_question(self, question_text: str) -> Dict[str, Any]:
        """
        Analyze a question and extract key information.
        
        Args:
            question_text: The text of the question
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        logger.info(f"Analyzing question: {question_text[:50]}...")
        
        # Process with spaCy
        doc = self.nlp(question_text)
        
        # Extract key information
        question_type = self._determine_question_type(doc)
        sentiment = self._analyze_sentiment(question_text)
        keywords = self._extract_keywords(doc)
        
        # Get the appropriate answer strategy
        answer_strategy = self._determine_answer_strategy(question_type, sentiment, keywords)
        
        analysis = {
            "question_type": question_type,
            "sentiment": sentiment,
            "keywords": keywords,
            "answer_strategy": answer_strategy,
            "expected_answer_type": self._determine_expected_answer_type(doc, question_type)
        }
        
        logger.debug(f"Question analysis complete: {analysis}")
        return analysis
    
    def predict_best_answer(self, question_text: str, options: List[str]) -> Tuple[int, float]:
        """
        Predict the best answer from a list of options.
        
        Args:
            question_text: The text of the question
            options: List of answer options
            
        Returns:
            Tuple[int, float]: Index of best option and confidence score
        """
        logger.info(f"Predicting best answer for question: {question_text[:50]}...")
        
        # Analyze the question
        analysis = self.analyze_question(question_text)
        
        # Score each option
        scores = []
        for option in options:
            score = self._score_option(option, question_text, analysis)
            scores.append(score)
        
        # Find the best option
        best_index = scores.index(max(scores))
        confidence = scores[best_index]
        
        logger.info(f"Selected option {best_index} with confidence {confidence:.2f}")
        return best_index, confidence
    
    def _determine_question_type(self, doc) -> str:
        """
        Determine the type of question.
        
        Args:
            doc: spaCy document
            
        Returns:
            str: Question type
        """
        # Check for question words
        question_words = ["what", "when", "where", "who", "why", "how", "which", "can", "do", "is", "are"]
        
        # Extract the first few tokens to check for question words
        first_words = [token.text.lower() for token in list(doc)[:3]]
        
        # Check if any question words are present
        for word in question_words:
            if word in first_words:
                if word == "what":
                    return "factual"
                elif word == "when":
                    return "temporal"
                elif word == "where":
                    return "spatial"
                elif word == "who":
                    return "person"
                elif word == "why":
                    return "reason"
                elif word == "how":
                    return "process"
                elif word in ["can", "do", "is", "are"]:
                    return "yes_no"
                else:
                    return "selection"
        
        # If no question word is found, check if it ends with a question mark
        if doc.text.strip().endswith("?"):
            return "general_question"
        
        # If it's not a question, it might be a statement or prompt
        return "statement"
    
    def _analyze_sentiment(self, text: str) -> str:
        """
        Analyze the sentiment of the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            str: Sentiment (positive, negative, neutral)
        """
        if self.use_transformers:
            try:
                result = self.sentiment_analyzer(text)[0]
                return result['label'].lower()
            except Exception as e:
                logger.warning(f"Error in transformer sentiment analysis: {str(e)}")
        
        # Fallback to rule-based sentiment analysis
        positive_words = ["good", "great", "excellent", "best", "positive", "like", "love", "prefer"]
        negative_words = ["bad", "poor", "worst", "negative", "dislike", "hate", "avoid", "terrible"]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _extract_keywords(self, doc) -> List[str]:
        """
        Extract keywords from the document.
        
        Args:
            doc: spaCy document
            
        Returns:
            List[str]: List of keywords
        """
        # Extract nouns, verbs, and adjectives as keywords
        keywords = []
        
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
                keywords.append(token.lemma_)
            elif token.pos_ in ["VERB", "ADJ"] and not token.is_stop:
                keywords.append(token.lemma_)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = [kw for kw in keywords if not (kw in seen or seen.add(kw))]
        
        return unique_keywords
    
    def _determine_answer_strategy(self, question_type: str, sentiment: str, keywords: List[str]) -> str:
        """
        Determine the strategy for answering the question.
        
        Args:
            question_type: Type of question
            sentiment: Sentiment of the question
            keywords: Keywords from the question
            
        Returns:
            str: Answer strategy
        """
        # Define strategies based on question type
        if question_type == "yes_no":
            # For yes/no questions, often positive is preferred in evaluations
            return "prefer_yes"
        
        elif question_type == "selection":
            # For selection questions, use keyword matching
            return "keyword_match"
        
        elif question_type in ["factual", "temporal", "spatial", "person"]:
            # For factual questions, look for specific information
            return "specific_info"
        
        elif question_type == "reason":
            # For reason questions, provide explanations
            return "explanation"
        
        else:
            # Default strategy
            return "balanced"
    
    def _determine_expected_answer_type(self, doc, question_type: str) -> str:
        """
        Determine the expected type of answer.
        
        Args:
            doc: spaCy document
            question_type: Type of question
            
        Returns:
            str: Expected answer type
        """
        if question_type == "yes_no":
            return "boolean"
        
        elif question_type == "selection":
            return "option"
        
        elif question_type == "temporal":
            return "date_time"
        
        elif question_type == "spatial":
            return "location"
        
        elif question_type == "person":
            return "entity"
        
        # Default to text
        return "text"
    
    def _score_option(self, option: str, question: str, analysis: Dict[str, Any]) -> float:
        """
        Score an option based on the question analysis.
        
        Args:
            option: Option text
            question: Question text
            analysis: Question analysis results
            
        Returns:
            float: Score between 0 and 1
        """
        score = 0.5  # Start with a neutral score
        
        # Process the option with spaCy
        option_doc = self.nlp(option)
        
        # Get keywords from the option
        option_keywords = [token.lemma_ for token in option_doc if token.pos_ in ["NOUN", "VERB", "ADJ", "PROPN"] and not token.is_stop]
        
        # Strategy-based scoring
        if analysis["answer_strategy"] == "prefer_yes":
            # For yes/no questions, prefer positive answers
            if any(word in option.lower() for word in ["yes", "agree", "strongly agree", "definitely", "absolutely"]):
                score += 0.3
            elif any(word in option.lower() for word in ["no", "disagree", "strongly disagree", "definitely not"]):
                score -= 0.2
        
        elif analysis["answer_strategy"] == "keyword_match":
            # Count matching keywords
            matches = sum(1 for kw in analysis["keywords"] if kw in option_keywords)
            if matches > 0:
                score += 0.2 * (matches / len(analysis["keywords"]))
        
        # Sentiment matching
        option_sentiment = self._analyze_sentiment(option)
        if option_sentiment == analysis["sentiment"]:
            score += 0.1
        elif (analysis["sentiment"] == "positive" and option_sentiment == "negative") or \
             (analysis["sentiment"] == "negative" and option_sentiment == "positive"):
            score -= 0.1
        
        # Length preference (in evaluations, middle-length answers are often good)
        words = len(option.split())
        if 5 <= words <= 25:  # Prefer medium-length responses
            score += 0.05
        
        # Adjust the score to be between 0 and 1
        return max(0.0, min(1.0, score))