<!-- 02:50 24-03-2023 -->
# CaladiumBot

This is the source code for the CaladiumBot,
it uses GPT-3.5 for generating the answers through the OpenAI API.

Run the code below, to start an instance of the server on port `3389`.
Make sure you replace the `<OPENAI_API_KEY>` with your OpenAI API key.

Due to HTTPS being mandatory in all `fetch` requests in GitHub pages,
you need a `crt.pem` and `key.pem`. Place these in this directory.

```shell
python3 -m pip install flask openai pyopenssl requests
export OPENAI_API_KEY=<OPENAI_API_KEY>
python3 __main__.py &
```
