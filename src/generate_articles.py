#!/usr/bin/env python3
"""
Lightweight script to generate random topics, call OpenAI API or Ollama API,
and save the responses as PDFs with metadata.
"""

import os
import re
import time
import json
import random
import string
import argparse
from pathlib import Path
from datetime import datetime


# =============================================================================
# CONFIGURATION
# =============================================================================
def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--api_variant",
        type=str,
        choices=["ollama", "openai", "openai_compatible"],
        default=os.getenv("API_VARIANT", "openai"),
        help="Type of API."
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default=os.getenv("MODEL_NAME", ""),
        help="Model to use for generating article text."
    )
    # API base URL (use for compatible APIs like Ollama, OpenAI, OpenAI-compatible)
    # Leave empty to use default OpenAI API (https://api.openai.com/v1)
    parser.add_argument(
        "--model_api_base_url",
        type=str,
        default=os.getenv("MODEL_API_BASE_URL", None),
        help="Base Url for Model API."
    )
    parser.add_argument(
        "--num_pdfs",
        type=int,
        default=int(os.getenv("NUM_PDFS", "3")),
        help="Number of articles to generate.",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=os.getenv("OUTPUT_DIR", "output_files"),
        help="Output directory for generated files."
    )
    parser.add_argument(
        "--skip_failed_parsing_files",
        type=str2bool,
        default=os.getenv("SKIP_FAILED_PARSING_FILES", False),
        help="Skip a generated model-text if text is not parsable as excepted."
    )

    return parser.parse_args()


args = parse_args()

API_VARIANT = args.api_variant

# model to use for text generation
MODEL_NAME = args.model_name

MODEL_API_BASE_URL = args.model_api_base_url

# Number of PDF files to generate
NUM_PDFS = args.num_pdfs

# Output directory for PDFs and metadata
OUTPUT_DIR = args.output_dir

# Skip a file if parsing of model response fails
SKIP_FAILED_PARSING_FILES=args.skip_failed_parsing_files
SKIPPED_FAILED_PARSING_FILES_COUNT = 0
FAILED_PARSING_FILES_TO_MARKDOWN_COUNT = 0

if API_VARIANT == "ollama" and MODEL_API_BASE_URL in ("", None):
    MODEL_API_BASE_URL = "https://ollama.com" # cloud variant
elif API_VARIANT == "openai" and MODEL_API_BASE_URL == "":
    MODEL_API_BASE_URL = None
elif API_VARIANT == "openai_compatible" and MODEL_API_BASE_URL == "":
    print("Please set MODEL_API_BASE_URL environment variable to your API.")
    exit(1)

OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# List of random topics for the LLM to write about
RANDOM_TOPICS = [
    # Technology & Computing
    "the history of coffee",
    "quantum computing basics",
    "the evolution of smartphones",
    "artificial intelligence in healthcare",
    "blockchain technology and its applications",
    "cybersecurity best practices",
    "the Internet of Things (IoT)",
    "cloud computing fundamentals",
    "virtual reality in education",
    "the development of renewable energy",
    "the history of video games",
    "augmented reality applications",
    "the evolution of the internet",
    "edge computing explained",
    "quantum cryptography",
    "natural language processing",
    "the ethics of artificial intelligence",
    "robotics in manufacturing",
    "data privacy regulations",
    "the development of wireless charging",
    # Nature & Science
    "the art of bonsai trees",
    "deep sea exploration",
    "the ecosystem of coral reefs",
    "the life cycle of butterflies",
    "volcanic eruptions and their impact",
    "the migration patterns of whales",
    "photosynthesis in plants",
    "the biodiversity of rainforests",
    "earth's magnetic field",
    "asteroids and their threat to Earth",
    "the phenomenon of bioluminescence",
    "plate tectonics and continental drift",
    "the science of climate change",
    "black holes and cosmology",
    "the psychology of animal behavior",
    "extinction events in Earth's history",
    "the water cycle and oceans",
    "genetic inheritance and traits",
    "the physics of lightning",
    "endangered species conservation",
    # History & Culture
    "the Silk Road trade routes",
    "ancient Egyptian mythology",
    "renaissance art history",
    "the architecture of Gothic cathedrals",
    "the fall of the Roman Empire",
    "the Industrial Revolution",
    "the construction of the Great Wall of China",
    "the discovery of penicillin",
    "the history of the Olympics",
    "the origins of democracy",
    "the French Revolution",
    "the Viking Age",
    "the spread of Buddhism",
    "the Magna Carta and legal history",
    "the Ottoman Empire",
    "the Renaissance scientific revolution",
    "the history of writing systems",
    "ancient Greek philosophy",
    "the spice trade",
    "the colonization of Australia",
    # Society & Psychology
    "the psychology of color",
    "time management techniques",
    "the science of taste and smell",
    "the effects of social media on mental health",
    "the psychology of dreams",
    "learning a new language",
    "the benefits of meditation",
    "the history of money and banking",
    "cultural diversity in the workplace",
    "the impact of music on the brain",
    "the psychology of motivation",
    "emotional intelligence",
    "the science of sleep",
    "body language and nonverbal communication",
    "the psychology of habit formation",
    "cognitive biases in decision making",
    "the history of advertising",
    "social inequality and its effects",
    "the psychology of persuasion",
    "addiction and the brain",
    # Modern Topics
    "vertical farming",
    "bioinformatics and DNA",
    "cryptocurrencies and blockchain",
    "machine learning in agriculture",
    "urban planning and smart cities",
    "3D printing in medicine",
    "the future of transportation",
    "space tourism",
    "gene editing with CRISPR",
    "sustainable living practices",
    "electric vehicles and infrastructure",
    "precision medicine",
    "artificial meat and food technology",
    "carbon capture technology",
    "the gig economy",
    "digital identity and authentication",
    "ocean cleanup initiatives",
    "neurotechnology and brain-computer interfaces",
    "smart home technology",
    "the circular economy",
    # Business & Finance
    "the principles of supply and demand",
    "stock market investing for beginners",
    "the role of central banks in economics",
    "entrepreneurship and startup culture",
    "the impact of globalization on economies",
    "personal finance and budgeting strategies",
    "the history of international trade",
    "cryptocurrency markets and trading",
    "corporate social responsibility",
    "the functioning of stock exchanges",
    "real estate investment strategies",
    "the psychology of consumer behavior",
    "diversification in investment portfolios",
    "the evolution of banking systems",
    "mergers and acquisitions basics",
    "economic indicators and their significance",
    "the role of venture capital in startups",
    "financial planning for retirement",
    "the impact of inflation on economies",
    "e-commerce business models",
    # Health & Wellness
    "the benefits of regular exercise",
    "nutrition and balanced diets",
    "mental health awareness",
    "the science of immunity and vaccines",
    "sleep hygiene and quality rest",
    "stress management techniques",
    "the effects of screen time on health",
    "preventive healthcare measures",
    "the importance of hydration",
    "aging gracefully and healthy longevity",
    "yoga and its health benefits",
    "cardiovascular health and heart disease",
    "the gut microbiome and overall health",
    "workplace ergonomics",
    "mindfulness and meditation practices",
    "the science of weight management",
    "hearing and vision protection",
    "addiction recovery and support systems",
    "the benefits of outdoor activities",
    "regular health checkups and screenings",
    # Arts & Entertainment
    "the evolution of cinema through decades",
    "classical music composers and their works",
    "the rise of streaming platforms",
    "street art and graffiti culture",
    "the history of photography as art",
    "musical theater and Broadway productions",
    "the impact of social media on entertainment",
    "traditional pottery and ceramics",
    "the golden age of jazz",
    "contemporary sculpture techniques",
    "the psychology of humor in entertainment",
    "the film noir genre and its influence",
    "digital art and NFT marketplaces",
    "the history of comedy in media",
    "opera and classical vocal performances",
    "independent filmmaking and indie cinema",
    "the evolution of video game design",
    "dance styles from around the world",
    "the impact of music streaming on artists",
    "theater production and stagecraft",
    # Sports & Recreation
    "the history of the FIFA World Cup",
    "the science of athletic training",
    "extreme sports and adrenaline activities",
    "the Olympic Games origins and evolution",
    "team building through recreational activities",
    "the psychology of competitive sports",
    "marathon training and long-distance running",
    "water sports and their health benefits",
    "the rise of esports and competitive gaming",
    "mountaineering and rock climbing",
    "the economics of professional sports leagues",
    "cycling as a sustainable transportation mode",
    "sports nutrition and athletic performance",
    "the history of tennis championships",
    "winter sports and skiing culture",
    "youth sports development programs",
    "the mental benefits of recreational activities",
    "martial arts and self-defense training",
    "sports injuries prevention and recovery",
    "the growth of adventure tourism",
    # Travel & Geography
    "the wonders of the Great Barrier Reef",
    "backpacking through Southeast Asia",
    "the cultural diversity of Europe",
    "desert landscapes and their unique ecosystems",
    "the ancient ruins of Machu Picchu",
    "sustainable tourism practices",
    "the geography of the Amazon rainforest",
    "exploring the Northern Lights",
    "island hopping in the Pacific",
    "the history of the Silk Road routes",
    "Arctic exploration and research",
    "the architecture of European cities",
    "volcanic islands and their formation",
    "the diverse cultures of Africa",
    "cruise travel and ocean voyages",
    "the geography of mountain ranges",
    "national parks and conservation areas",
    "the trans-Siberian railway journey",
    "coastal towns of the Mediterranean",
    "the geography of natural disasters",
]


# =============================================================================
# MARKDOWN PARSING FUNCTIONS
# =============================================================================

if API_VARIANT == "ollama":
    try:
        from ollama import Client, ChatResponse
    except ImportError:
        print("Error: ollama package not installed. Run: pip install ollama")
        exit(1)
elif API_VARIANT in ["openai", "openai_compatible"]:
    try:
        from openai import OpenAI
    except ImportError:
        print("Error: openai package not installed. Run: pip install openai")
        exit(1)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
except ImportError:
    print("Error: reportlab package not installed. Run: pip install reportlab")
    exit(1)


def clean_markdown(text: str) -> str:
    """Convert markdown syntax to PDF-friendly HTML-like format."""
    # Convert bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    
    # Convert italic: *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
    
    return text


def parse_list_items(items: list, styles: dict) -> list:
    """Parse list items into PDF flowables."""
    flowables = []
    for item in items:
        flowables.append(Paragraph(f'• {item}', styles['ListItem']))
    return flowables


def parse_text_to_story(text: str, styles: dict) -> list:
    """
    Parse markdown text into a list of PDF flowables with proper formatting.
    Handles headings, bold, italic, lists, and horizontal rules.
    """
    story = []
    lines = text.split('\n')
    list_items = []

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # Handle horizontal rules (---, ***, ___)
        if re.match(r'^-{3,}$', line) or re.match(r'^\*{3,}$', line) or re.match(r'^_{3,}$', line):
            if list_items:
                story.extend(parse_list_items(list_items, styles))
                list_items = []
            story.append(Spacer(1, 0.2 * inch))
            i += 1
            continue

        # Skip code blocks markers
        if line.startswith('```'):
            i += 1
            continue

        # Handle headings (markdown # style)
        if line.startswith('### '):
            if list_items:
                story.extend(parse_list_items(list_items, styles))
                list_items = []
            content = clean_markdown(line[4:])
            story.append(Spacer(1, 0.15 * inch))
            story.append(Paragraph(content, styles['Heading3']))
            i += 1
            continue
        elif line.startswith('## '):
            if list_items:
                story.extend(parse_list_items(list_items, styles))
                list_items = []
            content = clean_markdown(line[3:])
            story.append(Spacer(1, 0.15 * inch))
            story.append(Paragraph(content, styles['Heading2']))
            i += 1
            continue
        elif line.startswith('# '):
            if list_items:
                story.extend(parse_list_items(list_items, styles))
                list_items = []
            content = clean_markdown(line[2:])
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph(content, styles['Heading1']))
            i += 1
            continue

        # Handle bullet lists
        if line.startswith(('- ', '* ', '+ ')):
            content = clean_markdown(line[2:])
            list_items.append(content)
            i += 1
            continue

        # Handle numbered lists
        match = re.match(r'^(\d+)\.\s(.+)', line)
        if match:
            content = clean_markdown(match.group(2))
            list_items.append(f"{match.group(1)}. {content}")
            i += 1
            continue

        # Handle blockquotes
        if line.startswith('> '):
            if list_items:
                story.extend(parse_list_items(list_items, styles))
                list_items = []
            content = clean_markdown(line[2:])
            story.append(Paragraph(f'"{content}"', styles['Quote']))
            i += 1
            continue

        # Regular paragraph - collect until empty line
        if line.strip():
            if list_items:
                story.extend(parse_list_items(list_items, styles))
                list_items = []
            
            # Collect multi-line paragraphs
            para_lines = [line]
            j = i + 1
            while j < len(lines) and lines[j].strip():
                para_lines.append(lines[j])
                j += 1
            
            content = ' '.join(para_lines)
            content = clean_markdown(content)
            story.append(Paragraph(content, styles['Body']))
            i = j
            continue

        # Empty line
        if list_items:
            story.extend(parse_list_items(list_items, styles))
            list_items = []
        i += 1

    # Handle any remaining list items
    if list_items:
        story.extend(parse_list_items(list_items, styles))

    return story


# =============================================================================
# FUNCTIONS
# =============================================================================

def generate_random_filename(extension: str = "pdf") -> str:
    """Generate a random filename with the given extension."""
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    return f"{random_chars}.{extension}"

def get_article_generation_prompt(topic: str = "a green apple") -> str:
    """Returns the generate article prompt."""
    # Prompt to generate 1-3 pages of content with markdown formatting
    prompt = f"""Write a comprehensive, well-structured article about {topic}. 
The article should be approximately 300-500 words (about 1-3 pages when formatted).
Include an engaging introduction, several body sections with detailed explanations, and a conclusion.
Make it informative and suitable for a general audience.

Use markdown formatting including:
- Headings (#, ##, ###) (not h4 or smaller!)
- Bold (**text** or __text__)
- Italic (*text* or _text_)
- Bullet lists (- or *)
- Numbered lists (1., 2., etc.)
- Horizontal rules (---)

Use markdown to make the article well-organized and readable.

Make sure that this is a complete and finalized article within the maximum of 3 pages! Strictly avoid comments about the generation of the article.
"""
    return prompt

def generate_text_with_openai(topic: str) -> str:
    """
    Call OpenAI API to generate text about the given topic.
    Returns approximately 1-3 pages of text (500-1000 words).
    """
    # Get API key from environment variable
    api_key = OPENAI_API_KEY
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-api-key'")
        exit(1)

    client = OpenAI(
        api_key=api_key,
        base_url=MODEL_API_BASE_URL if MODEL_API_BASE_URL else None
    )

    prompt = get_article_generation_prompt(topic=topic)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a knowledgeable writer who creates informative, well-structured articles with markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        exit(1)

def generate_text_with_ollama(topic: str) -> str:
    """
    Call Ollama API to generate text about the given topic.
    Returns approximately 1-3 pages of text (500-1000 words).
    """
    # Get API key from environment variable
    api_key = OLLAMA_API_KEY
    if not api_key:
        print("Error: OLLAMA_API_KEY environment variable not set")
        print("Please set it with: export OLLAMA_API_KEY='your-api-key'")
        exit(1)

    client = Client(
        host=MODEL_API_BASE_URL,
        headers={'Authorization': f'Bearer {api_key}'}
    )

    prompt = get_article_generation_prompt(topic=topic)

    try:
        response: ChatResponse = client.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a knowledgeable writer who creates informative, well-structured articles with markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            stream=False,
            options={
                "num_predict": 2000,
                "temperature":0.7
            }
        )
        return response.message.content or ""
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        exit(1)

def text_to_pdf(text: str, pdf_path: str) -> None:
    """
    Convert text content to a nicely formatted PDF file.
    """
    # Global variables
    global SKIPPED_FAILED_PARSING_FILES_COUNT
    global FAILED_PARSING_FILES_TO_MARKDOWN_COUNT
        
    # Create custom styles
    styles = getSampleStyleSheet()

    # Title style (H1)
    styles.add(ParagraphStyle(
        name='ArticleHeading1',
        parent=styles['Heading1'],
        fontSize=22,
        textColor='black',
        spaceAfter=24,
        spaceBefore=12,
        alignment=TA_CENTER,
        bold=True,
    ))

    # Section heading style (H2)
    styles.add(ParagraphStyle(
        name='ArticleHeading2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='black',
        spaceAfter=12,
        spaceBefore=12,
        bold=True,
    ))

    # Subsection heading style (H3)
    styles.add(ParagraphStyle(
        name='ArticleHeading3',
        parent=styles['Heading3'],
        fontSize=14,
        textColor='black',
        spaceAfter=10,
        spaceBefore=10,
        bold=True,
    ))

    # Body text style
    styles.add(ParagraphStyle(
        name='ArticleBody',
        parent=styles['Normal'],
        fontSize=12,
        textColor='black',
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=16,
    ))

    # List item style
    styles.add(ParagraphStyle(
        name='ArticleListItem',
        parent=styles['Normal'],
        fontSize=12,
        textColor='black',
        alignment=TA_LEFT,
        spaceAfter=6,
        leftIndent=20,
    ))

    # Quote style
    styles.add(ParagraphStyle(
        name='ArticleQuote',
        parent=styles['Italic'],
        fontSize=12,
        textColor='gray',
        alignment=TA_LEFT,
        spaceAfter=12,
        leftIndent=30,
        rightIndent=30,
    ))

    # Create PDF document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    # Map style names to style objects
    style_map = {
        'Heading1': styles['ArticleHeading1'],
        'Heading2': styles['ArticleHeading2'],
        'Heading3': styles['ArticleHeading3'],
        'Body': styles['ArticleBody'],
        'ListItem': styles['ArticleListItem'],
        'Quote': styles['ArticleQuote'],
    }

    # Parse text into story elements
    try:
        story = parse_text_to_story(text, style_map)
        # Build PDF
        doc.build(story)
    except Exception as e:
        if SKIP_FAILED_PARSING_FILES:
            print("Error parsing markdown. Continue to next.")
            SKIPPED_FAILED_PARSING_FILES_COUNT += 1
        else:
            print("Error parsing markdown. Writing text to md.")
            with open(pdf_path.replace(".pdf", ".md"), 'w') as file:
                file.write(text)
                FAILED_PARSING_FILES_TO_MARKDOWN_COUNT += 1

def save_metadata(pdf_filename: str, topic: str, output_dir: Path) -> None:
    """
    Save metadata (PDF filename and topic) to a JSON file.
    """
    metadata = {
        "pdf_filename": pdf_filename,
        "topic": topic,
        "model_used": MODEL_NAME,
        "generated_at": datetime.now().isoformat()
    }

    metadata_path = output_dir / "metadata.json"

    # Load existing metadata or create new list
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata_list = json.load(f)
    else:
        metadata_list = []

    # Add new metadata entry
    metadata_list.append(metadata)

    # Save updated metadata
    with open(metadata_path, 'w') as f:
        json.dump(metadata_list, f, indent=2)

    print(f"Metadata saved to: {metadata_path}")


def generate_single_article(output_dir: Path) -> None:
    """Generate a single article and save as PDF with metadata."""
    # Select a random topic
    topic = random.choice(RANDOM_TOPICS)
    print(f"Selected topic: {topic}")

    # Generate text using OpenAI API
    print(f"Generating text with Model API (model: {MODEL_NAME})...")
    start_time = time.time()
    if API_VARIANT == "ollama":
        text = generate_text_with_ollama(topic)
    elif API_VARIANT in ["openai", "openai_compatible"]:
        text = generate_text_with_openai(topic)
    else:
        raise ValueError("Invalid API variant")
    api_time = time.time() - start_time
    print(f"API call completed in {api_time:.2f} seconds")

    # Generate random filename
    filename = generate_random_filename()
    pdf_path = output_dir / filename

    # Convert text to PDF
    print("Converting to PDF...")
    pdf_start_time = time.time()
    text_to_pdf(text, str(pdf_path))
    pdf_time = time.time() - pdf_start_time
    print(f"PDF generated in {pdf_time:.2f} seconds")

    # Save metadata
    save_metadata(filename, topic, output_dir)

    total_time = api_time + pdf_time
    print(f"Done! Article about '{topic}' saved to {pdf_path}")
    print(f"Total time: {total_time:.2f} seconds\n")


def main():
    """Main and save as PDF function to generate text."""
    # Create output directory if it doesn't exist
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    print(f"Configuration:")
    print(f"  - Model: {MODEL_NAME}")
    print(f"  - Base URL: {MODEL_API_BASE_URL if MODEL_API_BASE_URL else 'default'}")
    print(f"  - Number of PDFs: {NUM_PDFS}")
    print(f"  - Output directory: {output_dir}")
    print(f"  - Number of available topics: {len(RANDOM_TOPICS)}")
    print()

    # Generate the requested number of PDFs
    main_start_time = time.time()
    for i in range(NUM_PDFS):
        print(f"--- Generating PDF {i + 1} of {NUM_PDFS} ---")
        generate_single_article(output_dir)
        time.sleep(1)

    total_time = time.time() - main_start_time
    if SKIP_FAILED_PARSING_FILES:
        print(f"{SKIPPED_FAILED_PARSING_FILES_COUNT} generated texts were skipped due to failed parsing.")
    else:
        print(f"{FAILED_PARSING_FILES_TO_MARKDOWN_COUNT} generated texts were written as markdown files due to failed parsing.")
    
    print(f"\nAll done! Generated {NUM_PDFS} PDF(s) in {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
