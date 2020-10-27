## PrEWSampleProduction

Marlin processor(s) to produce the input samples needed for a PrEW fit.

### Installation

This package needs `iLCSoft` and my own `MarlinHelp` library.

To install it first set up the environment and add the processor to the Marlin path
```shell
cd macros && source load_env.sh && source add_processors.sh && cd ..
```

Then the source code can be compiled using
```shell
cd macros && ./compile.sh && cd ..
```

### How to run the analysis

#### Examples

Examples for a single Marlin run are in `scripts/examples`, e.g.

```shell
Marlin ./scripts/examples/WWProcessorTest.xml
```

#### Production

Macros to run the production are in `macros/FullProduction`. 
They use the configuration provided in `scripts/config`.

The `run_single_process.sh` script starts the production for a single process.
```shell
./macros/FullProduction/run_single_process.sh --process=4f_WW_sl --input-config=$(pwd)/scripts/config/input_250.config --output-config=$(pwd)/scripts/config/output_250.config
```

### How to create PrEW fit input

Python code to convert the Marlin processor output into PrEW fit input is provided in the `PrEWInputProduction` directory.