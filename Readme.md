# PrEWSampleProduction

Marlin processor(s) to produce the input samples needed for a PrEW fit.

## Installation

This package needs `iLCSoft`, `WHIZARD` and my own `MarlinHelp` library.

To install it first set up the environment and add the processor to the Marlin path
```shell
cd macros && source load_env.sh && source add_processors.sh && cd ..
```

Then the source code can be compiled using
```shell
cd macros && ./compile.sh && cd ..
```

## How to run the analysis

### Event rescanning with WHIZARD

Macros to rescan all files of a process for different TGC values are in `macros/WhizardRescan`.
They need configuration files such as those provided in `scripts/config`, and the rescan template provided in `scripts/templates`.

The `rescan_single_process.sh` scripts starts the full rescan for a single process, e.g.:
```shell
chmod u+x ./macros/*/*.sh 
./macros/WhizardRescan/rescan_single_process.sh --process=4f_WW_sl --input-config=$(pwd)/scripts/config/input_250.config --output-config=$(pwd)/scripts/config/output_250.config --tgc-config=$(pwd)/scripts/tgc.config --tgc-points-file=$(pwd)/scripts/config/tgc_dev_points_g1z_ka_la.config
```
The file given for `--tgc-points-file` contains the points to rescan (each line being `g1z kappa_gamma lambda_gamma` - separated by a whitespace), and the file given for `--tgc.config` sets the scale for those points.

An additional `--failed-only` flag can be provided to the script to rerun those rescans that previously failed to produce a weight file.


### Observable extraction with Marlin

#### Examples

Examples for a single Marlin run are in `scripts/examples`, e.g.

```shell
Marlin ./scripts/examples/WWProcessorTest.xml
```

#### Full production

Macros to run the production are in `macros/FullProduction`. 
They use the configuration provided in `scripts/config`.

The `run_single_process.sh` script starts the production for a single process.
```shell
chmod u+x ./macros/*/*.sh 
./macros/FullProduction/run_single_process.sh --process=4f_WW_sl --input-config=$(pwd)/scripts/config/input_250.config --output-config=$(pwd)/scripts/config/output_250.config
```

Available processes are:

Input name | Common name | Final state
---|---|---
2f_Z_l  | Di-lepton production | mu mubar / tau taubar 
2f_Z_h  | Di-quark production | qq
4f_WW_sl  | Semileptonic W pair production | qq mu/tau nu 
4f_sW_sl  | Semileptonic single-W production  | qq e nu

## How to create PrEW fit input

Python code to convert the Marlin processor output into PrEW fit input is provided in the `PrEWInputProduction` directory.