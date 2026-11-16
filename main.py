"""Launch from any directory: python path/to/Drill_Project/main.py."""

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='SHELLBOUND / body takeover demo')
    parser.add_argument('--classic', action='store_true', help='original 3-room shedding game')
    parser.add_argument('--frames', type=int, help='bounded startup check')
    args = parser.parse_args()
    if args.classic:
        from shellgame.app import run
    else:
        from shellgame.takeover_app import run
    run(max_frames=args.frames)
