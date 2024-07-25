const TelegramBot = require('node-telegram-bot-api');
const ytdl = require('ytdl-core');
const ffmpeg = require('fluent-ffmpeg');
const fs = require('fs');
const path = require('path');
const youtubeSearch = require('youtube-search-api');

const token = '7163308622:AAGSibGMbW6hl2eQVhhuJRiBXyHXsqh0vGk';
const bot = new TelegramBot(token, { polling: true });

bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, "Welcome to the Song Download Bot. Send me a song name or a YouTube link to download the audio.");
});

bot.on('message', async (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text;

    if (text.startsWith('http')) {
        downloadAndSendAudio(chatId, text);
    } else {
        const searchResults = await youtubeSearch.GetListByKeyword(text, false);
        if (searchResults.items.length > 0) {
            const videoUrl = `https://www.youtube.com/watch?v=${searchResults.items[0].id}`;
            downloadAndSendAudio(chatId, videoUrl);
        } else {
            bot.sendMessage(chatId, "No results found for your search. Please try with a different song name.");
        }
    }
});

function downloadAndSendAudio(chatId, url) {
    bot.sendMessage(chatId, "Downloading audio... Please wait.");

    const audioStream = ytdl(url, { filter: 'audioonly' });
    const audioFile = path.resolve(__dirname, 'audio.mp3');

    ffmpeg(audioStream)
        .audioBitrate(128)
        .save(audioFile)
        .on('end', () => {
            bot.sendAudio(chatId, audioFile).then(() => {
                fs.unlinkSync(audioFile);
            });
        })
        .on('error', (error) => {
            console.error(error);
            bot.sendMessage(chatId, "Failed to download audio.");
        });
}
