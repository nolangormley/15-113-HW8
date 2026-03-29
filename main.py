import json
import os
import sys
import getpass
import hashlib
import random
import time

QUESTIONS_FILE = 'questions.json'
USERS_FILE = 'users.json'
ANSWERS_FILE = 'answers.json'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_welcome_art():
    print("""
  ____        _       ___  _   _ ___ _____ 
 |  _ \\ _   _(_)____ |_ _| \\ | |_ _|_   _|
 | |_) | | | | |_  /  | ||  \\| || |  | |  
 |  __/| |_| | |/ /   | || |\\  || |  | |  
 |_|    \\__,_|_/___| |___|_| \\_|___| |_|  
                                          
    """)

def print_correct_art():
    print("""
    \\ | /
 '-.     .-'
--. *WIN* .--
 .-'     '-.
    / | \\
  *CONFETTI*
    """)

def print_incorrect_art():
    print("""
   \\      /
    \\    /
     \\  /
      ><
     /  \\
    /    \\
   /      \\
    """)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def hash_username(username):
    # Used to obscure user identity in answers.json for security
    return hashlib.md5(username.encode()).hexdigest()

def load_json(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return None

def save_json(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def check_questions():
    if not os.path.exists(QUESTIONS_FILE):
        print(f"Error: Required file '{QUESTIONS_FILE}' not found.")
        sys.exit(1)
        
    data = load_json(QUESTIONS_FILE)
    if not data or 'questions' not in data:
        print(f"Error: Invalid format in '{QUESTIONS_FILE}'.")
        sys.exit(1)
        
    questions = data['questions']
    ids = set()
    collisions = []
    
    for q in questions:
        qid = q.get('question_id')
        if qid in ids:
            collisions.append(q)
        else:
            if qid is not None:
                ids.add(qid)
                
    if collisions:
        print("Warning: Duplicate question IDs found in questions.json.")
        choice = input("Would you like to automatically fix the collisions by reassigning unique IDs? (y/n): ")
        if choice.lower() == 'y':
            max_id = max((q for q in ids if isinstance(q, int)), default=0)
            for q in questions:
                # To be completely safe and just fix the collisions
                if q in collisions:
                    max_id += 1
                    q['question_id'] = max_id
                    collisions.remove(q) # Just update in place
            save_json(data, QUESTIONS_FILE)
            print("Collisions fixed and saved to questions.json.\n")
        else:
            print("Please fix the collisions manually and restart.")
            sys.exit(1)
            
    return data['questions']

def authenticate_user():
    users_data = load_json(USERS_FILE)
    if users_data is None:
        users_data = {}
        
    username = input("Username: ")
    if username in users_data:
        # Existing user
        while True:
            password = getpass.getpass("Password: ")
            hashed = hash_password(password)
            if users_data[username]['password'] == hashed:
                print(f"Welcome back, {username}!")
                return username
            else:
                print("Incorrect password. Please try again.")
    else:
        # New user
        print("User not found. Creating a new account.")
        while True:
            password = getpass.getpass("Enter new password: ")
            confirm = getpass.getpass("Confirm new password: ")
            if password == confirm:
                users_data[username] = {"password": hash_password(password)}
                save_json(users_data, USERS_FILE)
                print(f"Account created for {username}!")
                return username
            else:
                print("Passwords do not match. Please try again.")

def record_answer(username, qid, is_correct):
    answers_data = load_json(ANSWERS_FILE)
    if answers_data is None:
        answers_data = []
        
    answers_data.append({
        "user_hash": hash_username(username),
        "question_id": qid,
        "correct": is_correct
    })
    save_json(answers_data, ANSWERS_FILE)

def calculate_next_difficulty(current, feedback):
    levels = ["easy", "medium", "hard"]
    idx = levels.index(current) if current in levels else 1
    
    if feedback == "easy":
        # If it was easy, make it harder
        idx = min(idx + 1, len(levels) - 1)
    elif feedback == "hard":
        # If it was hard, make it easier
        idx = max(idx - 1, 0)
    
    return levels[idx]

def get_next_question(questions, categories, current_difficulty, answered_ids):
    # Filter by category and unseen
    pool = [q for q in questions if q.get("category") in categories and q.get("question_id") not in answered_ids]
    if not pool:
        return None
    
    # Try to find one matching difficulty
    diff_pool = [q for q in pool if q.get("difficulty", "medium") == current_difficulty]
    
    if diff_pool:
        return random.choice(diff_pool)
    else:
        # If none match difficulty, just pick a random one
        return random.choice(pool)

def main():
    clear_screen()
    print_welcome_art()
    time.sleep(1)
    
    questions = check_questions()
    username = authenticate_user()
    
    # Get unique categories
    all_categories = sorted(list(set(q.get("category", "Uncategorized") for q in questions)))
    
    print("\n--- Available Categories ---")
    for i, cat in enumerate(all_categories):
        print(f"{i+1}. {cat}")
        
    print(f"{len(all_categories) + 1}. All Categories")
    
    sel = input("\nEnter the numbers of the categories you want to study (comma-separated): ")
    selected_indices = [v.strip() for v in sel.split(",")]
    
    selected_categories = []
    for idx_str in selected_indices:
        if idx_str.isdigit():
            idx = int(idx_str) - 1
            if idx == len(all_categories):
                selected_categories = all_categories
                break
            elif 0 <= idx < len(all_categories):
                selected_categories.append(all_categories[idx])
                
    if not selected_categories:
        print("No valid categories selected. Defaulting to all.")
        selected_categories = all_categories
        
    current_difficulty = "medium"
    answered_ids = set()
    correct_count = 0
    incorrect_count = 0
    
    while True:
        clear_screen()
        print(f"--- Quiz Session | Score: {correct_count} Correct / {incorrect_count} Incorrect ---")
        print(f"Selected Categories: {', '.join(selected_categories)}")
        print(f"Current Target Difficulty: {current_difficulty}\n")
        
        q = get_next_question(questions, selected_categories, current_difficulty, answered_ids)
        if not q:
            print("No more questions available in the selected categories!")
            break
            
        qid = q.get("question_id")
        answered_ids.add(qid)
        
        print(f"[{q.get('category')} - {q.get('difficulty', 'medium')}]")
        print(q["question"])
        
        q_type = q.get("type", "short_answer")
        ans_given = ""
        
        if q_type == "multiple_choice":
            options = q.get("options", [])
            for i, opt in enumerate(options):
                print(f"{i+1}) {opt}")
            idx_str = input("Your answer (number): ")
            if idx_str.isdigit() and 1 <= int(idx_str) <= len(options):
                ans_given = options[int(idx_str) - 1]
        elif q_type == "true_false":
            ans_given = input("True or False? ").strip().lower()
        else:
            ans_given = input("Your answer: ").strip().lower()
            
        correct_ans = str(q["answer"]).strip().lower()
        is_correct = (str(ans_given).lower() == correct_ans)
        
        if is_correct:
            correct_count += 1
            print_correct_art()
            print("Correct!")
        else:
            incorrect_count += 1
            print_incorrect_art()
            print(f"Incorrect. The correct answer was: {q['answer']}")
            
        record_answer(username, qid, is_correct)
        
        feedback = ""
        while feedback not in ['easy', 'medium', 'hard', 'quit']:
            feedback = input("\nHow was this question? (easy/medium/hard) or 'quit' to exit: ").strip().lower()
            
        if feedback == 'quit':
            break
            
        current_difficulty = calculate_next_difficulty(current_difficulty, feedback)
        
    print("\n--- Session Complete ---")
    print(f"Final Score: {correct_count} Correct / {incorrect_count} Incorrect")
    print("Thanks for studying!")

if __name__ == "__main__":
    main()
