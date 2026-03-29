# Chat Conversation

Note: _This is purely the output of the chat conversation and does not contain any raw data, codebase snippets, etc. used to generate the output._

### User Input

Review the Python code in this project against the spec in SPEC.md.
For each item in the acceptance criteria, check whether the code
actually implements it correctly. Also check for:
- Bugs or logic errors
- Missing error handling
- Code quality issues (unclear naming, repeated code, etc.)
- Security concerns (e.g., unsafe file handling)

Format your review as a numbered list of findings, each marked as
[PASS], [FAIL], or [WARN]. Be specific — reference file names and
line numbers.

*Viewed [spec.md](file:///home/nolangormley/Documents/15-113-HW8/spec.md) *

*Viewed [main.py](file:///home/nolangormley/Documents/15-113-HW8/main.py) *

*Listed directory [15-113-HW8](file:///home/nolangormley/Documents/15-113-HW8) *

*Viewed [README.md](file:///home/nolangormley/Documents/15-113-HW8/README.md) *

### Planner Response

Here is my comprehensive review of `main.py` against the acceptance criteria outlined in `SPEC.md`, along with additional findings regarding bugs, security, and code quality.

### 1. Documentation & Requirements
* **[PASS]** **"The app will be very well documented and have a comprehensive README.md"** - `README.md` exists and covers features, prerequisites, and how to run it. 
* **[PASS]** **"The app will be written in Python 3"** - Written cleanly in Python 3.

### 2. User Interface
* **[PASS]** **"The app will be run from the command line and be displayed in a classic ascii application style, add some ascii art for some flair."** - Executes properly via CLI. `print_welcome_art()`, `print_correct_art()`, and `print_incorrect_art()` clearly provide the flair requested.
* **[FAIL]** **"The terminal screen will then move to a new screen that will display the categories of the questions that are available to be answered."** - *Logic Error:* The app logs the user in successfully (lines `119-136`), but it never calls `clear_screen()` before displaying the categories list (line `189`). The categories simply print natively below the login/registration output without moving to a new clean screen.

### 3. Data & File Handling
* **[PASS]** **"The app will read questions from a JSON file, questions.json... require this file... return an error if this file is not found"** - Checks for existence and exits gracefully if missing (lines `68-75`).
* **[PASS]** **"question ids should always be unique, prompt the user and offer to fix if it is found to collide"** - Scans the IDs and accurately auto-fixes duplicates by incrementing past the `max_id` when the user types 'y' (lines `89-106`).
* **[WARN]** **I/O Sub-optimization:** In `record_answer()` (lines `138-148`), the app loads a potentially massive list from `answers.json` into memory, appends one dictionary, and rewrites the entire file. If the file gets large, this results in O(N^2) time complexity. Using an append-only structure (like JSON Line formatting) would be vastly safer and more performant.

### 4. Authentication
* **[PASS]** **"The app will first ask for your username and password... If the user does not exist, it will create a new account... ask the user to enter their password twice... If existing, it will log the user in"** - The login and registration flows in `authenticate_user()` completely implement this flow.
* **[FAIL]** **Security Concern:** `hash_password()` (line `48`) uses raw `SHA-256` formatting with no salt formatting (`hashlib.sha256(password.encode()).hexdigest()`). This is highly insecure against dictionary/rainbow table attacks. A modern hashing library like `bcrypt` or `hashlib.pbkdf2_hmac` should be utilized.

### 5. Quiz Logic & Question Delivery
* **[PASS]** **"The app will present questions to the user one at a time... accept the follow question types (multiple_choice, true_false, short_answer)"** - Handled elegantly via looping and branching question types (lines `234-247`).
* **[FAIL]** **Bug / Logic Error:** When generating the pool of available questions, `get_next_question()` (line `165`) checks `q.get("category") in categories`. If a question in the JSON lacks a "category" key entirely, `q.get("category")` evaluates to `None`. Because "Uncategorized" defaults to a string elsewhere in the code, `None` won't map successfully to the user's selected "Uncategorized" category. Thus, genuinely uncategorized questions will be silently dropped from the selection pool.
  * **Fix:** Change to `q.get("category", "Uncategorized") in categories`

### 6. Answer Tracking
* **[PASS]** **"The app will record the answer which can be related to the user, but obscured for security reasons, in a json file, answers.json"** - Saves correctness, Question ID, and user hash properly. 
* **[FAIL]** **Security Concern:** `hash_username()` (line `52`) obscures user identity iteratively with raw `MD5`. MD5 is cryptographically deprecated. Additionally, hashing a predictable short string like a username without a salt means that anyone with access to `answers.json` and a list of usernames can trivially recreate the hashes to de-anonymize the data.
* **[PASS]** **"the app's algorithm will then use this feedback to adjust the difficulty of the questions it presents to the user"** - `calculate_next_difficulty()` dynamically and logically bumps the intended target difficulty around depending on user's inputted preference (lines `150-161`).

### 7. Code Quality Issues
* **[WARN]** **Dangerous Error Catching:** In `load_json()` (line `60`), using a bare `except:` is a notorious Python anti-pattern. This sweeps up critical exceptions like `KeyboardInterrupt` (Ctrl+C) and obfuscates `json.JSONDecodeError` details. It should be constrained strictly to file and JSON parsing exceptions.