# irc chatbot
This is an irc chatbot for csc482:Natural Language processing. Tested on unix3.csc.calpoly.edu.

## setup
run `bash setup.sh` to set up the venv. then make a new file `creds` that contains:

```
export API_KEY=<YOUR_API_KEY>
export BOT_PASS=<YOUR_BOT_PASS>
```

## use
`source venv/bin/activate` then `source creds`.

then run `python2 irc.py`