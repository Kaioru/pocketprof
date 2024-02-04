# pocketprof
a really cool telebot that tells u about ntu cs stuff

## How to run
1. Download dependencies `pip install -r requirements. txt`
2. Create `.env` file with `cp .env.example .env`
3. Modify .env files to the appropriate values
4. Execute `python app/bot.py`

## Updating datasets
1. Delete existing `chroma_store/` folder if any
2. Add files into the `datasets/..` folders appropriately
3. Run the app and it will regenerate the chroma_store based on the datasets