recommended: use the test exchange first.

- create a gemini api key
- clone the repo
- create a .env file in the repo with

```
PUBLIC_KEY="account-stuff"
PRIVATE_KEY="aaaaa"
```

eg buy 1 btc in usd with:

`(export $(cat .env | xargs) && python3 test btc 1 usd)`
