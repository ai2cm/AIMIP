"""Build the AIMIP code + minimal-data reproducibility archive.

Produces a self-contained `.tar.gz` (code + the ~140 MB minimal `cached/`) that reproduces every
manuscript figure with no raw-data download — the artifact intended for a new Zenodo version (see
`evaluations/REPRODUCIBILITY.md`).

Steps:
  1. Write `evaluations/notebooks/cached/MANIFEST.md` from FIG_MAP below (cache file -> figures it
     feeds, size, md5).
  2. Stage every git-tracked file into a clean tree (mirrors the Zenodo v0.2.1 layout).
  3. Inject the reduced `cached/*.nc` files listed in FIG_MAP + MANIFEST.md.
  4. tar.gz the tree.

The committed notebooks already default to `RESTORE_CACHE = True` / `RESET_CACHE = False` and carry the
interactive run-these-cells markdown, so no flag-flipping or cell-stripping is needed here.

Usage (from anywhere in the repo, with the aimip-evaluations env):
    python evaluations/build_repro_archive.py [--outdir DIR] [--name NAME]

FIG_MAP is the source of truth for which cache files are shipped; update it if the reduced-cache set
changes. Re-run after regenerating the cache (the `RESET_CACHE = True` toggle) to rebuild the archive.
"""
import argparse, hashlib, json, os, shutil, subprocess, tempfile

REPO = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                      capture_output=True, text=True, check=True).stdout.strip()
CACHE = os.path.join(REPO, 'evaluations', 'notebooks', 'cached')

# cache file -> manuscript figures it feeds (source of truth for the shipped cache set)
FIG_MAP = {
 'E1-time-mean-biases': {
   'biases_map_1deg.nc': ['bias_1deg_map_tas_pr', 'app_bias_1deg_map_train_tas', 'app_bias_1deg_map_test_tas'],
   'biases_map_2p8deg.nc': ['app_bias_2p8deg_map_tas_pr'],
   'rmsb_1deg.nc': ['rmsb_1deg_bar_surface_and_plev', 'app_rmsb_tas_bar', 'app_rmsb_1deg_plev_ta', 'app_rmsb_1deg_plev_hus', 'app_rmsb_1deg_plev_ua', 'app_rmsb_1deg_plev_va'],
   'rmsb_2p8deg.nc': ['app_rmsb_2p8deg_bar_surface_and_plev'],
 },
 'E2-trends': {
   'regridded_global_annual_means.nc': ['trend_series_tas_ens_false', 'trend_series_tas_ens_true', 'trend_bar_surface_and_plev', 'app_trend_1deg_plev_ta', 'app_trend_1deg_plev_hus'],
   'global_annual_mean_era5.nc': ['trend_series_tas_ens_false', 'trend_series_tas_ens_true', 'trend_bar_surface_and_plev'],
   'regridded_global_annual_means_2p8deg.nc': ['app_trend_series_tas_2p8deg', 'app_trend_bar_2p8deg_surface_and_plev'],
   'regridded_global_annual_mean_era5_2p8deg.nc': ['app_trend_series_tas_2p8deg', 'app_trend_bar_2p8deg_surface_and_plev'],
   'regridded_trend_1deg.nc': ['trend_map_1deg'],
   'regridded_trend_era5_1deg.nc': ['trend_map_1deg'],
   'regridded_trend_2p8deg.nc': ['app_trend_map_2p8deg'],
   'regridded_trend_era5_2p8deg.nc': ['app_trend_map_2p8deg'],
 },
 'E3-enso-correlations': {
   'enso_coeff_error_map_1deg.nc': ['enso_coeff_map_1deg'],
   'enso_coeff_era5_map_1deg.nc': ['enso_coeff_map_1deg'],
   'enso_coeff_error_map_2p8deg.nc': ['app_enso_coeff_map_2p8deg'],
   'enso_coeff_era5_map_2p8deg.nc': ['app_enso_coeff_map_2p8deg'],
   'enso_coeff_rmse_1deg.nc': ['app_enso_coeff_rmse_bar'],
   'enso_coeff_rmse_2p8deg.nc': ['app_enso_coeff_rmse_2p8deg_bar'],
 },
 'E4-temporal-variance': {
   'error_map_1deg.nc': ['daily_variability_error_1deg_map_tas_pr'],
   'daily_anomaly_std_era5_map_1deg.nc': ['daily_variability_error_1deg_map_tas_pr'],
   'gm_error_1deg.nc': ['daily_variability_relative_error_1deg_bar_surface_and_plev'],
   'gm_error_1deg_normalized.nc': ['daily_variability_relative_error_1deg_bar_surface_and_plev'],
   'error_dry_day_map_1deg.nc': ['app_dry_day_fraction_1deg_map'],
   'dry_day_frac_era5_map_1deg.nc': ['app_dry_day_fraction_1deg_map'],
 },
 'E5-perturbed-sst-response': {
   'combined_1deg_perturbed_sst_response_time_means.nc': ['perturbation_response_map_tas_pr'],
   'combined_2p8deg_perturbed_sst_response_time_means.nc': ['app_perturbation_response_map_2p8deg_tas_pr'],
 },
}


def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def write_manifest():
    lines = ['# Minimal cache manifest', '',
             'Each notebook loads only these files (with `RESTORE_CACHE = True`) to regenerate its '
             'manuscript figures.', '']
    shipped = []
    for nb, files in FIG_MAP.items():
        lines += [f'## {nb}', '', '| cache file | size | md5 | figures |', '|---|---|---|---|']
        for f, figs in files.items():
            p = os.path.join(CACHE, f)
            if not os.path.exists(p):
                raise SystemExit(f'ERROR: missing cache file {f} — regenerate the cache first.')
            shipped.append(f)
            lines.append(f'| `{f}` | {os.path.getsize(p) / 1e6:.2f} MB | `{md5(p)}` | {", ".join(figs)} |')
        lines.append('')
    total = sum(os.path.getsize(os.path.join(CACHE, f)) for f in shipped)
    lines.insert(3, f'**{len(shipped)} files, {total / 1e6:.1f} MB total.**')
    lines.insert(4, '')
    with open(os.path.join(CACHE, 'MANIFEST.md'), 'w') as fh:
        fh.write('\n'.join(lines))
    print(f'wrote MANIFEST.md ({len(shipped)} files, {total / 1e6:.1f} MB)')
    return shipped


def stage(shipped, stage_dir):
    if os.path.exists(stage_dir):
        shutil.rmtree(stage_dir)
    os.makedirs(stage_dir)
    tracked = subprocess.run(['git', '-C', REPO, 'ls-files'],
                             capture_output=True, text=True, check=True).stdout.split('\n')
    tracked = [t for t in tracked if t]
    for t in tracked:
        src = os.path.join(REPO, t)
        if not os.path.exists(src):
            continue
        dst = os.path.join(stage_dir, t)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    print(f'staged {len(tracked)} tracked files')
    # include the reproducibility doc even if not yet committed
    doc = os.path.join('evaluations', 'REPRODUCIBILITY.md')
    if os.path.exists(os.path.join(REPO, doc)) and not os.path.exists(os.path.join(stage_dir, doc)):
        shutil.copy2(os.path.join(REPO, doc), os.path.join(stage_dir, doc))
        print(f'  + {doc}')
    # inject the reduced cache + manifest
    dst_cache = os.path.join(stage_dir, 'evaluations', 'notebooks', 'cached')
    os.makedirs(dst_cache, exist_ok=True)
    for f in shipped + ['MANIFEST.md']:
        shutil.copy2(os.path.join(CACHE, f), os.path.join(dst_cache, f))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--outdir', default=tempfile.gettempdir(),
                    help='where to write the staging tree and tarball (default: system temp)')
    ap.add_argument('--name', default='AIMIP-repro-archive', help='archive base name')
    args = ap.parse_args()

    shipped = write_manifest()
    stage_dir = os.path.join(args.outdir, args.name)
    stage(shipped, stage_dir)
    out = stage_dir + '.tar.gz'
    subprocess.run(['tar', '-czf', out, '-C', os.path.dirname(stage_dir), os.path.basename(stage_dir)],
                   check=True)
    print(f'archive: {out}  ({os.path.getsize(out) / 1e6:.1f} MB)')


if __name__ == '__main__':
    main()
