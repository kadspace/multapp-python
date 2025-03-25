import random
import time
from db_manager import setup_database, update_stats, get_stats, get_weakest_combinations

def multiplication_quiz():
    print("Welcome to the Multiplication Quiz!")
    print("You'll be given multiplication problems from 5x5 to 9x9.")
    print("Type 'quit' to exit the game.")
    print("Type 'stats' to see your weakest combinations.")
    print()
    
    # Ensure the database is set up
    setup_database()
    
    score = 0
    total_questions = 0
    
    while True:
        # Generate random numbers between 5 and 9
        num1 = random.randint(5, 9)
        num2 = random.randint(5, 9)
        
        # Calculate the correct answer
        correct_answer = num1 * num2
        
        # Ask the question
        question = f"What is {num1} × {num2}? "
        start_time = time.time()
        user_input = input(question)
        end_time = time.time()
        duration = end_time - start_time
        
        # Check if user wants to quit
        if user_input.lower() == 'quit':
            break
        
        # Check if user wants to see stats
        if user_input.lower() == 'stats':
            print("\n===== Your Weakest Combinations =====")
            weakest = get_weakest_combinations(5)
            if weakest:
                for i, combo in enumerate(weakest, 1):
                    print(f"{i}. {combo['num1']} × {combo['num2']}: {combo['correct_count']}/{combo['total_attempts']} correct ({combo['success_rate']*100:.1f}%)")
            else:
                print("No data available yet.")
            print()
            continue
        
        # Validate input and check answer
        try:
            user_answer = int(user_input)
            total_questions += 1
            
            if user_answer == correct_answer:
                print("Correct! ✓")
                score += 1
            else:
                print(f"Incorrect. The answer is {correct_answer}.")
            
            # Update the statistics
            update_stats(num1, num2, user_answer, correct_answer, duration)
            
            # Show the current score and some statistics
            print(f"Current score: {score}/{total_questions}")
            
            # Show stats for this problem
            stats = get_stats(num1, num2)
            if stats:
                success_rate = (stats['correct_count'] / stats['total_attempts'] * 100) if stats['total_attempts'] > 0 else 0
                print(f"For {num1}×{num2}: {stats['correct_count']}/{stats['total_attempts']} correct ({success_rate:.1f}%)")
                if stats['correct_count'] > 0:
                    print(f"Average time for correct answers: {stats['avg_duration']:.2f} seconds")
            print()
            
        except ValueError:
            print("Please enter a number, 'stats', or 'quit' to exit.\n")
    
    # Final score when user quits
    if total_questions > 0:
        percentage = (score / total_questions) * 100
        print(f"\nGame Over! Your final score is {score}/{total_questions} ({percentage:.1f}%).")
    else:
        print("\nGame Over! You didn't answer any questions.")
    
    # Show overall statistics
    print("\n===== Your Overall Statistics =====")
    weakest = get_weakest_combinations(3)
    if weakest:
        print("Your weakest combinations:")
        for i, combo in enumerate(weakest, 1):
            print(f"{i}. {combo['num1']} × {combo['num2']}: {combo['correct_count']}/{combo['total_attempts']} correct ({combo['success_rate']*100:.1f}%)")
