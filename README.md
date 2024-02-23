# Generate Batch Audio
An addon that downloads and attaches audio to flashcards in bulk from URLs. Made for Anki, an SRS flashcard application. 

Written in Python, using the requests library for handling GET API calls, and PyQT for the UI elements added in Anki.

## Contents
* [Motivation](#motivation)
* [Quick Start](#quick-start)
* [Notes](#notes)
* [Usage Guide](#usage-guide)
* [Credits](#credits)
* [Screenshots](#screenshots)
* [Contributing](#contributing)

---

## Motivation
After finally getting my Japanese flashcards set up and getting many many hours into mining and repping vocab, I reached the point where I wanted to ensure that my pitch accent was on par with native speech, and the best way to do this would be to hear a native speak my vocab words many many times.

However, when I decided to make this change and add audio to all my flashcards, I quickly realized that doing this the manual way --one card at a time-- was going to take too long as I had reached over 5000 cards created already. After searching for an answer online and coming up short, I decided to create this addon so that I, and hopefully many others like me, would not have to suffer through hours of tedious work.

Hopefully you, like me and the hundreds of others who have downloaded my addon, can benefit from my work!

<div align="right">[ <a href="#contents">↑ Back to top ↑</a> ]</div>

---

## Quick Start
Anki addon page: https://ankiweb.net/shared/info/1156270186

1. [Download Anki](https://apps.ankiweb.net)
2. In Anki, go to `Tools -> Addons -> Get Addons...` and paste the code: `1156270186`
3. Restart Anki
4. Open the Anki browser and select the cards that need audio
5. Go to ```Edit``` > ```Generate Bulk Audio...```, or use the shortcut ```Ctrl+Alt+B```

<div align="right">[ <a href="#contents">↑ Back to top ↑</a> ]</div>

---

## Notes
Although this addon was initially created with Japanese cards in mind, it should also work for any other language provided that the fields and URLs are setup correctly.

This addon only works for Anki versions 2.1.45 and above.

<div align="right">[ <a href="#contents">↑ Back to top ↑</a> ]</div>

---

## Usage Guide
 - Open the Anki browser and select the cards that need audio
 - Go to ```Edit``` > ```Generate Bulk Audio...```, or use the shortcut ```Ctrl+Alt+B```
 - Sources are listed in priority order, 1 being the first source checked/used
   - If a source doesn't have the audio file, it will try the next source in priority order until all sources have been checked
 - Sources should have a name and URL
   - There should be at least one parameter in each URL
   - Parameters are just the name of a field on your card, surrounded by curly braces ```{}```
   - Parameters ignore casing, so if your field is named ```Reading```, you may use ```{reading}``` where the reading should go in the URL
 - The ```Audio field:``` selection will determine which field on the selected cards the audio will be save to
   - Any text or audio currently in that field will be replaced if successful
 - The ```Filer kana:``` selection should be used to filter out non-hiragana characters from a field before using it
   - This should be set to ```(None)``` if your cards aren't Japanese
   - An example usage might be, if you are using JPod101 audio and your ```Reading``` field looks like ```私[わたし]```, the kanji and brackets would cause the word to not be found.
Enabling Filter kana for the ```Reading``` field would instead turn it only into hiragana which would allow the word to be correctly found
 - The ```Delay between requests:``` amount is simply how long in seconds the addon should wait between download requests
   - This should be set to a higher number when using sites that use bot detection.
Otherwise, this may result in an IP ban if their system detects you as bot for downloading audio too frequently
 - The ```Duplicate to empty fields:``` checkbox should generally be enabled
   - This allows the addon to automatically use the previous parameter in the URL as the current paramter in the event that the current parameter is empty
   - This is very useful for cards that have, for example, the ```Word```/```Expression``` field in hiragana, and the ```Reading``` field has nothing.
In this case, the ```Word```/```Expression``` field would be used in place of both fields
 - The ```Dangerously fast:``` checkbox will remove a 0.1 second delay between audio downloads
   - If checked, this may results in errors, but would also be slightly faster, so please use at your own risk

<div align="right">[ <a href="#contents">↑ Back to top ↑</a> ]</div>

---

## Credits
Credit goes to the [Batch Editing addon](https://ankiweb.net/shared/info/291119185) from which I used its code as a base template. 
This was my first Anki addon, and I would have been extremely lost if there weren't such a similar addon to mine already created and open source.

Additionally, credit goes to [Yomichan](https://foosoft.net/projects/yomichan/) by FooSoft Productions from which I used their idea for comparing audio files.
This made it possible to use JPod101 audio since they return an audio file whether or not one was actually found.

Last but not least, thanks to everyone who has contributed to this project, your support is always very much appreciated, and a special thanks to the following contributors that helped get this addon off the ground:

[<img src="https://github.com/Aquafina-water-bottle.png" width="60px;"/>](https://github.com/Aquafina-water-bottle)
[<img src="https://github.com/sammy-snipes.png" width="60px;"/>](https://github.com/sammy-snipes)
[<img src="https://github.com/elizagamedev.png" width="60px;"/>](https://github.com/elizagamedev)
[<img src="https://github.com/B0sh.png" width="60px;"/>](https://github.com/B0sh)
<!--
 [<img src="https://github.com/       .png" width="60px;"/>](https://github.com/_________)
-->

<div align="right">[ <a href="#contents">↑ Back to top ↑</a> ]</div>

---

## Screenshots
![image](https://user-images.githubusercontent.com/49173127/203440799-8ed46a5c-b8c4-4618-b9a7-2a1f9e26b1cf.png)

![image](https://user-images.githubusercontent.com/49173127/203440842-a1624334-c9da-4e62-997c-4218b878c824.png)

<div align="right">[ <a href="#contents">↑ Back to top ↑</a> ]</div>

---

## Contributing
Please help support the development of this addon by:
* Checking out the list of [open issues](https://github.com/DillonWall/generate-batch-audio-anki-addon/issues?q=is%3Aissue+is%3Aopen+).
* If you need new features, please open a [new issue](https://github.com/DillonWall/generate-batch-audio-anki-addon/issues) or start a [discussion](https://github.com/DillonWall/generate-batch-audio-anki-addon/discussions).
* When creating a pull request, kindly consider the time it takes for reviewing and testing, and maintain proper coding style.
* If you wish to use this project commercially, kindly [contact me](https://github.com/DillonWall). 

Please [![Star generate-batch-audio-anki-addon](https://img.shields.io/github/stars/DillonWall/generate-batch-audio-anki-addon.svg?style=social&label=Star%20generate-batch-audio-anki-addon)](https://github.com/DillonWall/generate-batch-audio-anki-addon/) to support growth!

<div align="right">[ <a href="#contents">↑ Back to top ↑</a> ]</div>
