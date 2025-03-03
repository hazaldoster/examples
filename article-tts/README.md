# Article TTS

A Python tool for converting articles to speech using text-to-speech technology. This tool helps users transform written content into audio format for better accessibility and convenience.

## Features

- Convert articles from various sources (text files, URLs, etc.) to speech
- Support for multiple TTS engines
- Customizable voice options and speech parameters
- Easy-to-use command line interface
- Save output as MP3, WAV, or other audio formats

## Installation

Requires Python 3.13 or higher.

```bash
# Clone the repository
git clone https://github.com/yourusername/article-tts.git
cd article-tts

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python article_tts.py --input article.txt --output speech.mp3
```

### Advanced Options

```bash
python article_tts.py --input https://example.com/article --output speech.mp3 --voice female --rate 175 --format mp3
```

## Dependencies

- Python 3.13+
- [Required dependencies will be listed in requirements.txt]

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgements

- List any libraries, APIs, or other resources that were used or inspired this project
- Credit any contributors or sources of inspiration
