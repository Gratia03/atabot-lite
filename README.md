# Atabot-Lite

## Description

Atabot-Lite is a flexible and powerful chatbot backend built with FastAPI. It leverages Large Language Models (LLMs) via the Poe API and semantic search capabilities using the Voyage AI API to deliver intelligent and context-aware responses. The chatbot's knowledge base is easily configurable through a single `data.json` file, making it adaptable for various business needs.

## Features

  - **FastAPI Backend**: A modern, fast (high-performance) web framework for building APIs with Python.
  - **LLM Integration**: Connects with the Poe API to generate human-like text responses.
  - **Semantic Search**: Utilizes Voyage AI to create embeddings and find the most relevant information (e.g., FAQs) based on query similarity.
  - **Streaming Responses**: Supports real-time, word-by-word responses for a more interactive user experience.
  - **Session Management**: Maintains conversation history for each user session.
  - **Configurable Knowledge Base**: All company data, including services, FAQs, and contact information, is managed through a simple `data.json` file.
  - **Customizable Bot Persona**: Easily define the chatbot's name, personality, and response rules in the configuration.
  - **RAG (Retrieval-Augmented Generation)**: The chatbot finds relevant information from its knowledge base before generating a response, leading to more accurate and helpful answers.

## How It Works

1.  A user sends a message to one of the API endpoints.
2.  The `ChatbotService` processes the incoming request.
3.  The service uses the `EmbeddingService` to convert the user's query into a vector embedding.
4.  This embedding is compared against pre-calculated embeddings of the FAQs from `data.json` to find the most semantically similar questions and answers.
5.  The service also searches for keywords related to company information, services, and contact details within the query.
6.  A detailed prompt is constructed, including the bot's persona, rules, the retrieved information (FAQs, services, etc.), the conversation history, and the user's latest query.
7.  This comprehensive prompt is sent to the `LLMService`, which forwards it to the Poe API.
8.  The LLM generates a response based on the provided context.
9.  The `ChatbotService` sends this response back to the user, either as a complete message or as a real-time stream.

## Technologies Used

  - Python
  - FastAPI
  - Pydantic
  - Poe API (for LLM)
  - Voyage AI API (for embeddings)
  - Uvicorn (for serving the application)

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/GratiaManullang03/atabot-lite-v2
    cd atabot-lite-v2
    ```

2.  **Install dependencies:**
    (It is recommended to use a virtual environment)

    ```bash
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file:**
    Create a `.env` file in the root directory and add your API keys and configuration. See the [Configuration](https://www.google.com/search?q=%23configuration) section for details.

4.  **Create the `data.json` file:**
    Create a `data.json` file in the root directory. This file will serve as the chatbot's knowledge base. See the structure below:

    ```json
    {
      "bot_config": {
        "name": "Atabot",
        "personality": "helpful and friendly",
        "language": "Indonesian",
        "max_response_length": 500,
        "temperature": 0.7,
        "rules": [
          "Be polite.",
          "Do not answer questions outside the provided context."
        ]
      },
      "company_data": {
        "company_name": "Your Company Name",
        "description": "A brief description of your company.",
        "services": [
          {
            "name": "Service A",
            "description": "Description of Service A.",
            "features": ["Feature 1", "Feature 2"],
            "price": "$100"
          }
        ],
        "faq": [
          {
            "question": "What is Service A?",
            "answer": "Service A is a service that does..."
          }
        ],
        "contacts": {
          "email": "contact@yourcompany.com",
          "phone": "+123456789"
        }
      }
    }
    ```

5.  **Run the application:**

    ```bash
    uvicorn app.main:app --reload
    ```

    The application will be available at `http://127.0.0.1:8000`.

## Configuration

The following environment variables should be set in your `.env` file:

  - `POE_API_KEY`: Your API key for the Poe service.
  - `POE_MODEL`: The model to use, e.g., "ChatGPT-3.5-Turbo".
  - `VOYAGE_API_KEY`: (Optional) Your API key for the Voyage AI service. If not provided, the embedding functionality and semantic search will be disabled, and the chatbot will fall back to keyword matching.
  - `VOYAGE_MODEL`: The Voyage AI model to use, e.g., "voyage-3.5-lite".

## API Endpoints

The API documentation is available at `/docs` when the application is running.

  - `POST /api/v1/chat/message`
      - Sends a message to the chatbot and receives a complete response.
  - `POST /api/v1/chat/message/stream`
      - Sends a message and receives a streaming response (text/event-stream).
  - `GET /api/v1/chat/session/create`
      - Creates a new chat session and returns a `session_id`.
  - `GET /api/v1/chat/history/{session_id}`
      - Retrieves the conversation history for a given session.
  - `DELETE /api/v1/chat/session/{session_id}`
      - Clears the history for a given session.
  - `POST /api/v1/chat/reload`
      - Reloads the data from `data.json` and re-initializes the FAQ embeddings without restarting the server.
  - `GET /api/v1/health`
      - A health check endpoint to verify that the service is running.