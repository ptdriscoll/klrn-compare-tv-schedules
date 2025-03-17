# KLRN Compare TV Schedules

A Python application to compare TV schedules for KLRN TV, a PBS television station.

### Data Setup

The app is currently set up to parse raw files from three sources, which should be placed in the `/data` directory:

- [ProTrack broadcast management solution](https://myersinfosys.com/protrack-tv/): An Air Date Search Report - with the headers Channel, Air Date, Type, Air Time, Program Title, Source - downloaded as a `.pdf`

- [TitanTV MediaStar Editor](https://www.titantvinc.com/broadcast-software/mediastar-suite/mediastar-editor/): A schedule page set to a channel, saved as `Webpage, Single File (\*.mhtml)`, with the channel (e.g., 9.1) appended to the file name

- [PBS TV Schedules Service API](<https://docs.pbs.org/space/tvsapi/3964930/TV+Schedules+Service+(TVSS)+API>): A read-only API that returns a TV schedule, saved as `.json` to the `/data` folder

### Config Setup

The `config.py` file defines how raw schedule files are mapped to respective parsers. The `FILES` dictionary associates each parser with a file stored in the `/data` directory:

```
FILES = {
    'protrack': 'February 2025 Schedule.pdf', # .pdf format
    'titan': 'MediaStar_9.1.mhtml', # .mhtml format
    'pbs': 'pbs.json' # .json format
}
```

To fetch a raw schedule using the [PBS TV Schedules Service API](<https://docs.pbs.org/space/tvsapi/3964930/TV+Schedules+Service+(TVSS)+API>), which is saved to the `/data` directory, the following variables must be set in `config.py`:

```
PBS_TV_SCHEDULE_API_KEY = os.getenv('PBS_TV_SCHEDULE_API_KEY')
PBS_TV_SCHEDULE_ENDPOINT = 'https://tvss.services.pbs.org/tvss/'
STATION_CALL_SIGN = 'klrn'
```

PBS stations can [request an API key](https://digitalsupport.pbs.org/support/tickets/new). Once obtained, create an `.env` file in the root directory and add the following:

```
PBS_TV_SCHEDULE_API_KEY=<api_key>
```

### Code Setup

This application uses a Conda environment to manage dependencies. You get it at [Anaconda](https://www.anaconda.com/download/) or [Miniconda](https://docs.anaconda.com/miniconda/).

The environment is defined in `environment.yml`. The `name` is `klrn-compare-tv-schedules`, which can be changed.

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
- `python run.py parse pbs`

Compare two files, with optional argument to designate the channel (defaults to 9.1):

- `python run.py compare protrack titan`
- `python run.py compare protrack pbs`
- `python run.py compare protrack titan --channel 9.2`

Use API to retrieve raw PBS TV schedule as JSON, and save it to `/data` folder, with options to set start day (defaults to today), how many days to get (defaults to 7), and ending date (which overrides how many days to get):

- `python run.py get pbs`
- `python run.py get pbs --startdate 20250313`
- `python run.py get pbs --days 14`
- `python run.py get pbs --startdate 20250318 --days 14`
- `python run.py get pbs --startdate 20250318 --enddate 20250326`

Utility to explore JSON file, with options to designate max level (defaults to 4) and how many items to show in lists (defaults to 6):

- `python run.py explore data/pbs.json`
- `python run.py explore data/pbs.json --level 3 --items 3`

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

NOTE: When using an API to fetch a raw TV schedule, the file gets saved to the `/data` directory.

### References

- [ProTrack broadcast management solution](https://myersinfosys.com/protrack-tv/)
- [TitanTV MediaStar Editor](https://www.titantvinc.com/broadcast-software/mediastar-suite/mediastar-editor/)
- [PBS TV Schedules Service API](<https://docs.pbs.org/space/tvsapi/3964930/TV+Schedules+Service+(TVSS)+API>)
- [Anaconda](https://www.anaconda.com/download/)
- [Miniconda](https://docs.anaconda.com/miniconda/)
