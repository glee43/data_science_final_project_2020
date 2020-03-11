# Scraping Readme

### Author

- David Hong

## Setup

### Step 1

Set up your virtualenv for the first time in one of two ways:

#### Option 1

```zsh
./setup_scraping.sh
```

#### Option 2

```zsh
python3 -m pip install virtualenv
python3 -m virtualenv venv
source venv/bin/activate
python3 -m pip install -r scripts/requirements.txt
```

### Step 1

- Add `chromedriver` to PATH.

## Usage

### Relevant Scripts

- `scripts/`:
  - `stage1.py`
  - `d_stage2.py`
  - `stage3.py`

### Stage 1

Example input:

```zsh
python3 scripts/stage1.py "July 4, 2018" "July 5, 2018" ./intermediate/s1.csv
```

Or:

```zsh
python3 scripts/stage1.py "04-2018"
```

### Stage 2

Example input:

```zsh
python3 scripts/d_stage2.py ./intermediate/s1.csv ./intermediate/s2.csv
```

<!-- **This part doesn't work** because Cloudflare DDoS protection has been added since this script was last updated.

The script needs to be updated to incorporate Chrome and Selenium. This shouldn't be too hard. -->

Stage 2 is all about accessing individual incident pages (ex: `http://www.gunviolencearchive.org/incident/1157396`.)

#### Speed calculation notes

There are approximately 5,000 incidents in one month.
Between April 1, 2018 and December 31, 2019, there are 21 months.
There will be approximately 105,000 incidents to scrape.

If we allow a scraper 2 seconds to scrape a single incident, and we run 15 scrapers in parallel, then we will be able to scrape 30 \* 15 = 450 incidents in one minute.

Thus, it will take 233 minutes, or about 4 hours, to scrape the entirety of 2018-2019.

### Stage 3

???
