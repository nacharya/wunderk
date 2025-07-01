# xdnext

A `golang` based REST server that uses databases like `bolt` for Users, Realms, Tasks and Apps. 

## Configuration 

If you are running the server locally in the development environment 
you may want to create a configuration in `~/.config/xdnext/config.json`

```bash
% cp ../config ~/.config/xdnext/config.json
```

Please modify the configuration file to match your environment.

## Build

```bash
% make
```

## Initialize the database in the dev environment

```bash
% make init
```

## Run a series of local tests 

```bash
% make test
```

## Reset the database and run the tests again

```bash
% make reset
```

## Run the server

```bash
% make run
```

## Run the REST call tests
Use the Container level REST call test on this locally running binary 

```bash
% cd ..
% make test
```

## Clean up

```bash
% make clean
```

