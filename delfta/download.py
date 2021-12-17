"""
© 2021, ETH Zurich
"""

import argparse
import os
import tarfile

import requests
import torch
from tqdm import tqdm

from delfta.net_utils import DEVICE
from delfta.utils import DATA_PATH, LOGGER, ROOT_PATH

DATASET_REMOTE = (
    "https://www.research-collection.ethz.ch/bitstream/handle/20.500.11850/520329/qmugs.tar.gz?sequence=1&isAllowed=y"
)

MODELS = {
    "multitask_delta": "multitask_delta.pt",
    "single_energy_delta": "single_energy_delta.pt",
    "charges_delta": "charges_delta.pt",
    "wbo_delta": "wbo_delta.pt",
    "multitask_direct": "multitask_direct.pt",
    "single_energy_direct": "single_energy_direct.pt",
    "charges_direct": "charges_direct.pt",
    "wbo_direct": "wbo_direct.pt",
}

MODELS_REMOTE = (
    "https://www.research-collection.ethz.ch/bitstream/handle/20.500.11850/520281/models.tar.gz?sequence=6&isAllowed=y"
)

UTILS_REMOTE = (
    "https://www.research-collection.ethz.ch/bitstream/handle/20.500.11850/520281/utils.tar.gz?sequence=8&isAllowed=y"
)

TESTS_REMOTE = "https://www.research-collection.ethz.ch/bitstream/handle/20.500.11850/520329/test_data.tar.gz?sequence=2&isAllowed=y"


def download(src, dest):
    """Simple requests.get with a progress bar

    Parameters
    ----------
    src : str
        Remote path to be downloaded
    dest : str
        Local path for the download

    Returns
    -------
    None
    """
    r = requests.get(src, stream=True)
    tsize = int(r.headers.get("content-length", 0))
    progress = tqdm(total=tsize, unit="iB", unit_scale=True, position=0, leave=False)

    with open(dest, "wb") as handle:
        progress.set_description(os.path.basename(dest))
        for chunk in r.iter_content(chunk_size=1024):
            handle.write(chunk)
            progress.update(len(chunk))


def get_model_weights(model_path):
    """Returns a torch.load handle for a model with a specific `name` from the specified model_path.

    Parameters
    ----------
    name : str
        Name of the model weights to be returned
    model_path: str
        Path to model folder

    Returns
    -------
    torch.weights
        Trained weights for the requested model
    """
    weights = torch.load(model_path, map_location=DEVICE)
    return weights


def _download_required():
    """
    Helper function to download production trained models as well as utility files.
    """
    models_tar = os.path.join(ROOT_PATH, "models.tar.gz")
    download(MODELS_REMOTE, models_tar)

    with tarfile.open(models_tar) as handle:
        handle.extractall(ROOT_PATH)

    utils_tar = os.path.join(ROOT_PATH, "utils.tar.gz")
    download(UTILS_REMOTE, utils_tar)

    with tarfile.open(utils_tar) as handle:
        handle.extractall(ROOT_PATH)


def _download_training():
    """
    Helper function to download the QMugs data set.
    """
    download(DATASET_REMOTE, os.path.join(DATA_PATH, "qmugs.tar.gz"))

    with tarfile.open(os.path.join(DATA_PATH, "qmugs.tar.gz")) as handle:
        handle.extractall(DATA_PATH)


def _download_tests():
    """
    Helper function to download the tests used upon package build.
    """
    tests_tar = os.path.join(DATA_PATH, "test_data.tar.gz")
    download(TESTS_REMOTE, tests_tar)

    with tarfile.open(tests_tar) as handle:
        handle.extractall(DATA_PATH)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="General download script")
    parser.add_argument("--training", dest="training", action="store_true", default=False)
    parser.add_argument("--tests", dest="tests", action="store_true", default=False)
    args = parser.parse_args()

    os.makedirs(DATA_PATH, exist_ok=True)

    # Trained models and utils
    LOGGER.info("Now downloading trained models and utils...")
    _download_required()

    # Training data
    if args.training:
        LOGGER.info("Now downloading training data...")
        _download_training()

    # Test files
    if args.tests:
        LOGGER.info("Downloading tests...")
        _download_tests()

