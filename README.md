# MEV-Boost allowed relays list

MEV-Boost allowed relays list is a simple contract storing a list of relays that have been approved by DAO for use in [MEV-Boost](https://github.com/flashbots/mev-boost). The data from the contract are used to generate a configuration file that contains a list of relays that should be connected to.

## Install dependencies

```shell
npm i
```

## Run tests

```shell
npm run test
```

## Local deploy

Step 1. Compile artifacts

```shell
npm run compile
```

Step 2. Run the local node

```shell
npm run node
```

Step 3. Run the deploy script

```shell
npm run deploy localhost
```

## Network deploy

Step 1. Compile artifacts

```shell
npm run compile
```

Step 2. Copy the contents of `sample.env` to `.env`

```shell
cp sample.env .env
```

Step 3. Fill out the `.env` file

Step 4. Run the deploy script

```shell
npm run deploy goerli
```
