<!-- 21:12 23-03-2023 -->
# Server

You can find instructions to set up the server in the root [README](/README.md).

## Testing

You can find a suite of tests in the `tests` directory.
In-order to run tests you must have the `CALADIUM_SERVER_ADDRESS`
environmental variable set with the address of a caladium server instance.

Run these commands to execute the tests (`python3` if on Linux or macOS).

```shell
cd tests
python -m unittest
```
