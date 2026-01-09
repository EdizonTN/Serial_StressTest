# Serial_StressTest
Serial_StressTest is used to test serial communication between two serial ports of one computer.

<img width="1249" height="786" alt="Serial Stress Tester" src="https://github.com/user-attachments/assets/31df34ad-1211-439f-a310-bb40c872aa08" />

It allows testing when changing the transmission direction (i.e. port A transmits and port B receives and vice versa), when changing the baudrate (from the default) using a file with a data sample.

These changes can be set constant or use random changes from a set interval.

The transmission is evaluated by comparing the sent and received characters and checking the time at which the character is received.

The test can be stopped automatically in case of an error, or the progress can be saved to a log file continuously for a long time.

## Motivation
While developing a USB serial communication dual-port device, I encountered a random error during communication. To detect it, I needed to transfer data, change the transfer direction and also the transfer speed.
The most important thing was that the entire FIFO USB buffer (for a USB COM port in Win) was transferred at once, and not character by character. Only TeraTerm could do this, but it cannot compare received and sent characters. Therefore, with the help of AI, I created this python script, which helped me detect and step over (not one) error in the FW of the developed device (with an LPC5516 microcontroller from NXP).

## Features:
- automatic detection of available serial ports
- direction switching none/random/constant
- baudrate switching (600 - 921600) none/random/constant
- option to insert time gaps between characters
- option to insert time gap when switching baudrate
- option to transfer defined data block
- saving to LOG file
- option to immediately stop the test in case of error
- saving settings to json file
- test evaluation:
- by comparing the content of sent and received data
- by exceeding the timeout when receiving

## Requirements:
Since this is a python script, python is required.
You can download it here: https://www.python.org/downloads/windows/

The script will install additional modules automatically after startup.

## Usage:
After running the Serial_StressTest.py script, just load the available COM ports on the computer and select "Port A" and "Port B" from them, between which the transfer will take place.
Next, you need to select the test file that will be transferred.
And just run the test.

## Description of settings
**Load COM ports** - the script loads the available serial ports on the computer and writes them to the list for port selection.
Port A, Port B - selection from the list of available serial ports. <u>The ports must be different!</u>

**Load settings/Save settings** - the testing settings can be saved to a json file and then selected for faster application.

**Test file** - the file whose contents will be transferred during testing.

**Transfer block size in bytes (Min, Max)** - setting the range from-to for generating a random size of the transferred characters (block size).
If Min and Max are equal, this value will be used.
<u>Caution! This value will be accepted only if the number of characters (bytes) for changing direction and baudrate are set to zero.</u>

**Number of bytes for changing direction (Min, Max)** - setting the range from-to for generating a random size of transmitted characters, after which the transmission direction will be changed (From Port A to Port B and vice versa).
If Min and Max are equal, this value will be used.
If Min and Max are equal to zero, the function is deactivated (the direction does not change).

**Number of bytes for changing baudrate (Min, Max)** - setting the range from-to for generating a random size of transmitted characters, after which the transmission speed will be changed.
If Min and Max are equal, this value will be used.
If Min and Max are equal to zero, the function is deactivated (the baud rate does not change).

**Time gap between characters** - insert a time gap (delay) in milliseconds when transmitting for each byte sent. This value is taken into account when evaluating the timeout when receiving.

**Delay of transmission after baudrate change** - insert a time gap (delay) in milliseconds when changing the transmission speed (baudrate). Only after this time has elapsed, transmission continues.

**Save LOG** - if checked, the testing process will be saved to the log file.

**Select LOG file** - select the file in which the testing process will be saved.

**LOG file** - currently selected file for saving the testing process.

**Baudrate** - Selecting individual values ​​allows the use of this value when changing the baudrate. From the selected values, the next one is selected randomly during the test, only from the confirmed ones. Below each value there is also a quick statistics of transmitted and erroneous data (in [] brackets).
<u>At least one baud rate value must be selected.</u>

**Stop on error** - checking this box will pause the entire test in case of a transmission error.

**Start test** - will start transmitting the selected test file according to the settings above. The file will be sent over and over.
<u>If the test is stopped in case of an error, pressing this button







-----------------------------------------------------------------------------------------------------------------------------------
# Serial_StressTest
Serial_StressTest slúži na testovanie sériovej komunikácie medzi dvoma sériovými portami jednoho počítača.

<img width="1249" height="786" alt="Serial Stress Tester" src="https://github.com/user-attachments/assets/31df34ad-1211-439f-a310-bb40c872aa08" />


Umožňuje testovanie pri zmene smeru vysielania (t.j. port A vysiela a port B prijíma a naopak), pri zmene baudrate (z predvolených) s použitím súboru so vzorkou dát.
Tieto zmeny je možné nastaviť konštantné alebo použiť náhodné zmeny z nastaveného intervalu.

Vyhodnotenie prenosu je v porovnaní odoslaného a prijatého znaku a kontrola času v ktorom je znak prijatý.

Test je možné automaticky zastaviť v prípade chyby, alebo priebežne dlhodobo ukladať priebeh do log súboru.

## Motivácia
Pri vývoji USB komunikačného sériového dvojportového zariadenia, som narazil na náhodnú chybu, pri komunikácii. Na jej odhalenie som potreboval prenášať dáta, meniť smer prenosu a zároveň aj prenosovú rýchlosť.
Najdôležitejšie ale bolo, aby bol prenášaný naraz celý FIFO USB buffer (pri USB COM porte vo Win) anie znak po znaku. Toto dokázal len TeraTerm, ale ten zasa nevie porovnávať prijate a odoslané znaky. Preto som s pomocou AI vytvoril tento python script, ktorý mi pomohol odhali5 a odkrokova5 (nie jednu) chybu vo FW vyvájaného zariadenia (s mikrokontrolérom LPC5516 od NXP).

## Vlastnosti:
- automatická detekcia dostupných sériových portov
- prepínanie smeru žiadne/náhodné/konštantné
- prepínanie baudrate (600 - 921600) žiadne/náhodné/konštantné
- možnosť vkladať časové medzery medzi znaky
- možnosť vložiť časovú medzeru pri prepnutí baudrate
- možnosť prenášať definovaný blok dát
- ukladanie do LOG súboru
- možnosť okamžitého zastavenia testu pri chybe
- ukladanie nastavení do json súboru
- vyhodnotenie testu:
  - porovnaním obsahu vyslaných a prijatých dát
  - prekročením timoutu pri príjme

## Požiadavky:
Keďže sa jedná o python script, je potrebný python.
Stiahnete ho tu: https://www.python.org/downloads/windows/

Dodatočné moduly si script nainštaluje automaticky po spustení.

## Použitie:
Po spustení scriptu Serial_StressTest.py stačí načítať dostupné COM porty v počítači a z nich zvoliť "Port A" a "Port B", medzi ktorými bude prebiehať prenos.
Ďalej je potrebné zvoliť test súbor, ktorý bude prenášaný.
A už len spustiť test.

## Popis nastavení
**Načítať COM porty** - script načíta dostupné sériové porty v počítači a zapíše ich do zoznamu pre výber portu.
Port A, Port B - výber zo zoznamu dostupných sériových portov. <u>Porty musia byť rozdielne!</u>

**Načítať nastavenie/Uložiť nastavenie** - nastavenie testovania je možné uložiť do json súboru a následne vybrať pre rýchlejšie aplikovanie.

**Test súbor** - súbor, ktorého obsah bude prenášaný počas testovania.

**Veľkosť pren. blok v byte (Min, Max)** - nastavenie rozsahu od-do pre generovanie náhodnej veľkosti prenesených znakov (veľkosť bloku).
Ak je Min a Max rovnaké, použije sa práve táto hodnota.
<u>Pozor! Táto hodnota bude akceptovaná iba ak je počet znakov (bajtov) pre zmenu smeru a baudrate nastavená na nulu.</u>

**Počet bytov pre zmenu smeru (Min, Max)** - nastavenie rozsahu od-do pre generovanie náhodnej veľkosti prenesených znakov, po prenesení ktorých bude zmenený smer prenosu (Z Port A do Port B a naopak). 
Ak je Min a Max rovnaké, použije sa práve táto hodnota.
Ak je Min a Max rovné nule, funkcia je deaktivovaná (smer sa nemení).

**Počet bytov pre zmenu baudrate (Min, Max)** - nastavenie rozsahu od-do pre generovanie náhodnej veľkosti prenesených znakov, po prenesení ktorých bude zmenená prenosová rýchlosť. 
Ak je Min a Max rovnaké, použije sa práve táto hodnota.
Ak je Min a Max rovné nule, funkcia je deaktivovaná (Baud rate sa nemení).

**Časová medzera medzi znakmi** - vloženie časovej medzery (delay) v milisekundách pri vysielaní za každý odoslaný byte. S touto hodnotou sa počíta pri vyhodnotení timeoutu pri príjme.

**Oneskorenie vysielania po zmene baudrate** - vloženie časovej medzery (delay) v milisekundách pri zmene prenosovej rýchlosti (baudrate). Až po uplynutí tohto času, vysielanie pokračuje.

**Ukladať LOG** - ak je zaškrtnuté, priebeh testovania bude ukladaný do log súboru.

**Zvoliť LOG súbor** - voľba súboru do ktorého bude ukladaný priebeh testovania.

**LOG súbor** - aktuálne zvolený súbor prte ukladanie priebehu tyestovania.

**Baudrate** - Zvolenie jednotlivých hodnôt povolí použitie tejto hodnoty pri zmene baudrate. Zo zvolených hodnôt je pri teste nasledujúca zvolená náhodne práve len z potvrdených. Pod každou hodnotou je aj rýchla štatistika prenesených a chybných dát (v [] zátvorkách).
<u>Musí byť zvolená minimálne jedna hodnota prenosovej rýchlosti.</u>

**Zastaviť pri chybe** - označením tohto políčka bude v prípade chyby pri prenose celé testovanie pozastavené.

**Spustiť test** - spustí prenášanie zvoleného testovacieho súboru podľa nastavení vyššie. Súbor bude posielaný stále dokola. 
<u>V prípade zastavenia testu pri chybe, stlačenie tohto tlačítka povolí ďalšie pokračovanbie prenosu ďalej.</u>

**Zastaviť test** - ukončí prenos a celé testovanie.

**Clear** - zmaže okno so správami o priebehu testovania a všetky štatistiky.



## Štatistika
je zobrazená v spodnej časti okna. Priebežne sa počas behu tesovania aktualizuje (cca po pol sekunde).

**Cycle** - počítadlo cyklov odoslania testovacieho súboru. Cyklus je zvýšený po kompletom odoslaní testovacieho súboru.

**Errors** - počítadlo chýb (pre všetky prenosopvé rýchlosti)

**Block Size** - aktuálna veľkosť prenášaného bloku. Pri náhodnom generovaní veľkosti blokov sa zobrazuje vždy posledná hodnota.

**Baudrate** - aktuálna prenosová rýchlosť.

**TxCharTime** - prepočítaný čas na základe aktuálnej prenosovej rýchlosti s pripočítaním časovej medzeri medzi znakmi (rozhodovacia timeout hodnota). 
<u>Pozor! Počítaná je pre 8 bytový prenos bez parity s jedným stop bitom.</u>

**TxChar_Delay** - Časová medzera medzi vysielanými znakmi v milisekundách.

**RxBlockTimeout** - prepočítaný timeout na aktuálnu veľkosť bloku.



## Upozornenie
Nie som python programátor, preto je štruktúra scriptu amatérska a škaredá - kostru mi pomohla vytvoriť AI. Nie je dokončený preklad a niektoré texty by mohli byť zrozumiteľnejšie, alebo iné.
Ničmenej, script mi pomohol a preto je tu. Možno pomôže ďalším.
Ak chcete, upravte ho prepíšte ho, doplňte ho....

