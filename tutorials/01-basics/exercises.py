# -*- coding: utf-8 -*-
"""
Tutorial 01: Hands-On Exercises
================================

Complete these exercises to master AI agent basics!

Each exercise builds on what you learned in LEARNING_GUIDE.md
"""

import os
from dotenv import load_dotenv
from openai import OpenAI


# ============================================================================
# EXERCISE 1: Build a Chef Agent ⭐ START HERE
# ============================================================================

def exercise_1_chef_agent():
    """
    Exercise 1: Create a Chef Assistant Agent

    Goal: Modify the system prompt to create a cooking assistant

    Instructions:
    1. Complete the chef_prompt below
    2. Run this function
    3. Ask the agent cooking questions

    Example questions to try:
    - "How do I make pasta carbonara?"
    - "What's a good beginner recipe?"
    - "How do I dice an onion?"
    """

    # TODO: Complete this system prompt
    chef_prompt = """You are a professional chef assistant.

    TODO: Add personality traits here
    - You love cooking and sharing recipes
    - You are patient and encouraging
    - You provide clear step-by-step instructions

    TODO: Add what the assistant should do
    - Provide recipes with ingredients and steps
    - Give cooking tips and techniques
    - Suggest alternatives for ingredients
    """

    # Create and run the agent
    # TODO: Import SimpleAgent from simple_agent.py and use it here
    print("Exercise 1: Chef Agent")
    print("="*60)
    print("\nTODO: Complete the implementation!")
    print("\nHint: from simple_agent import SimpleAgent")
    print("Then: agent = SimpleAgent(system_prompt=chef_prompt)")
    print("Then: agent.run()")


# ============================================================================
# EXERCISE 2: Temperature Experimentation
# ============================================================================

def exercise_2_temperature():
    """
    Exercise 2: See how temperature affects responses

    Goal: Understand how temperature parameter changes AI behavior

    Instructions:
    1. Complete the code to test different temperatures
    2. Observe how responses vary
    3. Note which temperature is best for which use case
    """

    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # The same prompt, tested with different temperatures
    user_message = "Tell me a creative story idea about a robot"

    temperatures = [0.0, 0.5, 1.0, 1.5]

    print("\nExercise 2: Temperature Experiment")
    print("="*60)
    print(f"\nPrompt: {user_message}\n")

    for temp in temperatures:
        print(f"\n{'='*60}")
        print(f"Temperature: {temp}")
        print('='*60)

        # TODO: Complete this API call
        # Hint: Look at simple_agent.py lines 74-82
        messages = [
            {"role": "system", "content": "You are a creative writer."},
            {"role": "user", "content": user_message}
        ]

        # TODO: Make the API call with different temperatures
        # response = client.chat.completions.create(...)

        print("\nTODO: Add API call here with temperature =", temp)
        print("Hint: Copy the API call from simple_agent.py")
        print("Add parameter: temperature=temp")


# ============================================================================
# EXERCISE 3: Multi-Personality Agent
# ============================================================================

def exercise_3_personalities():
    """
    Exercise 3: Create agents with different personalities

    Goal: Learn how system prompts define agent behavior

    Instructions:
    1. Complete the personality prompts below
    2. Test each personality
    3. Ask the same question to each and compare responses
    """

    personalities = {
        "professional": """
        TODO: Write a system prompt for a professional business consultant
        - Formal tone
        - Uses business terminology
        - Provides strategic advice
        """,

        "friendly": """
        TODO: Write a system prompt for a friendly casual assistant
        - Informal, warm tone
        - Uses emojis (optional)
        - Relatable and encouraging
        """,

        "teacher": """
        TODO: Write a system prompt for a patient teacher
        - Explains concepts simply
        - Uses examples and analogies
        - Asks questions to check understanding
        """,

        "pirate": """
        You are a helpful AI assistant who speaks like a pirate.
        Use pirate slang like "ahoy", "matey", "arr".
        Still be helpful and accurate with information!
        """
    }

    print("\nExercise 3: Multi-Personality Agent")
    print("="*60)
    print("\nTODO: Complete the personality prompts above")
    print("Then uncomment the code below to test them\n")

    # TODO: Uncomment this after completing prompts
    # from simple_agent import SimpleAgent
    #
    # test_question = "What is Python programming?"
    #
    # for name, prompt in personalities.items():
    #     print(f"\n{'='*60}")
    #     print(f"Personality: {name}")
    #     print('='*60)
    #
    #     agent = SimpleAgent(system_prompt=prompt)
    #     response = agent.generate_response(test_question)
    #     print(f"\nResponse: {response}\n")


# ============================================================================
# EXERCISE 4: Build a Translation Agent
# ============================================================================

def exercise_4_translator():
    """
    Exercise 4: Create a language translation agent

    Goal: Build a specialized agent for a specific task

    Instructions:
    1. Complete the translator system prompt
    2. Implement the translation logic
    3. Test with different languages
    """

    translator_prompt = """
    TODO: Write a system prompt for a language translator

    The translator should:
    - Ask for target language if not specified
    - Show original text and translation
    - Provide pronunciation guide (optional)
    - Be accurate and helpful

    Example behavior:
    User: "Translate 'Hello' to Spanish"
    Agent: "Original: Hello
            Spanish: Hola
            Pronunciation: OH-lah"
    """

    print("\nExercise 4: Translation Agent")
    print("="*60)
    print("\nTODO: Complete the translator_prompt above")
    print("Then implement the agent below\n")

    # TODO: Implement the translator agent
    # from simple_agent import SimpleAgent
    # agent = SimpleAgent(system_prompt=translator_prompt)
    # agent.run()


# ============================================================================
# EXERCISE 5: Error Handling (Advanced)
# ============================================================================

def exercise_5_error_handling():
    """
    Exercise 5: Add better error handling

    Goal: Make agents more robust and user-friendly

    Instructions:
    1. Study the error handling in simple_agent.py
    2. Improve it with specific error messages
    3. Test edge cases
    """

    load_dotenv()

    # TODO: Add error handling for these scenarios:

    # 1. Missing API key
    # try:
    #     api_key = os.getenv("OPENAI_API_KEY")
    #     if not api_key:
    #         # TODO: Raise a helpful error
    #         pass
    # except ...:
    #     # TODO: Handle the error
    #     pass

    # 2. Invalid API key format
    # TODO: Check if API key starts with "sk-"

    # 3. Network errors
    # TODO: Handle connection timeout

    # 4. Rate limit errors
    # TODO: Handle "too many requests"

    print("\nExercise 5: Error Handling")
    print("="*60)
    print("\nTODO: Implement error handling for common scenarios")
    print("\nScenarios to handle:")
    print("1. Missing API key")
    print("2. Invalid API key format")
    print("3. Network connection errors")
    print("4. Rate limiting errors")


# ============================================================================
# EXERCISE 6: Build Your Own Agent (Capstone)
# ============================================================================

def exercise_6_custom_agent():
    """
    Exercise 6: Design and build your own unique agent

    Goal: Apply everything you've learned

    Ideas:
    - Code reviewer agent
    - Study buddy agent
    - Creative writing assistant
    - Fitness coach
    - Language learning partner
    - Math tutor
    - Career advisor

    Instructions:
    1. Choose an agent purpose
    2. Write a detailed system prompt
    3. Decide on appropriate temperature
    4. Add any special handling
    5. Test thoroughly!
    """

    print("\nExercise 6: Build Your Own Agent")
    print("="*60)
    print("\nYour turn to be creative!")
    print("\n1. Choose what kind of agent you want to build")
    print("2. Write a detailed system prompt")
    print("3. Implement special features")
    print("4. Test and refine")
    print("\nTODO: Build your dream agent here!")

    # TODO: Your code here!
    # my_agent_prompt = """..."""
    # agent = SimpleAgent(system_prompt=my_agent_prompt)
    # agent.run()


# ============================================================================
# Exercise Runner - Run all exercises
# ============================================================================

def run_all_exercises():
    """
    Run all exercises interactively.

    This helps you go through exercises one by one.
    """
    exercises = {
        "1": ("Chef Agent", exercise_1_chef_agent),
        "2": ("Temperature Experiment", exercise_2_temperature),
        "3": ("Multi-Personality", exercise_3_personalities),
        "4": ("Translator", exercise_4_translator),
        "5": ("Error Handling", exercise_5_error_handling),
        "6": ("Build Your Own", exercise_6_custom_agent),
    }

    print("\n" + "="*60)
    print(" Tutorial 01: Hands-On Exercises ".center(60, "="))
    print("="*60)
    print("\nChoose an exercise to work on:\n")

    for num, (name, _) in exercises.items():
        print(f"  {num}. {name}")

    print("\n  0. Exit")
    print("\n" + "="*60)

    while True:
        choice = input("\nEnter exercise number (or 0 to exit): ").strip()

        if choice == "0":
            print("\nGood luck with your learning! 🚀\n")
            break

        if choice in exercises:
            name, func = exercises[choice]
            print(f"\n{'='*60}")
            print(f" Exercise {choice}: {name} ".center(60, "="))
            print(f"{'='*60}\n")
            func()
            print("\n" + "="*60)
            print("Exercise complete! Try another or exit.")
        else:
            print("Invalid choice. Please enter a number from the list.")


# ============================================================================
# Solutions - Check these AFTER attempting exercises
# ============================================================================

def solution_1_chef_agent():
    """
    SOLUTION for Exercise 1: Chef Agent

    Only look at this after trying the exercise yourself!
    """
    from simple_agent import SimpleAgent

    chef_prompt = """You are a professional chef assistant named Chef Alex.

You are passionate about cooking and love helping people learn to cook.
You have 20 years of experience in Italian and French cuisine.

Your responses should:
- Be warm, encouraging, and enthusiastic about food
- Provide clear, step-by-step instructions
- Include helpful tips and techniques
- Suggest ingredient substitutions when asked
- Explain why certain techniques are used

When giving recipes:
- List all ingredients with measurements
- Provide numbered steps
- Include cooking times and temperatures
- Add pro tips and common mistakes to avoid

You believe anyone can learn to cook with patience and practice!"""

    agent = SimpleAgent(system_prompt=chef_prompt)
    agent.run()


def solution_2_temperature():
    """
    SOLUTION for Exercise 2: Temperature

    Only look at this after trying the exercise yourself!
    """
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    user_message = "Tell me a creative story idea about a robot"
    temperatures = [0.0, 0.5, 1.0, 1.5]

    print("\nSOLUTION: Temperature Experiment")
    print("="*60)
    print(f"\nPrompt: {user_message}\n")

    for temp in temperatures:
        print(f"\n{'='*60}")
        print(f"Temperature: {temp}")
        print('='*60)

        messages = [
            {"role": "system", "content": "You are a creative writer."},
            {"role": "user", "content": user_message}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=temp,  # This is the key parameter!
            max_tokens=150
        )

        print(f"\n{response.choices[0].message.content}\n")


# Main execution
if __name__ == "__main__":
    run_all_exercises()
