## PrEWSampleProduction

Marlin processor(s) to produce the input samples needed for a PrEW fit.

### Installation

This package needs `iLCSoft` and my own `MarlinHelp` library.

To intall it first set up the environment and add the processor to the Marlin path
```shell
cd macros && source load_env.sh && source add_processors.sh && cd ..
```

Then the source code can be compiled using
```shell
cd macros && ./compile.sh && cd ..
```

### How to run the analysis

Run the WW example using:

```shell
Marlin ./scripts/WWProcessorTest.xml
```