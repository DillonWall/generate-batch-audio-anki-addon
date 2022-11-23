# Generate Batch Audio

## Overview
An addon that generates audio in bulk from a list of URLs. Made for Anki, an SRS flashcard application.

## Usage
 - Open the Anki browser and select the cards that need audio.
 - Go to "Edit > Generate Bulk Audio...", or use the shortcut Ctrl+Alt+B
 - Sources are listed in priority order, 1 being the first source checked/used. 
   - If a source doesn't have the audio file, it will try the next source in priority order until all sources have been checked. 
 - Sources should have a name and URL.
   - There should be at least one parameter in each URL
   - Parameters are just the name of a field on your card, surrounded by curly braces {}
   - Parameters ignore casing, so if your field is named "Reading", you may use "{reading}" where the reading should go in the URL.
 - The "Audio field:" selection will determine which field on the selected cards the audio will be save to. 
   - Any text or audio currently in that field will be replaced if successful.
 - The "Filer kana:" selection should be used to filter out non-hiragana characters from a field before using it. 
   - This should be set to (None) if your cards aren't Japanese
   - An example usage might be, if you are using JPod101 audio and your "Reading" field looks like "私[わたし]", the kanji and brackets would cause the word to not be found.
Enabling Filter kana for the "Reading" field would instead turn it only into hiragana which would allow the word to be correctly found.
 - The "Delay between requests:" amount is simply how long in seconds the addon should wait between download requests. 
   - This should be set to a higher number when using sites that use bot detection.
Otherwise, this may result in an IP ban if their system detects you as bot for downloading audio too frequently.
 - The "Duplicate to empty fields:" checkbox should generally be enabled. 
   - This allows the addon to automatically use the previous parameter in the URL as the current paramter in the event that the current parameter is empty.
   - This is very useful for cards that have, for example, the "Word"/"Expression" field in hiragana, and the "Reading" field has nothing. 
In this case, the "Word"/"Expression" field would be used in place of both fields.
 - The "Dangerously fast:" checkbox will remove a 0.1 second delay between audio downloads. 
   - If checked, this may results in errors, but would also be slightly faster, so please use at your own risk.

## Notes
Although this addon was initially created with Japanese cards in mind, it should also work for any other language provided that the fields and URLs are setup correctly.

## Credits
Credit goes to the [Batch Editing addon](https://ankiweb.net/shared/info/291119185) from which I used its code as a base template. 
This was my first Anki addon, and I would have been extremely lost if there weren't such a similar addon to mine already created and open source.

Additionally, credit goes to [Yomichan](https://foosoft.net/projects/yomichan/) by FooSoft Productions from which I used their idea for comparing audio files.
This made it possible to use JPod101 audio since they return an audio file whether or not one was actually found.

## Screenshots
![image](https://user-images.githubusercontent.com/49173127/203440799-8ed46a5c-b8c4-4618-b9a7-2a1f9e26b1cf.png)

![image](https://user-images.githubusercontent.com/49173127/203440842-a1624334-c9da-4e62-997c-4218b878c824.png)
