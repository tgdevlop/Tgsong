import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pytube import YouTube, Search
from moviepy.editor import AudioFileClip

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your Telegram bot token
TOKEN = '7163308622:AAGSibGMbW6hl2eQVhhuJRiBXyHXsqh0vGk'

# Command to start the bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to the Song Download Bot. Send me a song name or a YouTube link to download the audio.')

# Function to download and send audio
def download_and_send_audio(update: Update, url: str):
    chat_id = update.message.chat_id
    update.message.reply_text("Downloading audio... Please wait.")
    
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_file = audio_stream.download(filename='audio.mp4')
        
        # Convert to MP3
        audio_clip = AudioFileClip(audio_file)
        audio_clip.write_audiofile('audio.mp3')
        audio_clip.close()
        
        # Send the audio file to the user
        with open('audio.mp3', 'rb') as audio:
            context.bot.send_audio(chat_id=chat_id, audio=audio)
        
        # Clean up files
        os.remove('audio.mp4')
        os.remove('audio.mp3')
        
    except Exception as e:
        logger.error(e)
        update.message.reply_text("Failed to download audio.")

# Handle incoming messages
def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    
    # Check if the message is a valid YouTube URL
    if 'youtube.com/watch?v=' in text or 'youtu.be/' in text:
        download_and_send_audio(update, text)
    else:
        # If the message is not a URL, assume it's a song name and search for it on YouTube
        try:
            search_results = Search(text).results
            if search_results:
                video_url = search_results[0].watch_url
                download_and_send_audio(update, video_url)
            else:
                update.message.reply_text("No results found for your search. Please try with a different song name.")
        except Exception as e:
            logger.error(e)
            update.message.reply_text("Failed to search for the song. Please try again later.")

def main() -> None:
    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    
    # on noncommand i.e. message - handle the message
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Start the Bot
    updater.start_polling()
    
    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
