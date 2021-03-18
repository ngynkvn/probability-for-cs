import configparser
import argparse


def main(simulation_config, seed):
    print(*simulation_config.items())
    print("Hi!", seed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Event Simulator")
    parser.add_argument(
        "input",
        metavar="input",
        type=str,
        help="Input file for simulation",
    )
    parser.add_argument(
        "seed", metavar="seed", type=int, help="Seed number for simulation"
    )
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.input)
    if "Simulation" not in config:
        raise ValueError('Missing "Simulation" header from config file.')

    main(config["Simulation"], args.seed)