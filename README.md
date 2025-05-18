# Mochi Vocabulary Exporter

This Python script exports vocabulary cards from a Mochi Pro deck (e.g., "Chinese") to a text file using the Mochi API. It’s designed for language learners to extract Chinese vocabulary (pinyin, hanzi, meaning, and creation date) for further processing, such as generating translations or example sentences.

## Features
- Fetches cards from a specified Mochi deck via the REST API.
- Parses pinyin, hanzi, meaning, and creation date.
- Outputs to a text file in the format:
  ```
  Pinyin: nǐ hǎo
  Hanzi: 你好
  Meaning: bonjour
  Added: 2025-01-15 14:30:22
  ---
  ```
- Securely loads API key from a `.env` file using `pydantic-settings`.
- Supports batch processing for large decks.

## Prerequisites
- Python 3.8 or higher
- A Mochi Pro account with an API key (get it from [app.mochi.cards](https://app.mochi.cards) account settings)
- Git (optional, for cloning the repository)

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Create and Activate a Virtual Environment
Create a virtual environment named `venv`:
```bash
python -m venv venv
```

Activate it:
- **Windows**:
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies
Install required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Configure the Environment
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```

Edit `.env` with your Mochi API key (availble on https://app.mochi.cards)
```
MOCHI_API_KEY=your_mochi_api_key
MOCHI_API_BASE_URL=https://app.mochi.cards/api
MOCHI_DECK_NAME=Chinese
MOCHI_OUTPUT_FILE=chinese_vocab.txt
```

**Note**: Keep `.env` private. It’s excluded from Git via `.gitignore`.

## Usage 

### 1. Run the Script
Run the script to export vocabulary:
```bash
python -m src.main
```

The script will:
- Fetch cards from the "Chinese" deck.
- Save to `chinese_vocab.txt` in the specified format.

#### Output
The output file (`chinese_vocab.txt`) looks like:
```
Pinyin: nǐ hǎo
Hanzi: 你好
Meaning: bonjour
Added: 2025-01-15 14:30:22
---
Pinyin: xuéxí
Hanzi: 学习
Meaning: étudier
Added: 2025-01-16 09:45:10
```

Use this file to copy batches (e.g., 20–30 entries) for further processing, such as sending to a language model for translations or example sentences.

### Prompt 
Open Grok and use the following prompt:
```
I'm adding new vocabulary that I learned with my Chinese teacher into mochi. Everytime I type pinyin, you will translate it in French, write the sinogram/hanzi and create an example using the vocabulary I already learned. I just told you every word I know as of now. Wait for my input in pinyin or in French now
```
Then copy the whole list of vocabulary created (mine has around 600 words) to the LLM.
Finally input your vocabulary, for example:
```
haishi: quand meme
```
Output would be:

- **Pinyin**: hǎishì
- **French Translation**: quand même
- **Hanzi**: 还是
- **Example Sentence**: 
  - **Hanzi**: 虽然我很累，我还是想去公园跑步。
  - **Pinyin**: Suīrán wǒ hěn lèi, wǒ hǎishì xiǎng qù gōngyuán pǎobù.
  - **French**: Bien que je sois très fatigué, je veux quand même aller courir dans le parc.


**Explanation**: The word "还是" (hǎishì) is used here to mean "quand même" in the sense of "nevertheless" or "still." It connects with vocabulary from your list like 累 (lèi, fatigué), 想 (xiǎng, vouloir), 去 (qù, aller), 公园 (gōngyuán, parc), and 跑步 (pǎobù, courir). If you meant a different nuance of "quand même" or want a specific context, let me know! What's the next word?


## Troubleshooting
- **API Key Error**: Ensure `MOCHI_API_KEY` is set in `.env` or as an environment variable.
- **Deck Not Found**: Verify the deck name in `.env` matches your Mochi deck (case-insensitive).
- **Card Parsing Issues**: If your cards have custom fields, edit the `parse_card` function in the script to match your field names (e.g., "Pinyin", "Hanzi").

## Contributing
Feel free to open issues or submit pull requests for improvements!

## License
[MIT License](LICENSE)


