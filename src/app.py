from query_router import full_pipeline, full_pipeline_from_photo
import whisper


def get_text_input():
    query = input("\nType your ingredients or request: ").strip()
    return query


def get_voice_input():
    audio_path = input("\nPath to your audio file: ").strip()
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcribed = result["text"].strip()
    print(f"Transcribed: {transcribed}")
    return transcribed


def get_photo_input():
    image_path = input("\nPath to your photo: ").strip()
    return image_path  # handled differently since full_pipeline_from_photo takes the path directly


def main():
    print("=" * 60)
    print("Welcome to Fridge2Fork!")
    print("=" * 60)

    while True:
        print("\nHow would you like to give your ingredients?")
        print("1. Type them")
        print("2. Speak them (provide an audio file)")
        print("3. Show a photo")
        print("4. Quit")

        choice = input("Choose 1-4: ").strip()

        email_input = input("Email address to send the recipe to (or press Enter to skip): ").strip()
        email_to = email_input if email_input else None

        nutrition_input = input("Include nutrition suggestions? (y/n): ").strip().lower()
        include_nutrition = nutrition_input == "y"

        if choice == "1":
            query = get_text_input()
            full_pipeline(query, email_to=email_to, include_nutrition=include_nutrition)

        elif choice == "2":
            query = get_voice_input()
            full_pipeline(query, email_to=email_to, include_nutrition=include_nutrition)

        elif choice == "3":
            image_path = get_photo_input()
            full_pipeline_from_photo(image_path, email_to=email_to, include_nutrition=include_nutrition)

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()