# k4_urlv4_final_fixed

## Description:
This tool performs URL guessing using a base URL with a placeholder and a wordlist. It uses real HTTP requests to test which guessed URLs return HTTP 200.

## How to Run:
1. Make sure you have Python installed.
2. Install Flask and requests if you haven't:

```bash
pip install flask requests
```

3. Run the app:

```bash
python k4_urlv4_final_fixed.py
```

4. Open your browser and go to:

```
http://127.0.0.1:5000
```

5. Enter base URLs (with {{var1}} as placeholder), wordlist, and start the guessing.
