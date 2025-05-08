# Real-Time Text To Speech Through the Cloud

## What is Moon TTS?

This is a small project I started because I couldn't find anything similar. It's a simple GUI for interacting with Google's Cloud TTS service and play back its responses in real time through a virtual cable or output device.

It allows for monitoring with no delay, volume control, and live preview of audio length.

You can select any of the ***28 supported languages*** and ***8 voices*** that Google provides.

Currently, I've set it up with only the Chirp3 voices, which have a ***limit of 1,000,000 characters per month on the free plan.*** In the future, I plan to configure it so that when the limit of a voice model is reached, it automatically downgrades to the next voice tier, allowing for continued use without incurring charges.

This is meant to be a free tool, but I may add the option to disable the character limit for those who want to pay for it. It's aimed at helping people who, for some reason, can't use their own voice and need something simple and reliable.

The usage statistics reset automatically every month.

##

### Pros:

- Low latency
- Doesn't use any PC resources

### Cons:

- Monthly character limit (1,000,000)
- Requires an internet connection

##

# How to Use

> Before anything, please read [Considerations](#considerations).

First, you'll need a Google Cloud account. Just click the following link and set it up with your regular Google account:

- https://console.developers.google.com/apis/dashboard

Once there, search for "***Cloud Text-to-Speech API***" (please do not confuse it with Speech-To-Text), and select "***Enable***".

<picture><source srcset="readme assets/example0.png"/><img src="readme assets/example0.png" alt="Example instructions"/></picture>

- ### Billing:

    At this point, you'll be asked to set up a billing account for Google Cloud's services. This **DOES NOT** mean that you'll be charged, but it is necessary for API usage. Unfortunately, if you don't have a credit/debit card, you won't be able to continue. (An API is like a personal key that Google provides, to know who is using its services)

    You can check the free limits for each model here:\
    https://cloud.google.com/text-to-speech/pricing

After that's done, return to the Cloud Text-to-Speech API page and enable it. Once enabled, you'll see a tab on the left labeled "***Credentials***". If it doesn't appear, look for a section called "***APIs and Services***". Inside, look for the third credentials option, "***Service account***", and create a new service account.

<picture><source srcset="readme assets/example1.png"/><img src="readme assets/example1.png" alt="Example instructions"/></picture>
<picture><source srcset="readme assets/example2.png"/><img src="readme assets/example2.png" alt="Example instructions"/></picture>

After it's created, click on your new service account, go to Keys, click New Key, select ***JSON*** format, and download it.

<picture><source srcset="readme assets/example3.png"/><img src="readme assets/example3.png" alt="Example instructions"/></picture>
<picture><source srcset="readme assets/example4.png"/><img src="readme assets/example4.png" alt="Example instructions"/></picture>
<picture><source srcset="readme assets/example5.png"/><img src="readme assets/example5.png" alt="Example instructions"/></picture>

> Bear in mind that these credentials are personal and should **NOT** be shared with anyone.

The only thing left is to open Moon TTS, click "Select Credentials," point to the JSON file you just downloaded, and it should be ready to use.

# Considerations

First of all, I have no idea what I'm doing and barely know how to code. This is just an amalgamation of tutorials I found on YouTube and questions I asked Copilot, combined with a couple of weeks of banging my head against it. I just needed something for a friend of mine, but if it helps someone else, then great.

I'm open to any suggestions to improve the program, and any feedback or ideas will be greatly appreciated.

Also, <ins>very important</ins>: if you try to run the .exe file, it ***WILL BE FLAGGED AS SUSPICIOUS*** by Windows. I do not have the money for a license or company certification to sign it, so unfortunately, I can't do anything about this.\
If you don't trust the .exe, feel free to download the full source code. You can read it completely and run it yourself.
