
This is a program designed to check your workday grades for you. Only been tested using UBC. 

## Instructions

#### Download
Download the code [here](https://github.com/veen2718/workday-checker/archive/refs/heads/main.zip)

#### Setup

First, run `pip install -r requirements.txt` to install the required dependencies. 
Then, run `playwright install chromium` to install the browser
Then, run `python3 makeFiles.py`, which should create the necessary json files. 

###### Username & Password
Open the newly created `constants.json` and you should find two lines:
```
"Workday-Username":"<YOUR-USERNAME>",
"Workday-Password":"<YOUR-PASSWORD>",
```
Replace `<YOUR-USERNAME>` and `<YOUR-PASSWORD>` with your workday username and password respectively. 
It will be stored in plain-text which is not exactly secure. 

###### Notification
This uses Pushbullet to send notifications

First you need to install the Pushbullet app on your phone, and sign in. 

Then go to pushbullet.com, and sign in with the same account. 
Then, navigate to the settings tab, and then you should see an option to *Create Access Token*. 
Copy this token and in `constants.json`, copy it in as the value for:
```
"Pushbullet-API-Key":""
```

Now, you should be able to receive mobile notifications. 


#### Running it for the first time
To run the program for the first time, run `python3 main.py head`
This will run the program in a visible open window. This is important, as the first time you run, you will need to authenticate using 2FA like duo mobile. 
Once you've run it once, it will save the grade data to `gradeData.json`. Now the next time you run it, it will have data to check against. 

#### Automating
To automate this, you will need an automation that runs the python file every few minutes. The way you will do this depends on your OS. 
Unlike the last step, you do not want to automate `python3 main.py head`. Rather, you want to just automate `python3 main.py`. This way the file will run in headless mode, and will not open a visible window on your computer. 

#### Arguments
There are three different ways you could run this
```
python3 main.py head
```
As seen previously, this opens a new visible window. 

```
python3 main.py
```
As mentioned previously, this does the same thing without opening a visible window. 

```
python3 main.py last
```
This prints out the last few logs, so you can double-check when the last times the program was run. 

