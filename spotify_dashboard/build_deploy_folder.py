"""Build a Plotly Cloud deploy folder with only the files the app needs (no credentials, AWS tooling or notebooks).

Usage:
    python spotify_dashboard/build_deploy_folder.py private
    python spotify_dashboard/build_deploy_folder.py public [--source data/full_data_2026-10-26.csv] [--until 2026-07-16]
Then:
    cd spotify_dashboard/deploy/<target> && plotly app publish [--name <app-name>]

private: live app, reads S3 via env vars set in Plotly Cloud; bundles no data.
public:  static app, bundles data/snapshot.csv (reduced columns, cut after --until); needs no AWS keys.
"""
import argparse
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent  # the dashboard app folder (app.py, src/, assets/)
REPO_ROOT = ROOT.parent
DEPLOY = ROOT / 'deploy'
CLOUD_CONFIG = 'plotly-cloud.toml'

PY_PACKAGES = ['src']  # only *.py: skips .cache (Spotify token), .DS_Store, caches
IGNORED_ASSET_FILES = shutil.ignore_patterns('.DS_Store')

DEFAULT_SOURCE = REPO_ROOT / 'data' / 'full_data_2026-10-26.csv'
DEFAULT_UNTIL = '2026-07-16'  # the pipeline silently lost data after this day
SNAPSHOT_FILE = 'snapshot.csv'

# Columns the dashboard reads or needs to load; the 11 audio features must stay contiguous (fill_missing_features).
SNAPSHOT_COLUMNS = [
    'id', 'track_id', 'track_name', 'track_duration_ms', 'track_popularity',
    'acousticness', 'danceability', 'energy', 'instrumentalness', 'key', 'liveness',
    'loudness', 'mode', 'speechiness', 'tempo', 'valence',
    'first_artist_name', 'combined_artist_names', 'artist_followers_total', 'artist_popularity',
    'artist_genres', 'artist_image_url', 'album_name', 'album_image_url', 'played_at',
]


def create_snapshot(source: Path, until: str) -> pd.DataFrame:
    """Keep only the needed columns and the plays up to and including the end of the `until` day (UTC)."""
    data = pd.read_csv(source)
    missing = [column for column in SNAPSHOT_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f'{source.name} lacks required columns: {missing}')

    played_at = pd.to_datetime(data['played_at'], format='ISO8601', utc=True)
    end = pd.Timestamp(until, tz='UTC') + pd.Timedelta(days=1)
    snapshot = data.loc[played_at < end, [c for c in data.columns if c in SNAPSHOT_COLUMNS]].reset_index(drop=True)

    if len(snapshot.columns) != len(SNAPSHOT_COLUMNS):
        raise ValueError('Unexpected snapshot columns')
    if pd.to_datetime(snapshot['played_at'], format='ISO8601', utc=True).max() >= end:
        raise ValueError('Snapshot contains plays after the cutoff')
    return snapshot


def build(target: str, source: Path, until: str) -> None:
    """Recreate deploy/<target>/ from the allow-listed sources."""
    out = DEPLOY / target
    cloud_config = out / CLOUD_CONFIG  # holds the app_id: losing it would publish a new app
    saved_config = cloud_config.read_bytes() if cloud_config.exists() else None
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    if saved_config is not None:
        cloud_config.write_bytes(saved_config)

    shutil.copy2(ROOT / 'app.py', out / 'app.py')
    shutil.copy2(ROOT / 'requirements-plotly-cloud.txt', out / 'requirements.txt')  # the name Plotly Cloud reads
    shutil.copytree(ROOT / 'assets', out / 'assets', ignore=IGNORED_ASSET_FILES)

    for package in PY_PACKAGES:
        for py_file in (ROOT / package).rglob('*.py'):
            destination = out / py_file.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(py_file, destination)

    if target == 'public':
        snapshot = create_snapshot(source, until)
        (out / 'data').mkdir()
        snapshot.to_csv(out / 'data' / SNAPSHOT_FILE, index=False)
        print(f'Snapshot: {len(snapshot)} rows, {len(snapshot.columns)} columns, plays up to {until}')

    files = sorted(p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file())
    size_mb = sum((out / f).stat().st_size for f in files) / 1e6
    print(f'{len(files)} files, {size_mb:.1f} MB in {out}')
    print('\n'.join(files))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('target', choices=['private', 'public'])
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE, help='CSV the public snapshot is built from')
    parser.add_argument('--until', default=DEFAULT_UNTIL, help='last day (UTC, YYYY-MM-DD) kept in the public snapshot')
    args = parser.parse_args()
    build(args.target, args.source, args.until)
