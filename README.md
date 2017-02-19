# flinch
Flinch.py checks a list of websites for changes. Flinch runs with Python3 and required ```ssdeep```, ```requests``` and ```BeatifulSoup4```

Run ```python3 flinch.py -h``` for help.

Example output:

```
$ python3 flinch.py -c
Flinch.py - see -h for help and command line options

1: [HTTP 200] https://github.com: How people build software · GitHub
  ➤ Content identical [100%]		[size 2660 bytes]
2: [HTTP 200] https://google.com: Google
  ➤ Content similar [90%]		[size 213984 (+47) bytes]
3: [HTTP 200] https://kirjuri.kurittu.org: Kirjuri - Digital Forensic Evidence Item Management
  ➤ Content identical [100%]		[size 7899 bytes]
4: [HTTP 200] https://kurittu.org: Kurittu.org
  ➤ Content identical [100%]		[size 208 bytes]
```
