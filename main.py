"""Launch from any directory: python path/to/Drill_Project/main.py."""

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='SHELLBOUND / body takeover demo')
    parser.add_argument('--classic', action='store_true', help='original 3-room shedding game')
    parser.add_argument('--stage',type=int,choices=range(1,9),help='start at campaign stage 1-8')
    parser.add_argument('--frames', type=int, help='bounded startup check')
    args = parser.parse_args()
    if args.classic:
        from shellgame.app import run
    else:
        from shellgame.takeover_app import run
    if args.classic:
        run(max_frames=args.frames)
    else:
        run(max_frames=args.frames,stage=args.stage-1 if args.stage else None)
