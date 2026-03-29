# CLI Quiz Application

A Python 3 terminal-based quiz application that delivers questions to users, records their answers, and adjusts difficulty based on user feedback.

## Features
- **User Authentication**: Secure user registration and login with hashed passwords.
- **Dynamic Question Loading**: Loads questions and categories dynamically from `questions.json`.
- **Automatic Question ID Collision Resolution**: Detects duplicate question IDs and offers to automatically fix them.
- **Category Selection**: Choose one or multiple categories to study.
- **Multiple Question Types**: Supports multiple choice, true/false, and short answer formats.
- **Answer Tracking**: Securely records user performance in `answers.json` with anonymized user IDs.
- **Difficulty Adjustment**: Asks for user feedback (easy/medium/hard) on each question and adjusts the upcoming question difficulties accordingly.
- **Fun ASCII Art**: Displays over-the-top ASCII art (confetti for correct answers, a giant X for incorrect ones) for a classic terminal feel.
- **Score Tracking**: Displays real-time session statistics (correct/incorrect counts).

## Requirements
- Python 3.6+
- Built-in libraries used: `json`, `os`, `sys`, `getpass`, `hashlib`, `random`

## Usage

1. Ensure `questions.json` is located in the same directory.
2. Run the application:
   ```bash
   python3 main.py
   ```
3. Follow the on-screen prompts to log in or create an account.
4. Select your categories and begin the quiz!
