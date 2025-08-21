import logging
import requests
import os
from transformers import pipeline
from typing import Dict, Any
import json

logger = logging.getLogger("webtapi.ai_enhancer")

class AIEnhancer:
    def __init__(self):
        self.summarizer = None
        self.question_answerer = None
        self.init_models()
    
    def init_models(self):
        """Initialize AI models"""
        try:
            # Use smaller models that can run on CPU
            self.summarizer = pipeline(
                "summarization", 
                model="sshleifer/distilbart-cnn-12-6",
                tokenizer="sshleifer/distilbart-cnn-12-6"
            )
            self.question_answerer = pipeline(
                "question-answering",
                model="distilbert-base-cased-distilled-squad"
            )
            logger.info("AI models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {str(e)}")
            self.summarizer = None
            self.question_answerer = None
    
    def generate_natural_summary(self, data: Dict[str, Any], query: str) -> str:
        """Generate natural language summary from extracted data"""
        try:
            # Convert data to text for summarization
            text_content = self._extract_text_content(data)
            
            if self.summarizer and text_content:
                # Generate summary
                summary = self.summarizer(
                    text_content,
                    max_length=150,
                    min_length=30,
                    do_sample=False
                )[0]['summary_text']
                
                return f"Based on your query '{query}', here's what I found:\n\n{summary}"
            
            # Fallback if AI is not available
            return self._generate_fallback_summary(data, query)
            
        except Exception as e:
            logger.error(f"Natural language generation failed: {str(e)}")
            return self._generate_fallback_summary(data, query)
    
    def answer_question(self, data: Dict[str, Any], question: str) -> str:
        """Answer specific questions about the extracted data"""
        try:
            if not self.question_answerer:
                return "AI question answering is not available at the moment."
            
            context = self._extract_text_content(data)
            
            if not context:
                return "I couldn't find enough information to answer your question."
            
            result = self.question_answerer(question=question, context=context)
            return result['answer']
            
        except Exception as e:
            logger.error(f"Question answering failed: {str(e)}")
            return "I encountered an error while trying to answer your question."
    
    def _extract_text_content(self, data: Dict[str, Any]) -> str:
        """Extract text content from structured data"""
        text_parts = []
        
        if "content" in data:
            content = data["content"]
            
            # Extract article text
            if "article" in content:
                article = content["article"]
                text_parts.append(article.get("title", ""))
                text_parts.append(article.get("content", ""))
            
            # Extract text from other content types
            for key, value in content.items():
                if key != "article" and isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            text_parts.append(item)
                        elif isinstance(item, dict):
                            for k, v in item.items():
                                if isinstance(v, str):
                                    text_parts.append(v)
        
        return " ".join(text_parts)
    
    def _generate_fallback_summary(self, data: Dict[str, Any], query: str) -> str:
        """Generate a fallback summary without AI"""
        content = data.get("content", {})
        summary_parts = [f"Based on your query '{query}', I found:"]
        
        if "article" in content:
            article = content["article"]
            title = article.get("title", "an article")
            summary_parts.append(f"- An article titled '{title}'")
        
        if "images" in content:
            image_count = len(content["images"])
            summary_parts.append(f"- {image_count} images")
        
        if "tables" in content:
            table_count = len(content["tables"])
            summary_parts.append(f"- {table_count} tables")
        
        if "links" in content:
            link_count = len(content["links"])
            summary_parts.append(f"- {link_count} links")
        
        summary_parts.append("\nThe structured data is available in JSON format for technical use.")
        return "\n".join(summary_parts)

# Global instance
ai_enhancer = AIEnhancer()