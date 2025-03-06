# KLRN Compare TV Schedules

A Python application to compare TV schedules for KLRN TV, a PBS television station.

### Data Setup

The app is currently set up to parse raw files from two sources, which should be placed in the `/data` directory:

- [ProTrack broadcast management solution](https://myersinfosys.com/protrack-tv/): An Air Date Search Report - with the headers Channel, Air Date, Type, Air Time, Program Title, Source - downloaded as a `.pdf`

- [TitanTV MediaStar Editor](https://www.titantvinc.com/broadcast-software/mediastar-suite/mediastar-editor/): A schedule page set to a channel, saved as `Webpage, Single File (\*.mhtml)`, with the channel (e.g., 9.1) appended to the file name

### Config Setup

In `config.py`, a dictionary called `FILES` maps each parser to a raw file placed in `/data`. The format is `"parser_name": "file_name"`:

```
FILES = {
    'protrack': 'February 2025 Schedule.pdf', # .pdf format
    'titan': 'MediaStar_9.2.mhtml' # .mhtml format
}
```

### Code Setup

This application uses a Conda environment to manage dependencies. You get it at [Anaconda](https://www.anaconda.com/download/) or [Miniconda](https://docs.anaconda.com/miniconda/).

The environment is defined in `environment.yml`. The `name` is set to `klrn-compare-tv-schedules`, which can be changed.

In an Anaconda Prompt, from the application's root directory, there are two options to set up the environment:

- Option 1, system-wide environment:

  - **Create Environment:** `conda env create -f environment.yml`
  - **Activate Environment:** `conda activate <name>`
  - **Update Environment:** `conda env update -f environment.yml --prune`

- Option 2, working-directory environment:

  - **Create Environment:** `conda env create -p venv -f environment.yml`
  - **Activate Environment:** `conda activate ./venv`
  - **Update Environment:** `conda env update -p ./venv -f environment.yml --prune`

### Running Commands

Parse a file:

- `python run.py parse protrack`
- `python run.py parse titan`

Compare two files, with optional fourth argument to designate channel (defaults to 9.1):

- `python run.py compare protrack titan`
- `python run.py compare protrack titan 9.2`

### Output

A parsed file goes to `output/<parser_name>.csv`.

A comparison merges two files, adds a `MISMATCH` column, and saves:

- All comparisons at `output/<parsed_file_name_1>_<parsed_file_name_2>.csv`
- Only mismatches at `output/<parsed_file_name_1>_<parsed_file_name_2>_mismatches.csv`

Examples:

- Parsed file: `protrack.csv`
- Parsed file: `titan.csv`
- Compared files: `protrack_titan.csv`
- Compared files: `protrack_titan_mismatches.csv`

### References

- [ProTrack broadcast management solution](https://myersinfosys.com/protrack-tv/)
- [TitanTV MediaStar Editor](https://www.titantvinc.com/broadcast-software/mediastar-suite/mediastar-editor/)
- [Anaconda](https://www.anaconda.com/download/)
- [Miniconda](https://docs.anaconda.com/miniconda/)
