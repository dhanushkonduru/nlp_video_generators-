import argparse
import json

from dotenv import load_dotenv

from src.video_generator.main import generate_video


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automated educational video generation")
    parser.add_argument("--topic", required=True, type=str)
    parser.add_argument("--audience", required=True, choices=["kids", "students", "general"])
    parser.add_argument("--tone", required=True, choices=["formal", "engaging", "storytelling"])
    parser.add_argument("--duration", required=True, type=int, help="Target duration in seconds, between 30 and 60")
    parser.add_argument("--tts", default="speecht5", choices=["speecht5", "gtts"], help="TTS engine (default: speecht5)")
    parser.add_argument("--output-dir", default="outputs", type=str)
    parser.add_argument("--bgm", default=None, type=str, help="Optional background music file path")
    return parser.parse_args()


def main() -> None:
    load_dotenv(".env")
    load_dotenv(".env.example")
    args = parse_args()
    duration = max(30, min(60, int(args.duration)))

    result = generate_video(
        topic=args.topic,
        audience=args.audience,
        tone=args.tone,
        duration_seconds=duration,
        output_dir=args.output_dir,
        tts_engine=args.tts,
        background_music_path=args.bgm,
    )

    print(json.dumps(
        {
            "final_video": result.final_video_path,
            "script_json": result.script_json_path,
            "assets_used_json": result.assets_json_path,
            "asset_count": len(result.assets_used),
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
