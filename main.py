import json
import os
import sys
import getpass
import hashlib
import random
import time
import shutil
import textwrap

QUESTIONS_FILE = 'questions.json'
USERS_FILE = 'users.json'
ANSWERS_FILE = 'answers.json'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_tui(title, body_lines, prompt=None, is_password=False, subtitle=""):
    """
    Renders a full-screen Terminal User Interface (TUI).
    """
    clear_screen()
    cols, lines = shutil.get_terminal_size((80, 24))
    
    # Ensure minimum sizes to prevent crashing on tiny terminals
    cols = max(40, cols)
    lines = max(15, lines)
    
    # Top Border
    print("+" + "-" * (cols - 2) + "+")
    
    # Title
    title_str = f" {title} "
    print(f"|{title_str.center(cols - 2)}|")
    
    if subtitle:
        subtitle_str = f" {subtitle} "
        print(f"|{subtitle_str.center(cols - 2)}|")
        
    print("+" + "-" * (cols - 2) + "+")
    
    # Process Body
    wrapped_body = []
    if isinstance(body_lines, str):
        body_lines = body_lines.split("\n")
        
    for line in body_lines:
        # Strip trailing newlines but preserve leading spaces (crucial for ASCII art)
        clean_line = line.rstrip('\r\n')
        if len(clean_line) < cols - 6:
            wrapped_body.append(clean_line)
        else:
            # Wrap long text logically
            wrapped = textwrap.wrap(clean_line, width=cols-6, drop_whitespace=False)
            if not wrapped:
                wrapped_body.append("")
            else:
                wrapped_body.extend(wrapped)
            
    # Calculate available vertical space in the box
    header_lines = 4 if subtitle else 3
    footer_lines = 2
    available_lines = lines - header_lines - footer_lines - 1 # 1 extra padding line
    
    if len(wrapped_body) > available_lines:
        wrapped_body = wrapped_body[:available_lines]
        
    # Center vertically
    top_pad = max(0, (available_lines - len(wrapped_body)) // 2)
    bottom_pad = max(0, available_lines - len(wrapped_body) - top_pad)
    
    for _ in range(top_pad):
        print("|" + " " * (cols - 2) + "|")
        
    # Block-center horizontally for cleaner aesthetics, preserving inner alignment
    max_line_len = max([len(line) for line in wrapped_body] + [0])
    max_line_len = min(cols - 4, max_line_len)
    
    block_left_margin = max(2, (cols - 2 - max_line_len) // 2)

    for line in wrapped_body:
        margin = " " * block_left_margin
        content = line[:cols - 2 - block_left_margin]
        padding = " " * max(0, cols - 2 - len(margin) - len(content))
        print(f"|{margin}{content}{padding}|")
        
    for _ in range(bottom_pad):
        print("|" + " " * (cols - 2) + "|")
        
    # Footer border
    print("+" + "-" * (cols - 2) + "+")
    
    # Prompt input
    if prompt is not None:
        # Align prompt with the text block
        pad = " " * block_left_margin
        if is_password:
            return getpass.getpass(f"{pad}{prompt} ")
        else:
            return input(f"{pad}{prompt} ")
    return None

def print_welcome_art():
    return [
        "  ____        _       ___  _   _ ___ _____ ",
        " |  _ \\ _   _(_)____ |_ _| \\ | |_ _|_   _|",
        " | |_) | | | | |_  /  | ||  \\| || |  | |  ",
        " |  __/| |_| | |/ /   | || |\\  || |  | |  ",
        " |_|    \\__,_|_/___| |___|_| \\_|___| |_|  "
    ]

def play_animation(anim_type, subtitle, bonus_msg):
    cols, lines = shutil.get_terminal_size((80, 24))
    cols = max(40, cols)
    lines = max(15, lines)
    box_width = cols - 6
    box_height = lines - 4 - 2 - 1 
    
    canvas_height = max(5, box_height - 3)
    frames_count = 15
    body_lines = []
    
    if anim_type == "confetti":
        chars = ['*', '.', '\'', '"', 'o', '0', '+', 'x']
        particles = [[random.randint(0, box_width-1), random.randint(-canvas_height, 0), random.choice(chars)] for _ in range(box_width * canvas_height // 15)]
        
        for _ in range(frames_count):
            for p in particles:
                p[1] += random.randint(1, 2)
                p[0] += random.choice([-1, 0, 1])
                
            frame = [[" " for _ in range(box_width)] for _ in range(canvas_height)]
            for p in particles:
                x, y, c = p
                if 0 <= y < canvas_height and 0 <= x < box_width:
                    frame[int(y)][int(x)] = c
                    
            body_lines = ["".join(row) for row in frame]
            body_lines.extend(["", bonus_msg])
            draw_tui("RESULT", body_lines, subtitle=subtitle, prompt=None)
            time.sleep(0.08)
            
    elif anim_type == "x":
        cx = box_width / 2.0
        cy = canvas_height / 2.0
        for i in range(frames_count):
            progress = (i + 1) / frames_count
            frame = [[" " for _ in range(box_width)] for _ in range(canvas_height)]
            for y in range(canvas_height):
                for x in range(box_width):
                    nx = (x - cx) / cx if cx else 0
                    ny = (y - cy) / cy if cy else 0
                    dist = max(abs(nx), abs(ny))
                    if dist <= progress:
                        if abs(nx - ny) < 0.15 or abs(nx + ny) < 0.15:
                            frame[y][x] = "X"
            
            body_lines = ["".join(row) for row in frame]
            body_lines.extend(["", bonus_msg])
            draw_tui("RESULT", body_lines, subtitle=subtitle, prompt=None)
            time.sleep(0.08)
            
    draw_tui("RESULT", body_lines, subtitle=subtitle, prompt="Press enter to continue...")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def hash_username(username):
    # Used to obscure user identity in answers.json
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
        draw_tui("FATAL ERROR", [f"Required file '{QUESTIONS_FILE}' not found."], prompt="Press enter to exit...")
        sys.exit(1)
        
    data = load_json(QUESTIONS_FILE)
    if not data or 'questions' not in data:
        draw_tui("FATAL ERROR", [f"Invalid format or parsing error in '{QUESTIONS_FILE}'."], prompt="Press enter to exit...")
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
        msg = [
            "Warning: Duplicate question IDs found in questions.json.", 
            "", 
            f"- {len(collisions)} collision(s) detected.",
            "",
            "Would you like to automatically fix the collisions",
            "by reassigning unique IDs sequentially?"
        ]
        choice = draw_tui("COLLISION DETECTED", msg, prompt="Auto-fix collisions? (y/n): ")
        if choice and choice.strip().lower() == 'y':
            max_id = max((q for q in ids if isinstance(q, int)), default=0)
            for q in questions:
                if q in collisions:
                    max_id += 1
                    q['question_id'] = max_id
                    collisions.remove(q)
            save_json(data, QUESTIONS_FILE)
            draw_tui("SUCCESS", ["Collisions successfully fixed and saved to questions.json."], prompt="Press enter to continue...")
        else:
            draw_tui("ABORTED", ["Please fix the collisions manually and restart."], prompt="Press enter to exit...")
            sys.exit(1)
            
    return data['questions']

def authenticate_user():
    users_data = load_json(USERS_FILE)
    if users_data is None:
        users_data = {}
        
    username = ""
    while not username:
        username = draw_tui("LOGIN / REGISTER", ["Welcome to the Quiz App!", "Please identify yourself."], prompt="Username: ")
        if username:
            username = username.strip()

    if username in users_data:
        # Existing user
        while True:
            password = draw_tui("LOGIN", [f"Welcome back, {username}! Please enter your password."], prompt="Password: ", is_password=True)
            hashed = hash_password(password)
            if users_data[username]['password'] == hashed:
                draw_tui("SUCCESS", [f"Login successful. Welcome back, {username}!"], prompt="Press enter to continue...")
                return username
            else:
                draw_tui("ERROR", ["Incorrect password.", "Please try again."], prompt="Press enter to continue...")
    else:
        # New user
        while True:
            password = draw_tui("REGISTER", [f"User '{username}' not found.", "Let's create a new account for you.", ""], prompt="Enter new password: ", is_password=True)
            if not password:
                continue
            confirm = draw_tui("REGISTER", [f"User '{username}' not found.", "Let's create a new account for you.", ""], prompt="Confirm new password: ", is_password=True)
            
            if password == confirm:
                users_data[username] = {"password": hash_password(password)}
                save_json(users_data, USERS_FILE)
                draw_tui("SUCCESS", [f"Account securely created for {username}!"], prompt="Press enter to continue...")
                return username
            else:
                draw_tui("ERROR", ["Passwords do not match.", "Please try again."], prompt="Press enter to continue...")

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
    # Filter by category and unseen. Default to 'Uncategorized' if key missing
    pool = [q for q in questions if q.get("category", "Uncategorized") in categories and q.get("question_id") not in answered_ids]
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
    # Show welcome art gracefully
    draw_tui("QUIZ APP", print_welcome_art(), prompt="Press enter to begin!")
    
    questions = check_questions()
    username = authenticate_user()
    
    # Get unique categories (safely defaulting to "Uncategorized")
    all_categories = sorted(list(set(q.get("category", "Uncategorized") for q in questions)))
    
    cat_msg = ["Please select the categories you want to study:", ""]
    for i, cat in enumerate(all_categories):
        cat_msg.append(f"  {i+1}. {cat}")
    cat_msg.append("")
    cat_msg.append(f"  {len(all_categories) + 1}. All Categories")
    
    sel = draw_tui("CATEGORY SELECTION", cat_msg, prompt="Enter numbers (comma-separated): ")
    if not sel: 
        sel = ""
        
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
        draw_tui("CAUTION", ["No valid categories selected.", "Defaulting to studying ALL categories."], prompt="Press enter to continue...")
        selected_categories = all_categories
        
    current_difficulty = "medium"
    answered_ids = set()
    correct_count = 0
    incorrect_count = 0
    
    while True:
        # Score header string
        subtitle = f"Score: {correct_count} Correct | {incorrect_count} Incorrect | Diff: {current_difficulty.upper()}"
        
        q = get_next_question(questions, selected_categories, current_difficulty, answered_ids)
        if not q:
            draw_tui("QUIZ COMPLETE", ["No more questions available in the selected categories!", "You have exhausted the study pool."], subtitle=subtitle, prompt="Press enter to exit...")
            break
            
        qid = q.get("question_id")
        answered_ids.add(qid)
        
        q_text = f"Category: {q.get('category', 'Uncategorized')}  |  Difficulty: {q.get('difficulty', 'medium')}\n\n"
        q_text += q["question"] + "\n\n"
        
        q_type = q.get("type", "short_answer")
        ans_given = ""
        
        body_lines = q_text.split('\n')
        prompt_text = "Your answer: "
        
        # Display rendering logic based on type
        if q_type == "multiple_choice":
            options = q.get("options", [])
            for i, opt in enumerate(options):
                body_lines.append(f" {i+1}) {opt}")
            prompt_text = "Your answer (number): "
            
            raw_ans = draw_tui("QUIZ SESSION", body_lines, subtitle=subtitle, prompt=prompt_text)
            if raw_ans and raw_ans.strip().isdigit() and 1 <= int(raw_ans.strip()) <= len(options):
                ans_given = options[int(raw_ans.strip()) - 1]
        elif q_type == "true_false":
            prompt_text = "True or False? "
            raw_ans = draw_tui("QUIZ SESSION", body_lines, subtitle=subtitle, prompt=prompt_text)
            ans_given = raw_ans.strip().lower() if raw_ans else ""
        else:
            raw_ans = draw_tui("QUIZ SESSION", body_lines, subtitle=subtitle, prompt=prompt_text)
            ans_given = raw_ans.strip() if raw_ans else ""
            
        # Evaluation Logic
        correct_ans = str(q["answer"]).strip().lower()
        is_correct = (str(ans_given).lower() == correct_ans)
        
        if is_correct:
            correct_count += 1
            subt = f"Score: {correct_count} Correct | {incorrect_count} Incorrect"
            play_animation("confetti", subt, "CORRECT! Great job.")
        else:
            incorrect_count += 1
            subt = f"Score: {correct_count} Correct | {incorrect_count} Incorrect"
            play_animation("x", subt, f"INCORRECT. The correct answer was: {q['answer']}")
            
        record_answer(username, qid, is_correct)
        
        # Feedback Flow
        feedback = ""
        while feedback not in ['easy', 'medium', 'hard', 'quit']:
            feedback_raw = draw_tui("FEEDBACK", ["How was this question?", "(easy, medium, hard) or 'quit'"], subtitle=subtitle, prompt="Feedback: ")
            if feedback_raw:
                feedback = feedback_raw.strip().lower()
            
        if feedback == 'quit':
            break
            
        current_difficulty = calculate_next_difficulty(current_difficulty, feedback)
        
    final_score_msg = [
        "--- Session Complete ---",
        "",
        f"Final Score: {correct_count} Correct / {incorrect_count} Incorrect",
        "",
        "Thanks for studying with Quiz App!"
    ]
    draw_tui("FINISHED", final_score_msg, prompt="Press enter to exit to terminal...")

if __name__ == "__main__":
    main()
