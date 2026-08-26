import argparse
from pathlib import Path
from urllib.parse import urlparse

# python program-arguments.py --input-path s3://gksbucket/bronze/movielens/movies/  --output-path s3://gksbucket/silver/movielens/movies

# python program-arguments.py --input-path /mnt/c/bronze/movielens/movies/  --output-path /mnt/c/silver/movielens/movies

# python program-arguments.py --input-path hdfs:///user/cloud_user/movielens-bronze/ratings  --output-path hdfs:///user/cloud_user/movielens-silver/ratings



def validate_data_path(path, argument_name):
    parsed = urlparse(path)

    # S3 path
    if parsed.scheme in {"s3", "s3a"}:
        if not parsed.netloc:
            raise argparse.ArgumentTypeError(
                f"{argument_name}: S3 bucket name is missing"
            )

        if not parsed.path.strip("/"):
            raise argparse.ArgumentTypeError(
                f"{argument_name}: S3 object key or prefix is missing"
            )

        return path

    # HDFS path
    if parsed.scheme == "hdfs":
        if not parsed.path.startswith("/"):
            raise argparse.ArgumentTypeError(
                f"{argument_name}: invalid HDFS path"
            )

        return path

    # Explicit local-file URI
    if parsed.scheme == "file":
        if parsed.netloc not in {"", "localhost"}:
            raise argparse.ArgumentTypeError(
                f"{argument_name}: file URI must use file:///path "
                "or file://localhost/path"
            )

        if not parsed.path.startswith("/"):
            raise argparse.ArgumentTypeError(
                f"{argument_name}: local file path must be absolute"
            )

        return path

    # Plain Linux absolute path
    if parsed.scheme == "":
        if not Path(path).is_absolute():
            raise argparse.ArgumentTypeError(
                f"{argument_name}: Linux path must be absolute"
            )

        return path

    raise argparse.ArgumentTypeError(
        f"{argument_name}: unsupported path scheme '{parsed.scheme}'"
    )


def data_path_type(argument_name: str):
    return lambda value: validate_data_path(value, argument_name)


parser = argparse.ArgumentParser(
    description="Validate input and output data paths"
)

parser.add_argument(
    "--input-path",
    required=True,
    type=data_path_type("--input-path"),
    help="Input path: S3, HDFS or an absolute Linux path",
)

parser.add_argument(
    "--output-path",
    required=True,
    type=data_path_type("--output-path"),
    help="Output path: S3, HDFS or an absolute Linux path",
)

args = parser.parse_args()

if args.input_path.rstrip("/") == args.output_path.rstrip("/"):
    parser.error("--input-path and --output-path cannot be the same")

print("Parameters validated successfully")
print(f"Input path : {args.input_path}")
print(f"Output path: {args.output_path}")
