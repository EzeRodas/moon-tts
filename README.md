# Real time Text To Speech through the cloud

## What is Moon TTS?

This is a little project I started because I couldn't find any similar. A simple GUI to interact with Google's Cloud TTS service, and playback it's response in real time through a virtual cable or output device.

It allows for monitoring with no delay, volume control and live preview on audio lenght.

You can select any of the ***28 supported languages*** and ***8 voices*** that Google provides.

As of now I've set it up with only the Chirp3 voices, which have a ***limit of 1,000,000 characters per month on the free plan.*** On the future I'm planning to set it up so everytime the limit of a voice model is reached, it automatically downgrades tothe next voice tier to allow for more use without any charges.

This is meant to be a free thing, but I may add the option to disable the character limit in case someone wants to pay for it. It's aimed to help those who for some reason can't use their own voice and need something simple and reliable.

The usage statistics reset automatically every month.

##

### Pros:

- Low latency
- Doesn't use any pc resources

### Cons:

- Monthly character limit (1,000,000)
- Requires internet connection

##

# How to Use

>Before anything please read [Considerations](#considerations).

The program can be downloaded at the "Releases" section of this repository, after that proceed with the credentials set-up.

First you'll need a Google Cloud account. Just click on the next link and set it up with your regular Google account.

- https://console.developers.google.com/apis/dashboard

Once there search for "***Cloud Text-to-Speech API***" (Please not to be confused with Speech-To-text), and select "***Enable***".

- ### Billing:

    At this point you're going to be asked to set up a billing account for Google Cloud's services. This **DOES NOT** mean that you'll be charged for it, but it's necessary to be set up for the API'S usage. So sadly if you don't count with a credit/debit card of any kind it will not let you continue.

After that's done, head back to the Cloud Text-to-Speech API page, now you'll be able to enable it. Having done that at the left you'll see a tab that reads "***Credentials***", if it doesn't appear then look for a section called "***APIs and Services***". Once inside look for the third credentials option "***Service account***" and create a new service account.

After it's created head to keys, new key and select ***JSON*** format and doownload it.

The only thing left is to open Moon TTS, click on select credentials and point to the JSON file you just downloaded and it should be ready to use.

# Considerations

First of all, I have no idea what I'm doing and barely know how to code, this is just an amalgamation of tutorials I saw somewhere in youtube and questions I asked to Copilot, combined into a couple of weeks of banging my head against it. I just needed something for a friend of mine, but if it helps someone else then great.

I'm open to any kind of suggestion improve the program, and any feedback or idea will be greatly appreciated.

Also, <ins>very important</ins>, if you try to run the .exe file it ***WILL BE FLAGGED AS SUSPICIOUS*** by Windows. I do not have the money to spend on a license neither a company certification to sign it, so I can't do anything about it.\
If you don't trust the .exe, feel free to download the full source code that you can completely read and execute it yourself.
