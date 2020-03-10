## Author

* David Hong

## Contents

* I've made some changes.

## Relevant Scripts

* `scripts/`:
  * `stage1.py`
  * `d_stage2.py`
  * `stage3.py`

## Setup

#### Req. For All

Set up your virtualenv for the first time:
```zsh
python3 -m pip install virtualenv
python3 -m virtualenv venv
source venv/bin/activate
python3 -m pip install -r scripts/requirements.txt
```

#### Req. For Stage 2

* Add `chromedriver` to PATH.

## Usage Details

### Stage 1

Example input:

```zsh
python3 scripts/stage1.py "July 4, 2018" "July 5, 2018" ./intermediate/s1.csv  
```

### Stage 2

Example input:

```zsh
python3 scripts/d_stage2.py ./intermediate/s1.csv ./intermediate/s2.csv
```

<!-- **This part doesn't work** because Cloudflare DDoS protection has been added since this script was last updated.

The script needs to be updated to incorporate Chrome and Selenium. This shouldn't be too hard. -->

Stage 2 is all about accessing individual incident pages (ex: `http://www.gunviolencearchive.org/incident/1157396`.) As far as I can tell, once you get Selenium to get access to the page and bypass the protection, the script just has to do the exact same thing it was already doing.

### Stage 3

???
