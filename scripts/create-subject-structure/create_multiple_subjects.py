import os
import sys

def create_structure():
    print("\n--- Subject Structure Creator ---")
    
    # Ask for subject names
    while True:
        subjects = input("Enter the subject names (separated by commas): ").strip()
        if subjects:
            subject_list = [s.strip() for s in subjects.split(',')]
            break
        print("You must enter at least one subject!")

    # Handle weeks
    if len(subject_list) == 1:
        while True:
            try:
                weeks = int(input(f"Enter the number of weeks for {subject_list[0]}: ").strip())
                if weeks > 0:
                    week_list = [weeks]
                    break
                print("It must be a positive number!")
            except ValueError:
                print("Enter a valid number!")
    else:
        while True:
            option = input("Do all subjects have the same number of weeks? (y/n): ").strip().lower()
            if option in ['y', 'n']:
                break
            print("Enter 'y' or 'n'!")

        if option == 'y':
            while True:
                try:
                    weeks = int(input("Enter the number of weeks for all subjects: ").strip())
                    if weeks > 0:
                        week_list = [weeks] * len(subject_list)
                        break
                    print("It must be a positive number!")
                except ValueError:
                    print("Enter a valid number!")
        else:
            while True:
                weeks_input = input("Enter the number of weeks for each subject (comma-separated): ").strip()
                if weeks_input:
                    try:
                        week_list = [int(w.strip()) for w in weeks_input.split(',')]
                        if all(w > 0 for w in week_list):
                            if len(week_list) == len(subject_list):
                                break
                            print(f"You must enter {len(subject_list)} values!")
                        else:
                            print("All values must be positive!")
                    except ValueError:
                        print("Only enter numbers separated by commas!")
                    print("Incorrect format!")

    # Create folder structure
    for subject, weeks in zip(subject_list, week_list):
        try:
            os.makedirs(subject, exist_ok=True)
            print(f"\nCreated subject folder: '{subject}'")
            
            for week in range(1, weeks + 1):
                week_name = f"{week:02d}_WEEK"
                os.makedirs(os.path.join(subject, week_name), exist_ok=True)
                print(f"  - {week_name}")
                
        except Exception as e:
            print(f"\nError creating folders for {subject}: {str(e)}")

    print("\n✅ Structure created successfully!")

if __name__ == "__main__":
    create_structure()
    if sys.platform == 'win32':
        os.system('pause')
