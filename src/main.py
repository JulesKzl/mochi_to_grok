import httpx
import json
import os
import time
import re
from datetime import datetime
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Configuration using pydantic-settings
class MochiConfig(BaseSettings):
    api_key: str
    api_base_url: str = "https://app.mochi.cards/api"
    deck_name: str = "Chinese"
    output_file: str = "chinese_vocab.txt"

    model_config = SettingsConfigDict(env_prefix="MOCHI_", case_sensitive=False)

# Load configuration
try:
    config = MochiConfig()
    print(f"Loaded API Key: {config.api_key[:4]}...{config.api_key[-4:]}")  # Debug: show partial key
except Exception as e:
    raise Exception(
        "Configuration error: Ensure MOCHI_API_KEY is set in .env or environment variables. "
        "Check .env file exists and contains MOCHI_API_KEY=your_api_key_here"
    ) from e

def get_deck_id(deck_name):
    """Fetch the deck ID for the given deck name."""
    url = f"{config.api_base_url}/decks"
    auth = httpx.BasicAuth(username=config.api_key, password="")
    timeout = httpx.Timeout(30.0, connect=30.0)  # 30s timeout for read and connect
    with httpx.Client(auth=auth, timeout=timeout) as client:
        while url:
            retries = 3
            for attempt in range(retries):
                try:
                    response = client.get(url)
                    if response.status_code != 200:
                        raise Exception(f"Failed to fetch decks: {response.status_code} {response.text}")
                    data = response.json()
                    decks = data.get("docs", [])
                    for deck in decks:
                        if deck["name"].lower() == deck_name.lower():
                            return deck["id"]
                    bookmark = data.get("bookmark")
                    if not bookmark or not decks:
                        break
                    url = f"{config.api_base_url}/decks?bookmark={bookmark}"
                    break  # Success, exit retry loop
                except httpx.ReadTimeout as e:
                    if attempt < retries - 1:
                        print(f"Read timeout on attempt {attempt + 1}/{retries}. Retrying in {2 ** attempt}s...")
                        time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    else:
                        raise Exception("Failed to fetch decks after retries: Read operation timed out") from e
    raise Exception(f"Deck '{deck_name}' not found")

def get_cards(deck_id):
    """Fetch all cards in the specified deck."""
    cards = []
    url = f"{config.api_base_url}/cards?deck-id={deck_id}&limit=100"  # Max limit to reduce requests
    auth = httpx.BasicAuth(username=config.api_key, password="")
    timeout = httpx.Timeout(30.0, connect=30.0)  # 30s timeout for read and connect
    with httpx.Client(auth=auth, timeout=timeout) as client:
        while url:
            retries = 3
            for attempt in range(retries):
                try:
                    response = client.get(url)
                    if response.status_code != 200:
                        raise Exception(f"Failed to fetch cards: {response.status_code} {response.text}")
                    data = response.json()
                    page_cards = data.get("docs", [])
                    print(f"Fetched {len(page_cards)} cards from page")  # Debug: log cards per page
                    cards.extend(page_cards)
                    if not page_cards:  # Stop if no cards are returned
                        return cards
                    bookmark = data.get("bookmark")
                    if not bookmark:
                        return cards
                    url = f"{config.api_base_url}/cards?bookmark={bookmark}&limit=100"
                    break  # Success, exit retry loop
                except httpx.ReadTimeout as e:
                    if attempt < retries - 1:
                        print(f"Read timeout on attempt {attempt + 1}/{retries}. Retrying in {2 ** attempt}s...")
                        time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    else:
                        raise Exception("Failed to fetch cards after retries: Read operation timed out") from e
    return cards

def parse_card(card):
    """Parse card content to extract pinyin, hanzi, meaning, and creation date."""
    try:
        # Extract pinyin from component-cache.pinyin
        pinyin = ""
        component_cache = card.get("component-cache", {}).get("pinyin", {})
        for key, value in component_cache.items():
            pinyin_text = value.get("text", "")
            # Extract pinyin (e.g., 'méi' from '{没}(méi) {V}(V)')
            match = re.search(r'\((.*?)\)', pinyin_text)
            if match:
                pinyin = match.group(1)
                break

        # Extract hanzi from fields (dynamic ID like RMtY4YCS)
        hanzi = ""
        fields = card.get("fields", {})
        for field_id, field_data in fields.items():
            if field_id != "name":
                field_value = field_data.get("value", "")
                # Extract hanzi, remove placeholders like 'V'
                hanzi = re.sub(r'\s*V\s*', '', field_value).strip()
                break

        # Extract meaning from name
        meaning = card.get("name", "")

        # Fallback: try component-cache.translate
        if not meaning:
            translate_cache = card.get("component-cache", {}).get("translate", {})
            for key, value in translate_cache.items():
                meaning = key  # Use the key as meaning (e.g., 'did not V (past events)')
                break

        # Get creation date
        created_at = card.get("created-at", {}).get("date", "")
        if created_at:
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")

        # Skip if critical fields are missing
        if not pinyin and not hanzi and not meaning:
            print(f"Skipping card due to missing fields: {json.dumps(card, ensure_ascii=False)}")
            return None

        return {
            "pinyin": pinyin,
            "hanzi": hanzi,
            "meaning": meaning,
            "added": created_at
        }
    except Exception as e:
        print(f"Error parsing card: {str(e)}. Raw card: {json.dumps(card, ensure_ascii=False)}")
        return None  # Skip problematic card

def write_vocab_to_file(cards):
    """Write vocabulary to a text file in the specified format."""
    valid_cards = []
    for card in cards:
        parsed = parse_card(card)
        if parsed:  # Only include valid cards
            valid_cards.append(parsed)
    
    with open(config.output_file, "w", encoding="utf-8") as f:
        for i, parsed in enumerate(valid_cards, 1):
            f.write(f"Pinyin: {parsed['pinyin']}\n")
            f.write(f"Hanzi: {parsed['hanzi']}\n")
            f.write(f"Meaning: {parsed['meaning']}\n")
            f.write(f"Added: {parsed['added']}\n")
            if i < len(valid_cards):
                f.write("---\n")
    
    print(f"Wrote {len(valid_cards)} valid cards to {config.output_file}")

def main():
    try:
        # Get deck ID
        print(f"Fetching deck '{config.deck_name}'...")
        deck_id = get_deck_id(config.deck_name)
        
        # Fetch cards
        print("Fetching cards...")
        cards = get_cards(deck_id)
        print(f"Found {len(cards)} cards")
        
        if not cards:
            print("No cards found in the deck")
            return
        
        # Write to file
        print(f"Writing to {config.output_file}...")
        write_vocab_to_file(cards)
        print(f"Vocabulary exported to {config.output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()