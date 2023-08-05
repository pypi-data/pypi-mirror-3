# Madiolahb
# Copyright 2011 Max Battcher. Licensed for use under the Ms-RL. See LICENSE.

def main():
    from core import fill_character
    import acting
    import argparse
    import chardesc
    import movement
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o', type=argparse.FileType('w'),
        default=sys.stdout)
    parser.add_argument('--format', '-f',
        choices=('JSON', 'YAML'),
        default='JSON')
    parser.add_argument('--input', '-i', type=argparse.FileType('r'),
        default=sys.stdin)

    subp = parser.add_subparsers()
    acting.register_commands(subp)
    chardesc.register_commands(subp)
    movement.register_commands(subp)

    args = parser.parse_args()

    lw = None
    if args.format == 'JSON':
        import json
        lw = json.load(args.input)
    elif args.format == 'YAML':
        import yaml
        lw = yaml.load(args.input)
    fill_character(lw)

    args.func(lw, **args.__dict__)
    if args.format == 'JSON':
        import json
        json.dump(lw, args.output)
    elif args.format == 'YAML':
        import yaml
        yaml.dump(lw, args.output)

if __name__ == "__main__":
    main()

# vim: ai et ts=4 sts=4 sw=4
