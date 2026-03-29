# Quiz Application Specification

This is an app that will deliver provided questions to a user and record their answers. Its intended use is for studying purposes.

- The app will be very well documented and have a comprehensive README.md
- The app will be written in Python 3
- The app will be run from the command line and be displayed in a classic ascii application style, add some ascii art for some flair.
- The app will read questions from a JSON file, questions.json
    - the app will require this file in order to run
    - the app will return an error if this file is not found
    - the file should be formated in the same way that ./questions.json is formated, but can obviously have different questions and categories
    - question ids should always be unique, prompt the user and offer to fix if it is found to collide with another question id
- The app will first ask for your username and password, which will attach to your account for this app
    - If the user does not exist, it will create a new account for the user
        - The user will be asked to enter their password twice to confirm it
        - If the passwords do not match, it will ask the user to enter their password again
        - If the passwords match, it will create the user account
        - The user account should be saved in a json file, users.json with a hashed password
            - if this file does not exist, create it
    - If the user exists, it will log the user in
- The terminal screen will then move to a new screen that will display the categories of the questions that are available to be answered.
    - The user will be able to select one or more categories of questions to answer.
- The app will present questions to the user one at a time.
- The app will accept the follow question types
    - multiple choice: multiple_choice
    - true false: true_false
    - short answer: short_answer
- once the question is answered
    - The app will record the answer which can be related to the user, but obscured for security reasons, in a json file, answers.json
        - if this file does not exist, create it
        - the app will add the question id and whether or not the user got it right
    - the app will tell the user if they were right or wrong
    - The app will then ask for feedback on the question (e.g. was this question easy, medium, or hard?)
    - the app's algorithm will then use this feedback to adjust the difficulty of the questions it presents to the user
- the app will show how many questions the user has answered correctly and incorrectly
- create ascii art for correct and incorrect answers, make it over the top and fun
    - Confetti for wins
    - a giant X for incorrect answers
    
